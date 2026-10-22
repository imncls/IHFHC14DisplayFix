from pathlib import Path

import pytest

# The layout the game writes (Windows line endings here, to check they stay).
SAMPLE_CFG = (
    '<?xml version="1.0" encoding="iso-8859-15" standalone="yes" ?>\r\n'
    "<!--Warning: change on own risk!-->\r\n"
    "<Configuration>\r\n"
    "    <Name>Sample</Name>\r\n"
    "    <Graphics>\r\n"
    "        <Resolution>3</Resolution>\r\n"
    "        <TextureQuality>4</TextureQuality>\r\n"
    "        <Fullscreen>0</Fullscreen>\r\n"
    "        <HDR>1</HDR>\r\n"
    "        <RefreshRate>0</RefreshRate>\r\n"
    "    </Graphics>\r\n"
    "    <Sound>\r\n"
    "        <!--min. 0, max. 1-->\r\n"
    "        <Music>0.5</Music>\r\n"
    "    </Sound>\r\n"
    "</Configuration>\r\n"
)


@pytest.fixture
def cfg(tmp_path: Path) -> Path:
    path = tmp_path / "game.cfg"
    path.write_bytes(SAMPLE_CFG.encode("iso-8859-15"))
    return path
