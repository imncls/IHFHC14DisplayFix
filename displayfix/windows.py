"""The few Windows facts the tool needs: Documents folder, is the game running."""

import ctypes
import os
import subprocess
from pathlib import Path

GAME_EXE = "HC14.exe"
# FOLDERID_Documents
_DOCUMENTS_FOLDER = "{FDD39AD0-238F-46AF-ADB4-6C85480369C7}"


class _Guid(ctypes.Structure):
    _fields_ = [
        ("data1", ctypes.c_uint32),
        ("data2", ctypes.c_uint16),
        ("data3", ctypes.c_uint16),
        ("data4", ctypes.c_ubyte * 8),
    ]

    def __init__(self, text: str) -> None:
        parts = text.strip("{}").split("-")
        tail = bytes.fromhex(parts[3] + parts[4])
        super().__init__(
            int(parts[0], 16),
            int(parts[1], 16),
            int(parts[2], 16),
            (ctypes.c_ubyte * 8)(*tail),
        )


def documents_dir() -> Path:
    """The user's Documents folder, also when it is redirected (OneDrive)."""
    path = ctypes.c_wchar_p()
    try:
        folder = _Guid(_DOCUMENTS_FOLDER)
        shell32 = ctypes.windll.shell32
        shell32.SHGetKnownFolderPath.argtypes = [
            ctypes.POINTER(_Guid),
            ctypes.c_uint32,
            ctypes.c_void_p,
            ctypes.POINTER(ctypes.c_wchar_p),
        ]
        shell32.SHGetKnownFolderPath.restype = ctypes.c_long
        if shell32.SHGetKnownFolderPath(
            ctypes.byref(folder), 0, None, ctypes.byref(path)
        ):
            return Path.home() / "Documents"
        return Path(path.value)
    except (AttributeError, OSError):
        return Path.home() / "Documents"
    finally:
        if path.value is not None:
            ctypes.windll.ole32.CoTaskMemFree(path)


def game_running() -> bool:
    tasklist = (
        Path(os.environ.get("SystemRoot", r"C:\Windows")) / "System32" / "tasklist.exe"
    )
    result = subprocess.run(  # noqa: S603 - fixed executable and arguments
        [str(tasklist), "/FI", f"IMAGENAME eq {GAME_EXE}", "/FO", "CSV", "/NH"],
        capture_output=True,
        text=True,
        errors="replace",
        check=True,
    )
    return f'"{GAME_EXE.lower()}"' in result.stdout.lower()
