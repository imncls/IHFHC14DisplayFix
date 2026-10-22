from pathlib import Path

import pytest
from conftest import SAMPLE_CFG
from test_modes import LAPTOP

from displayfix import __main__ as program
from displayfix import game_cfg, modes
from displayfix.game_cfg import Values
from displayfix.modes import Mode


@pytest.fixture(autouse=True)
def laptop(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(program, "game_running", lambda: False)
    monkeypatch.setattr(modes, "current_mode", lambda: Mode(1920, 1080, 144))
    monkeypatch.setattr(modes, "direct3d_modes", lambda: LAPTOP)


def values(cfg: Path) -> Values:
    return game_cfg.read_values(game_cfg.read(cfg))


def test_yes_writes(cfg: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert program.run(["--cfg", str(cfg), "--yes"]) == 0
    assert values(cfg) == Values(15, 1, 144)
    out = capsys.readouterr().out
    assert "now:  Resolution 3 (1280x600), Fullscreen 0, RefreshRate 0" in out
    assert "new:  Resolution 15 (1920x1080), Fullscreen 1, RefreshRate 144" in out


@pytest.mark.parametrize(
    ("answer", "written"), [("y", True), ("", False), ("no", False)]
)
def test_asks_first(
    cfg: Path, monkeypatch: pytest.MonkeyPatch, answer: str, written: bool
) -> None:
    monkeypatch.setattr("builtins.input", lambda _prompt: answer)
    assert program.run(["--cfg", str(cfg)]) == 0
    assert (values(cfg) == Values(15, 1, 144)) is written
    assert game_cfg.backup_path(cfg).exists() is written


def test_no_console_input_means_no(cfg: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    def closed(_prompt: str) -> str:
        raise EOFError

    monkeypatch.setattr("builtins.input", closed)
    assert program.run(["--cfg", str(cfg)]) == 0
    assert values(cfg) == Values(3, 0, 0)


def test_nothing_to_do(cfg: Path, capsys: pytest.CaptureFixture[str]) -> None:
    program.run(["--cfg", str(cfg), "--yes"])
    program.run(["--cfg", str(cfg), "--yes"])
    assert "Nothing to do" in capsys.readouterr().out


def test_restore(cfg: Path) -> None:
    program.run(["--cfg", str(cfg), "--yes"])
    assert program.run(["--cfg", str(cfg), "--restore"]) == 0
    assert cfg.read_bytes() == SAMPLE_CFG.encode("iso-8859-15")


def test_refuses_while_the_game_runs(
    cfg: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(program, "game_running", lambda: True)
    assert program.run(["--cfg", str(cfg), "--yes"]) == 1
    assert "Close it" in capsys.readouterr().out
    assert values(cfg) == Values(3, 0, 0)


def test_missing_cfg(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert program.run(["--cfg", str(tmp_path / "game.cfg"), "--yes"]) == 1
    assert "Start the game once" in capsys.readouterr().out


def test_screen_size_not_offered(
    cfg: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(modes, "current_mode", lambda: Mode(2560, 1440, 165))
    assert program.run(["--cfg", str(cfg), "--yes"]) == 1
    assert "2560x1440" in capsys.readouterr().out
    assert values(cfg) == Values(3, 0, 0)
