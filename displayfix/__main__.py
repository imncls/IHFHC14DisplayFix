"""HC14 Display Fix: fullscreen at the main monitor's resolution.

HC14DisplayFix.exe            show the change and ask before writing
HC14DisplayFix.exe --yes      write without asking
HC14DisplayFix.exe --restore  put back the game.cfg it found the first time
"""

import argparse
import ctypes
import sys
from pathlib import Path

from displayfix import FixError, __version__, game_cfg, modes
from displayfix.game_cfg import Values
from displayfix.windows import game_running

PER_MONITOR_AWARE = 2
NOTE = (
    "The game always uses the main monitor (Windows Settings > Display). To play "
    "on another monitor, make it the main one and run this tool again."
)


def describe(values: Values, sizes: list[tuple[int, int]]) -> str:
    size = (
        "{}x{}".format(*sizes[values.resolution])
        if 0 <= values.resolution < len(sizes)
        else "unknown size"
    )
    return (
        f"Resolution {values.resolution} ({size}), "
        f"Fullscreen {values.fullscreen}, RefreshRate {values.refresh}"
    )


def answer(prompt: str) -> str:
    """What the user typed; empty when there is no console input."""
    try:
        return input(prompt).strip().lower()
    except EOFError:
        return ""


def fix(cfg: Path, ask: bool) -> int:
    current = game_cfg.read_values(game_cfg.read(cfg))
    mode = modes.current_mode()
    sizes = modes.game_sizes(modes.direct3d_modes())
    wanted = Values(
        modes.resolution_index(sizes, mode.width, mode.height), 1, mode.refresh
    )
    print(f"Main monitor: {mode.width}x{mode.height} at {mode.refresh} Hz")
    print(f"Settings file: {cfg}")
    print(f"  now:  {describe(current, sizes)}")
    if current == wanted:
        print(
            "The game is already set to fullscreen at this resolution. Nothing to do."
        )
        return 0
    print(f"  new:  {describe(wanted, sizes)}")
    if ask and answer("Apply? [y/N] ") not in ("y", "yes"):
        print("Nothing was changed.")
        return 0
    backup = game_cfg.write(cfg, wanted)
    print(f"Done. The original settings are kept in {backup.name};")
    print("--restore puts them back.")
    print(NOTE)
    return 0


def run(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="HC14DisplayFix",
        description="Sets IHF Handball Challenge 14 to fullscreen at the main "
        "monitor's resolution (unofficial).",
    )
    parser.add_argument("--yes", action="store_true", help="write without asking")
    parser.add_argument(
        "--restore", action="store_true", help="put back the original game.cfg"
    )
    parser.add_argument("--cfg", type=Path, help="another game.cfg (for testing)")
    parser.add_argument("--version", action="version", version=__version__)
    args = parser.parse_args(argv)

    print(f"HC14 Display Fix {__version__} (unofficial)\n")
    try:
        if game_running():
            raise FixError("The game is running. Close it and run this tool again.")
        cfg = args.cfg or game_cfg.cfg_path()
        if args.restore:
            game_cfg.restore(cfg)
            print(f"The original settings were put back in {cfg}.")
            return 0
        return fix(cfg, ask=not args.yes)
    except FixError as error:
        print(f"Error: {error}")
        return 1


def main() -> None:
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(PER_MONITOR_AWARE)
    except (AttributeError, OSError):
        pass
    code = run()
    if getattr(sys, "frozen", False):  # a double-clicked .exe: keep the window open
        answer("\nPress Enter to close.")
    sys.exit(code)


if __name__ == "__main__":
    main()
