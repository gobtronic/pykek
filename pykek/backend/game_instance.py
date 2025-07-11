from dataclasses import dataclass, field
from typing import List, Protocol
from loguru import logger
import os
from pathlib import Path
from pykek.backend.addon import Addon


class GameInstanceListener(Protocol):
    def addons_did_load(self, addons: List[Addon]) -> None:
        pass


@dataclass
class GameInstance:
    """GameInstance stores various information about a WoW instance."""

    dir_path: str
    addons: List[Addon]

    _listeners: List[GameInstanceListener] = field(
        init=False, repr=False, default_factory=list
    )

    @classmethod
    def from_dir_path(cls, dir_path: str):
        if not _is_wow_dir(dir_path):
            logger.error(
                f"{dir_path} doesn't seem to be a WoW directory (WoW.exe not found)"
            )
            raise Exception("Not a valid WoW directory path")
        logger.success(f"Loaded {dir_path} instance")
        return cls(dir_path, [])

    def add_listener(self, listener: GameInstanceListener) -> None:
        if self._listeners.count(listener) > 0:
            return
        self._listeners.append(listener)

    def remove_listener(self, listener: GameInstanceListener) -> None:
        self._listeners.remove(listener)

    def load_addons(self):
        self.addons.clear()
        addons_path = Path(os.path.join(self.dir_path, "Interface/AddOns"))
        directories = [p for p in addons_path.iterdir() if p.is_dir()]
        for directory in directories:
            if directory.name.startswith("Blizzard_"):
                continue
            addon = Addon.from_dir_path(directory)
            self.addons.append(addon)
        for listener in self._listeners:
            listener.addons_did_load(self.addons)


def _is_wow_dir(dir_path: str) -> bool:
    wow_exe_path = Path(os.path.join(dir_path, "WoW.exe"))
    return os.path.exists(wow_exe_path)
