import os
from pathlib import Path
from pykek.backend.config import Config
from pykek.backend.game_instance import GameInstance


class TestConfig:
    ### Setup / Teardown

    @classmethod
    def setup_class(cls) -> None:
        Config.CONFIG_FILE_PATH = Path("/config/pykek/config.yml")

    def teardown_method(self) -> None:
        Config.reset()

    ### Tests

    def test_load_no_config(self, fs) -> None:
        "Test `Config.load()` when there's no config file."
        Config.load()

        assert os.path.exists(Config.CONFIG_FILE_PATH)
        assert len(Config.game_instances) == 0

    def test_load_invalid_wow_instance(self, fs) -> None:
        "Test `Config.load()` with a config file containing an invalid WoW instance."
        fs.create_file(
            "/config/pykek/config.yml",
            contents="""instances:
- /games/wow/ 
""",
        )

        Config.load()

        assert len(Config.game_instances) == 0

    def test_load_valid_wpw_instance(self, fs) -> None:
        "Test `Config.load()` with a config file containing a valid WoW instance."
        fs.create_file("/games/wow/WoW.exe")
        fs.create_file(
            "/config/pykek/config.yml",
            contents="""instances:
- /games/wow/ 
""",
        )

        Config.load()

        assert len(Config.game_instances) == 1
        assert Config.game_instances[0].dir_path == "/games/wow/"

    def test_load_mixed_wow_instances(self, fs) -> None:
        "Test `Config.load()` with a config file containing 2 WoW instances: one invalid and one valid."
        fs.create_file("/games/wow2/WoW.exe")
        fs.create_file(
            "/config/pykek/config.yml",
            contents="""instances:
- /games/wow1/
- /games/wow2/
""",
        )

        Config.load()

        assert len(Config.game_instances) == 1
        assert Config.game_instances[0].dir_path == "/games/wow2/"

    def test_load_invalid_config(self, fs) -> None:
        "Test `Config.load()` with an incorrectly formatted config file."
        fs.create_file("/games/wow/WoW.exe")
        fs.create_file(
            "/config/pykek/config.yml",
            contents="instances: /games/wow/",
        )

        Config.load()

        assert len(Config.game_instances) == 0

    def test_write_instances(self, fs) -> None:
        "Test `Config.write()` with two WoW instances."
        Config.load()
        fs.create_file("/games/wow1/WoW.exe")
        fs.create_file("/games/wow2/WoW.exe")
        Config.game_instances.append(GameInstance.from_dir_path("/games/wow1"))
        Config.game_instances.append(GameInstance.from_dir_path("/games/wow2"))
        expected_raw_conf = """instances:
- /games/wow1
- /games/wow2
"""

        Config.write()
        with open(Config.CONFIG_FILE_PATH, "r") as f:
            raw_conf = f.read()
            f.close()
            assert raw_conf == expected_raw_conf

    def test_write_no_instance(self, fs) -> None:
        "Test `Config.write()` with no instances."
        Config.load()
        expected_raw_conf = ""

        Config.write()
        with open(Config.CONFIG_FILE_PATH, "r") as f:
            raw_conf = f.read()
            f.close()
            assert raw_conf == expected_raw_conf
