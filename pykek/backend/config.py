from abc import ABC, abstractmethod
import os
from pathlib import Path
from loguru import logger
import platformdirs
from pykek.backend.game_instance import GameInstance
from typing import Dict, List, Optional, Protocol
import yaml


class ConfigListener(Protocol):
    def game_instances_did_change(self, instances: List[GameInstance]) -> None:
        pass


class Config(ABC):
    """myp
    Config stores the app's configuration,
    it should never be instanciated directly.

    Use `Config.load()` to load the config or `Config.write()` to write to it.
    """

    CONFIG_FILE_PATH = Path(
        os.path.join(platformdirs.user_config_path(appname="pykek"), "config.yml")
    )

    game_instances: List[GameInstance] = []
    favorite_instance: Optional[GameInstance] = None
    _listeners: List[ConfigListener] = []

    @abstractmethod
    def __init__(self) -> None:
        pass

    @staticmethod
    def load() -> None:
        """Loads the configuration by reading the config file"""
        if not Config.CONFIG_FILE_PATH.exists():
            logger.info(f"{Config.CONFIG_FILE_PATH} does not exist, it will be created")
            os.makedirs(Config.CONFIG_FILE_PATH.parent, exist_ok=True)
            with open(Config.CONFIG_FILE_PATH, "w") as f:
                f.close()
        else:
            with open(Config.CONFIG_FILE_PATH, "r") as f:
                conf = yaml.safe_load(f)
                f.close()

                if not isinstance(conf, Dict):
                    logger.error(
                        f"Unexpected error while reading {Config.CONFIG_FILE_PATH} file"
                    )
                    return

                instances = conf.get("instances", [])
                if not isinstance(instances, List):
                    logger.error(
                        f"Unexpected error while reading {Config.CONFIG_FILE_PATH} instances field"
                    )
                    return

                if len(instances) == 0:
                    logger.warning(
                        f"{Config.CONFIG_FILE_PATH} exists but instances field is missing or empty"
                    )
                else:
                    for wow_dir_path in instances:
                        try:
                            instance = GameInstance.from_dir_path(wow_dir_path)
                            Config.add_game_instance(instance)
                        except Exception as _:
                            pass

    @staticmethod
    def write() -> None:
        with open(Config.CONFIG_FILE_PATH, "w") as f:
            if len(Config.game_instances) == 0:
                f.close()
                return
            instances_paths = list(map(lambda i: i.dir_path, Config.game_instances))
            yaml_repr = {"instances": instances_paths}
            yaml.dump(yaml_repr, f)
            f.close()
        logger.info("Config file updated")

    @staticmethod
    def add_game_instance(game_instance: GameInstance) -> None:
        Config.game_instances.append(game_instance)
        for listener in Config._listeners:
            listener.game_instances_did_change(Config.game_instances)
            pass

    @staticmethod
    def add_listener(listener: ConfigListener, get_initial_value: bool) -> None:
        if Config._listeners.count(listener) > 0:
            return
        Config._listeners.append(listener)
        if get_initial_value:
            listener.game_instances_did_change(Config.game_instances)

    @staticmethod
    def remove_listener(listener: ConfigListener) -> None:
        Config._listeners.remove(listener)

    @staticmethod
    def reset() -> None:
        """Resets the config. Mostly used for testing purpose."""
        Config.game_instances = []
        Config.favorite_instance = None
        Config._listeners = []
