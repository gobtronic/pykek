from pathlib import Path

import pytest
from pykek.backend.addon import Addon, _TOCInfo


class TestAddon:
    ### Tests

    def test_from_dir_path(self) -> None:
        addon = Addon.from_dir_path(Path("fake/path/VeryCoolAddon"))

        assert addon.dir_path == "fake/path/VeryCoolAddon"
        assert addon.name == "VeryCoolAddon"

    def test_toc_info_invalid_file(self, fs) -> None:
        with pytest.raises(Exception):
            _TOCInfo.from_toc_path(Path("/fake/path/VeryCoolAddon/VeryCoolAddon.toc"))

    def test_toc_info_file_exists(self, fs) -> None:
        fs.create_file("/fake/path/VeryCoolAddon/VeryCoolAddon.toc")

        toc = _TOCInfo.from_toc_path(Path("/fake/path/VeryCoolAddon/VeryCoolAddon.toc"))

        assert toc.version is None

    def test_toc_info_valid_file(self, fs) -> None:
        fs.create_file(
            "/fake/path/VeryCoolAddon/VeryCoolAddon.toc",
            contents="""
### Stuff: Blabla
### Version: 1.4.5
### Comment: Some more stuff""",
        )

        toc = _TOCInfo.from_toc_path(Path("/fake/path/VeryCoolAddon/VeryCoolAddon.toc"))

        assert toc.version == "1.4.5"
