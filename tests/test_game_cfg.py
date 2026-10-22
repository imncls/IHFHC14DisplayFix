from pathlib import Path

import pytest
from conftest import SAMPLE_CFG

from displayfix import FixError, game_cfg
from displayfix.game_cfg import Values

WANTED = Values(15, 1, 144)


def test_read_values() -> None:
    assert game_cfg.read_values(SAMPLE_CFG) == Values(3, 0, 0)


def test_only_the_three_values_change() -> None:
    text = game_cfg.with_values(SAMPLE_CFG, WANTED)
    expected = (
        SAMPLE_CFG.replace("<Resolution>3<", "<Resolution>15<")
        .replace("<Fullscreen>0<", "<Fullscreen>1<")
        .replace("<RefreshRate>0<", "<RefreshRate>144<")
    )
    assert text == expected


@pytest.mark.parametrize(
    "text",
    [
        SAMPLE_CFG.replace("<RefreshRate>0</RefreshRate>", ""),
        SAMPLE_CFG.replace("<HDR>1</HDR>", "<Fullscreen>1</Fullscreen>"),
        "not a settings file",
    ],
    ids=["missing", "twice", "garbage"],
)
def test_unexpected_files_are_refused(text: str) -> None:
    with pytest.raises(FixError, match="was not changed"):
        game_cfg.with_values(text, WANTED)


def test_write_keeps_the_first_original(cfg: Path) -> None:
    backup = game_cfg.write(cfg, WANTED)
    assert backup.read_bytes() == SAMPLE_CFG.encode("iso-8859-15")
    assert game_cfg.read_values(game_cfg.read(cfg)) == WANTED
    game_cfg.write(cfg, Values(14, 1, 60))  # a second run keeps the first backup
    assert backup.read_bytes() == SAMPLE_CFG.encode("iso-8859-15")
    assert not cfg.with_name("game.cfg.tmp").exists()


def test_line_endings_and_encoding_stay(cfg: Path) -> None:
    game_cfg.write(cfg, WANTED)
    assert cfg.read_bytes().count(b"\r\n") == SAMPLE_CFG.count("\r\n")


def test_restore(cfg: Path) -> None:
    game_cfg.write(cfg, WANTED)
    game_cfg.restore(cfg)
    assert cfg.read_bytes() == SAMPLE_CFG.encode("iso-8859-15")


def test_restore_without_backup(cfg: Path) -> None:
    with pytest.raises(FixError, match="no backup"):
        game_cfg.restore(cfg)


def test_missing_file(tmp_path: Path) -> None:
    with pytest.raises(FixError, match="Start the game once"):
        game_cfg.read(tmp_path / "game.cfg")


def test_refused_file_is_not_touched(tmp_path: Path) -> None:
    cfg = tmp_path / "game.cfg"
    cfg.write_text("not a settings file", encoding="iso-8859-15")
    with pytest.raises(FixError):
        game_cfg.write(cfg, WANTED)
    assert cfg.read_text(encoding="iso-8859-15") == "not a settings file"
    assert not game_cfg.backup_path(cfg).exists()
