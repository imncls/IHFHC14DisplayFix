# CLAUDE.md

## What this is
A Windows-only console tool (Python ≥3.12, standard library only at run time) that edits the display settings of the game IHF Handball Challenge 14 in `Documents\neutron games\HandballChallenge14\game.cfg` so it starts fullscreen at the main monitor's resolution. It is shipped as a single PyInstaller `.exe`. User-facing behaviour and the manual fix are documented in README.md; developer notes are in CONTRIBUTING.md.

## Commands
```
pip install -e .[dev]                         # pytest, ruff, pyinstaller
python -m pytest                              # all tests
python -m pytest tests/test_main.py::test_restore   # one test
python -m ruff check .
python -m ruff format --check .
python -m displayfix --cfg path\to\copy\of\game.cfg  # try it on a copy, never the real file
```

Release build (writes `dist/HC14DisplayFix.exe`; the `--version-file` path is relative to `build/`, where the spec goes):
```
python -m PyInstaller --noconfirm --clean --onefile --console --name HC14DisplayFix --specpath build --paths . --version-file ../packaging/version_info.txt displayfix/__main__.py
```

## Working rules
- Prefer small, focused changes; do not modify unrelated code or add features that were not requested.
- No run-time dependencies beyond the standard library (Win32/Direct3D access goes through `ctypes`). Dev tools go in the `dev` extra.
- Match the existing style: short modules, plain functions and frozen dataclasses, meaningful names. Comments only for non-obvious decisions (e.g. measured game behaviour, vtable slots).
- Handle errors explicitly. Anything the user should see is raised as `FixError` with a short, plain message for non-technical players; never let a raw exception or traceback reach the console, and never swallow errors silently (the narrow `except (AttributeError, OSError)` fallbacks are deliberate).

## Security
- Treat `game.cfg` as untrusted input: it may be missing, malformed, hand-edited or in an unexpected encoding. Validate it fully (`read_values`: each of the three tags exactly once, integer value) **before** writing anything; on any doubt, raise `FixError` and leave the file unchanged.
- Touch only the user's `game.cfg`, its `.displayfix.bak` and the temporary `.tmp` next to it. No game files, registry, Windows settings or network access.
- Never overwrite the original backup, and keep writes atomic so an interruption cannot leave a half-written `game.cfg`.
- External processes: absolute executable path, fixed argument list, no `shell=True` (see `game_running`).
- Ruff's `S` (bandit) rules stay on. A `# noqa` needs a specific code and a reason, as in `windows.py`.
- Security-relevant changes (parsing, writing, backup/restore) need tests.

## Architecture
Flow in `displayfix/__main__.py` (`run` → `fix`): refuse if `HC14.exe` is running → read the three current values from game.cfg → get the main monitor's current mode (`EnumDisplaySettingsW`) → enumerate Direct3D 9 modes and build the game's size list → compute the target `Values(resolution_index, 1, refresh)` → show now/new, ask, write.

- `modes.py` talks to Win32 and Direct3D 9 purely through `ctypes`, including calling `IDirect3D9` methods by vtable slot (2 Release, 6 GetAdapterModeCount, 7 EnumAdapterModes). `game_sizes` must reproduce the game's own list exactly: adapter 0, `D3DFMT_X8R8G8B8`, unique (w, h), width ≥ 800, sorted ascending. `Resolution` in game.cfg is an index into that list. Refresh 0/1 is replaced by 60 because `RefreshRate` 0 breaks the game's fullscreen.
- `game_cfg.py` deliberately does **not** parse XML: it regex-replaces only `<Resolution>`, `<Fullscreen>`, `<RefreshRate>` and leaves the rest byte-for-byte (encoding `iso-8859-15`, `newline=""` to keep CRLF). Writes go to `.tmp` + `os.replace`; the first write copies the original to `game.cfg.displayfix.bak`, which `--restore` puts back.
- `windows.py`: Documents folder via `SHGetKnownFolderPath` (handles OneDrive redirection, falls back to `~/Documents`) and the running-game check via `tasklist.exe`.
- `main()` sets per-monitor DPI awareness before anything else so the mode is read in real pixels, and when frozen (`.exe`) waits for Enter so a double-clicked window stays open.

## Tests
Tests never touch the real game.cfg or need the game or real hardware. `tests/conftest.py` provides a sample CRLF `game.cfg` in `tmp_path`; `test_main.py` monkeypatches `modes.current_mode`, `modes.direct3d_modes` (with the fixed `LAPTOP` mode list from `test_modes.py`) and `program.game_running`. Because of that, `__main__.py` must keep calling `modes.current_mode()` / `modes.direct3d_modes()` through the module rather than importing them by name. Tests import sibling modules directly (`from conftest import ...`, `from test_modes import ...`).

## Versioning
The version lives in three places that must match (enforced by `tests/test_version.py`): `displayfix/__init__.py`, `pyproject.toml`, and `packaging/version_info.txt` (`filevers`/`prodvers` tuples and `FileVersion`/`ProductVersion` strings).
