from pykek.backend.addon import Addon, AddonStatus
from pykek.backend.game_instance import GameInstance
import pytest


class TestGameInstance:
    ### Tests

    def test_valid_dir(self, fs) -> None:
        "Test GameInstance init with a valid WoW dir path"
        fs.create_file("/games/wow/WoW.exe")

        instance = GameInstance.from_dir_path("/games/wow")

        assert instance.dir_path == "/games/wow"

    def test_invalid_dir(self) -> None:
        "Test GameInstance init with an invalid WoW dir path"
        with pytest.raises(Exception):
            GameInstance.from_dir_path("/games/wow")

    def test_load_addons(self, fs) -> None:
        "Test GameInstance loadAddons with 1 addon"
        fs.create_file("/games/wow/WoW.exe")
        fs.create_dir("/games/wow/Interface/AddOns/VeryCoolAddon")
        instance = GameInstance.from_dir_path("/games/wow")

        instance.load_addons()

        assert len(instance.addons) == 1

    def test_load_addons_skip_blizzard(self, fs) -> None:
        "Test GameInstance loadAddons with 2 addons, 1 being a Blizzard_ addon"
        fs.create_file("/games/wow/WoW.exe")
        fs.create_dir("/games/wow/Interface/AddOns/VeryCoolAddon")
        fs.create_dir("/games/wow/Interface/AddOns/Blizzard_Addon")
        instance = GameInstance.from_dir_path("/games/wow")

        instance.load_addons()

        assert len(instance.addons) == 1

    def test_load_addons_should_clear_addons(self, fs) -> None:
        "Test that GameInstance loadAddons should clear previous addons list"
        fs.create_file("/games/wow/WoW.exe")
        fs.create_dir("/games/wow/Interface/AddOns/VeryCoolAddon")
        instance = GameInstance.from_dir_path("/games/wow")
        instance.addons.append(
            Addon(
                dir_path="/games/wow/Interface/AddOns/PreviousAddon",
                name="PreviousAddon",
                is_git=False,
                version=None,
                current_status=AddonStatus.UP_TO_DATE,
                branches=[],
                current_branch="",
            )
        )

        instance.load_addons()

        assert len(instance.addons) == 1
