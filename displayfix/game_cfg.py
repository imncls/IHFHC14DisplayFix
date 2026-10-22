"""Display settings in Documents\\neutron games\\HandballChallenge14\\game.cfg.

That folder is created by the game on its first run.

Only the three tags this tool sets are touched; the rest of the file stays as
the game wrote it.
"""

import os
import re
import shutil
from dataclasses import dataclass
from pathlib import Path

from displayfix import FixError
from displayfix.windows import documents_dir

ENCODING = "iso-8859-15"
CFG_SUBPATH = Path("neutron games") / "HandballChallenge14" / "game.cfg"
BACKUP_SUFFIX = ".displayfix.bak"
TAGS = ("Resolution", "Fullscreen", "RefreshRate")


@dataclass(frozen=True)
class Values:
    resolution: int
    fullscreen: int
    refresh: int


def cfg_path() -> Path:
    return documents_dir() / CFG_SUBPATH


def backup_path(cfg: Path) -> Path:
    return cfg.with_name(cfg.name + BACKUP_SUFFIX)


def _pattern(tag: str) -> re.Pattern[str]:
    return re.compile(rf"(<{tag}>)\s*(\d+)\s*(</{tag}>)")


def read_values(text: str) -> Values:
    found = {}
    for tag in TAGS:
        matches = _pattern(tag).findall(text)
        if len(matches) != 1:
            raise FixError(
                f"game.cfg has no single <{tag}> setting; it was not changed."
            )
        found[tag] = int(matches[0][1])
    return Values(found["Resolution"], found["Fullscreen"], found["RefreshRate"])


def with_values(text: str, values: Values) -> str:
    read_values(text)  # each tag exactly once
    new = {
        "Resolution": values.resolution,
        "Fullscreen": values.fullscreen,
        "RefreshRate": values.refresh,
    }
    for tag in TAGS:
        text = _pattern(tag).sub(rf"\g<1>{new[tag]}\g<3>", text)
    return text


def read(cfg: Path) -> str:
    if not cfg.is_file():
        raise FixError(
            f"{cfg} was not found. Start the game once, close it, "
            "and run this tool again."
        )
    with cfg.open(encoding=ENCODING, newline="") as file:
        return file.read()


def write(cfg: Path, values: Values) -> Path:
    """Write the values; the first time, keep a copy of the original. Returns
    the backup's path."""
    text = with_values(read(cfg), values)
    backup = backup_path(cfg)
    if not backup.exists():
        shutil.copy2(cfg, backup)
    _write_atomic(cfg, text)
    return backup


def restore(cfg: Path) -> None:
    backup = backup_path(cfg)
    if not backup.is_file():
        raise FixError(f"There is no backup to restore ({backup.name} not found).")
    shutil.copyfile(backup, cfg)


def _write_atomic(cfg: Path, text: str) -> None:
    temporary = cfg.with_name(cfg.name + ".tmp")
    try:
        with temporary.open("w", encoding=ENCODING, newline="") as file:
            file.write(text)
        os.replace(temporary, cfg)
    finally:
        temporary.unlink(missing_ok=True)
