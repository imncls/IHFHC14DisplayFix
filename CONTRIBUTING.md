# Contributing

## Setup
Windows with Python 3.12 or later (32 or 64-bit). Only the standard library is used at run time.

```
python -m venv .venv
.venv\Scripts\activate
pip install -e .[dev]
```

## Run and test
```
python -m displayfix --help
python -m displayfix --cfg path\to\a\copy\of\game.cfg
python -m pytest
python -m ruff check .
python -m ruff format --check .
```

`--cfg` works on another file, so you can try changes on a copy instead of the game's real settings. The tests never touch the real file or need the game: they use a sample settings file and a fixed list of display modes.

## Structure
```
displayfix/
  __init__.py   version and FixError (a message for the user, no traceback)
  __main__.py   the console program: arguments, what it prints, the question
  modes.py      the main monitor's mode and the game's numbered list of resolutions (Direct3D 9)
  game_cfg.py   reading and rewriting the three settings in game.cfg, backup and restore
  windows.py    the Documents folder (also when redirected to OneDrive) and whether the game is running
```

How the game reads its settings (measured on Windows 11 with the Steam version):
- `game.cfg` is XML in iso-8859-15. `Resolution` is an index into the sizes Direct3D 9 lists for adapter 0 (the main monitor) in `X8R8G8B8`, each size once, smallest first, from 800 pixels wide. `RefreshRate` 0 makes fullscreen fail, and the game falls back to a 1024x768 window.
- `HC14.exe` has no DPI awareness in its manifest, so Windows scales its windows with the display scale. Fullscreen is not affected.

## Release build
```
python -m PyInstaller --noconfirm --clean --onefile --console --name HC14DisplayFix --specpath build --paths . --version-file ../packaging/version_info.txt displayfix/__main__.py
```

This writes `dist/HC14DisplayFix.exe`; publish it in the GitHub release as `HC14DisplayFix-<version>.exe`, with its SHA-256 in the release notes and in a `SHA256SUMS.txt` asset (`certutil -hashfile HC14DisplayFix-<version>.exe SHA256`, written as `<hash>  HC14DisplayFix-<version>.exe`). The version is in `displayfix/__init__.py`, `pyproject.toml` and `packaging/version_info.txt` (the Windows properties of the `.exe`); a test checks they match. The `--version-file` path is relative to `build/`, where PyInstaller writes its spec.
