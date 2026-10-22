"""The main monitor's mode and the list of sizes the game numbers.

The game asks Direct3D 9 for the modes of adapter 0 (the main monitor) and
stores the chosen size as a position in its own list: every size once,
smallest first, from 800 pixels wide. RefreshRate 0 makes its fullscreen fail.
"""

import ctypes
from ctypes import wintypes
from dataclasses import dataclass

from displayfix import FixError

MIN_WIDTH = 800
DEFAULT_REFRESH = 60
ENUM_CURRENT_SETTINGS = -1
D3D_SDK_VERSION = 32
D3DFMT_X8R8G8B8 = 22


@dataclass(frozen=True)
class Mode:
    width: int
    height: int
    refresh: int


class _DEVMODEW(ctypes.Structure):
    _fields_ = [
        ("dmDeviceName", wintypes.WCHAR * 32),
        ("dmSpecVersion", wintypes.WORD),
        ("dmDriverVersion", wintypes.WORD),
        ("dmSize", wintypes.WORD),
        ("dmDriverExtra", wintypes.WORD),
        ("dmFields", wintypes.DWORD),
        ("dmPositionX", wintypes.LONG),
        ("dmPositionY", wintypes.LONG),
        ("dmDisplayOrientation", wintypes.DWORD),
        ("dmDisplayFixedOutput", wintypes.DWORD),
        ("dmColor", ctypes.c_short),
        ("dmDuplex", ctypes.c_short),
        ("dmYResolution", ctypes.c_short),
        ("dmTTOption", ctypes.c_short),
        ("dmCollate", ctypes.c_short),
        ("dmFormName", wintypes.WCHAR * 32),
        ("dmLogPixels", wintypes.WORD),
        ("dmBitsPerPel", wintypes.DWORD),
        ("dmPelsWidth", wintypes.DWORD),
        ("dmPelsHeight", wintypes.DWORD),
        ("dmDisplayFlags", wintypes.DWORD),
        ("dmDisplayFrequency", wintypes.DWORD),
        ("dmICMMethod", wintypes.DWORD),
        ("dmICMIntent", wintypes.DWORD),
        ("dmMediaType", wintypes.DWORD),
        ("dmDitherType", wintypes.DWORD),
        ("dmReserved1", wintypes.DWORD),
        ("dmReserved2", wintypes.DWORD),
        ("dmPanningWidth", wintypes.DWORD),
        ("dmPanningHeight", wintypes.DWORD),
    ]


class _D3DDISPLAYMODE(ctypes.Structure):
    _fields_ = [
        ("Width", ctypes.c_uint),
        ("Height", ctypes.c_uint),
        ("RefreshRate", ctypes.c_uint),
        ("Format", ctypes.c_uint),
    ]


def usable_refresh(refresh: int) -> int:
    """0 and 1 mean "the hardware's default", which the game cannot use."""
    return refresh if refresh > 1 else DEFAULT_REFRESH


def current_mode() -> Mode:
    """The main monitor's current mode, in real pixels."""
    mode = _DEVMODEW()
    mode.dmSize = ctypes.sizeof(_DEVMODEW)
    if not ctypes.windll.user32.EnumDisplaySettingsW(
        None, ENUM_CURRENT_SETTINGS, ctypes.byref(mode)
    ):
        raise FixError("Could not read the main monitor's display mode.")
    return Mode(
        mode.dmPelsWidth, mode.dmPelsHeight, usable_refresh(mode.dmDisplayFrequency)
    )


def direct3d_modes() -> list[Mode]:
    """The modes Direct3D 9 lists for adapter 0, in its own order.

    IDirect3D9 methods by vtable slot: 2 Release, 6 GetAdapterModeCount,
    7 EnumAdapterModes.
    """
    try:
        d3d9 = ctypes.windll.d3d9
    except OSError:
        raise FixError("Direct3D 9 is not available on this computer.") from None
    d3d9.Direct3DCreate9.restype = ctypes.c_void_p
    direct3d = d3d9.Direct3DCreate9(D3D_SDK_VERSION)
    if not direct3d:
        raise FixError("Direct3D 9 could not be started.")
    vtable = ctypes.cast(
        ctypes.cast(direct3d, ctypes.POINTER(ctypes.c_void_p))[0],
        ctypes.POINTER(ctypes.c_void_p),
    )

    def method(slot: int, *argtypes: type) -> ctypes._CFuncPtr:
        prototype = ctypes.WINFUNCTYPE(ctypes.c_long, ctypes.c_void_p, *argtypes)
        return prototype(vtable[slot])

    release = method(2)
    mode_count = method(6, ctypes.c_uint, ctypes.c_uint)
    enum_mode = method(
        7, ctypes.c_uint, ctypes.c_uint, ctypes.c_uint, ctypes.POINTER(_D3DDISPLAYMODE)
    )
    try:
        modes = []
        for index in range(mode_count(direct3d, 0, D3DFMT_X8R8G8B8)):
            mode = _D3DDISPLAYMODE()
            if enum_mode(direct3d, 0, D3DFMT_X8R8G8B8, index, ctypes.byref(mode)) == 0:
                modes.append(Mode(mode.Width, mode.Height, mode.RefreshRate))
        return modes
    finally:
        release(direct3d)


def game_sizes(modes: list[Mode]) -> list[tuple[int, int]]:
    """The game's numbered list: each size once, smallest first."""
    return sorted({(m.width, m.height) for m in modes if m.width >= MIN_WIDTH})


def resolution_index(sizes: list[tuple[int, int]], width: int, height: int) -> int:
    try:
        return sizes.index((width, height))
    except ValueError:
        raise FixError(
            f"The game does not offer {width}x{height}, the main monitor's resolution."
        ) from None
