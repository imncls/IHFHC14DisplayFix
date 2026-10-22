import pytest

from displayfix import FixError
from displayfix.modes import Mode, game_sizes, resolution_index, usable_refresh

# Adapter 0 of a laptop as Direct3D 9 lists it: current mode first, each size
# once per refresh rate, 640x480 included.
LAPTOP = [
    Mode(1920, 1080, 144),
    Mode(1920, 1080, 60),
    Mode(640, 480, 144),
    Mode(640, 480, 60),
    Mode(800, 600, 144),
    Mode(800, 600, 60),
    Mode(1024, 768, 144),
    Mode(1024, 768, 60),
    Mode(1152, 864, 144),
    Mode(1280, 600, 144),
    Mode(1280, 720, 144),
    Mode(1280, 768, 144),
    Mode(1280, 800, 144),
    Mode(1280, 960, 144),
    Mode(1280, 1024, 144),
    Mode(1360, 768, 144),
    Mode(1366, 768, 144),
    Mode(1400, 1050, 144),
    Mode(1440, 900, 144),
    Mode(1600, 900, 144),
    Mode(1680, 1050, 144),
    Mode(1680, 1050, 60),
]


def test_sizes_are_unique_sorted_and_from_800_wide() -> None:
    sizes = game_sizes(LAPTOP)
    assert sizes[0] == (800, 600)
    assert sizes == sorted(set(sizes))
    assert (640, 480) not in sizes


def test_indexes_measured_in_the_game() -> None:
    # Measured on that laptop: 15 opens 1920x1080 and 14 opens 1680x1050.
    sizes = game_sizes(LAPTOP)
    assert resolution_index(sizes, 1920, 1080) == 15
    assert resolution_index(sizes, 1680, 1050) == 14


def test_a_size_the_game_does_not_offer() -> None:
    with pytest.raises(FixError, match="2560x1440"):
        resolution_index(game_sizes(LAPTOP), 2560, 1440)


@pytest.mark.parametrize(("refresh", "used"), [(0, 60), (1, 60), (60, 60), (144, 144)])
def test_usable_refresh(refresh: int, used: int) -> None:
    assert usable_refresh(refresh) == used
