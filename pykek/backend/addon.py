from dataclasses import dataclass, field
from enum import Enum
import os
from pathlib import Path
import re
from typing import Optional, Protocol
from git import List, Repo


class AddonStatus(Enum):
    UP_TO_DATE = 1
    OUTDATED = 2
    NON_GIT = 3
    LOADING = 4

    @staticmethod
    def icon_name(self) -> str:
        if self == AddonStatus.UP_TO_DATE:
            return "checkmark-symbolic"
        if self == AddonStatus.OUTDATED:
            return "folder-download-symbolic"
        if self == AddonStatus.NON_GIT:
            return "dialog-warning-symbolic"
        return "process-working-symbolic"


@dataclass
class AddonStatusRepresentation:
    icon_name: str
    css_class: str
    label: str

    @classmethod
    def from_status(cls, status: AddonStatus):
        if status == AddonStatus.UP_TO_DATE:
            return cls(
                icon_name="checkmark-symbolic",
                css_class="success",
                label="This addon is up-to-date.",
            )
        if status == AddonStatus.OUTDATED:
            return cls(
                icon_name="folder-download-symbolic",
                css_class="accent",
                label="TThis addon has an update available to download.",
            )
        if status == AddonStatus.NON_GIT:
            return cls(
                icon_name="dialog-warning-symbolic",
                css_class="warning",
                label="This addon is not versioned, meaning you won't be able to see if there is an update available.",
            )
        if status == AddonStatus.LOADING:
            return cls(
                icon_name="process-working-symbolic",
                css_class="",
                label="",
            )
        raise Exception(f"Unexpected AddonStatus {status}")


class AddonListener(Protocol):
    def addon_status_did_change(self, new_status: AddonStatus) -> None:
        pass

    def addon_version_did_change(self, new_version: Optional[str]) -> None:
        pass


@dataclass
class Addon:
    dir_path: str
    name: str
    is_git: bool
    version: Optional[str]
    current_status: AddonStatus
    branches: List[str]
    current_branch: str

    _listeners: List[AddonListener] = field(
        init=False, repr=False, default_factory=list
    )

    @classmethod
    def from_dir_path(cls, dir_path: Path):
        name = dir_path.name
        is_git = _is_git_dir(dir_path)
        toc_info = _parse_toc(dir_path, name)
        version = None
        if isinstance(toc_info, _TOCInfo):
            version = toc_info.version
        return cls(
            dir_path=str(dir_path),
            name=name,
            is_git=is_git,
            version=version,
            current_status=AddonStatus.UP_TO_DATE if is_git else AddonStatus.NON_GIT,
            branches=[],
            current_branch="",
        )

    def add_listener(self, listener: AddonListener) -> None:
        if self._listeners.count(listener) > 0:
            return
        self._listeners.append(listener)

    def remove_listener(self, listener: AddonListener) -> None:
        self._listeners.remove(listener)

    def update_status(self) -> None:
        if self.is_git:
            if self.current_status != AddonStatus.LOADING:
                self.current_status = AddonStatus.LOADING
                for listener in self._listeners:
                    listener.addon_status_did_change(self.current_status)
            has_update = self.check_for_update()
            new_status = AddonStatus.OUTDATED if has_update else AddonStatus.UP_TO_DATE
            if self.current_status != new_status:
                self.current_status = new_status
                for listener in self._listeners:
                    listener.addon_status_did_change(self.current_status)
        else:
            if self.current_status != AddonStatus.NON_GIT:
                self.current_status = AddonStatus.NON_GIT
                for listener in self._listeners:
                    listener.addon_status_did_change(self.current_status)

    def check_for_update(self) -> bool:
        if not self.is_git:
            return False
        repo = Repo(self.dir_path)
        remote = repo.remote()
        remote.fetch()
        commits = list(repo.iter_commits(f"HEAD..origin/{self.current_branch}"))
        return len(commits) > 0

    def update(self) -> None:
        if not self.is_git:
            return
        self.current_status = AddonStatus.LOADING
        for listener in self._listeners:
            listener.addon_status_did_change(self.current_status)
        repo = Repo(self.dir_path)
        repo.git.reset("--hard", f"origin/{self.current_branch}")
        self.current_status = AddonStatus.UP_TO_DATE
        for listener in self._listeners:
            listener.addon_status_did_change(self.current_status)

    def reload_branches(self) -> None:
        if not self.is_git:
            return
        repo = Repo(self.dir_path)
        remote = repo.remote()
        branches = []
        for ref in remote.refs:
            if ref.name == "origin/HEAD":
                continue
            branches.append(ref.name.removeprefix("origin/"))
        self.branches = branches
        self.current_branch = repo.active_branch.name

    def switch_to_branch(self, branch: str) -> None:
        if not self.is_git:
            return
        self.current_status = AddonStatus.LOADING
        for listener in self._listeners:
            listener.addon_status_did_change(self.current_status)
        repo = Repo(self.dir_path)
        if repo.is_dirty():
            repo.git.reset("--hard")
        repo.git.checkout("--force", f"{branch}")
        self.current_status = AddonStatus.UP_TO_DATE
        for listener in self._listeners:
            listener.addon_status_did_change(self.current_status)

    def refresh_toc_info(self) -> None:
        toc_info = _parse_toc(Path(self.dir_path), self.name)
        version = None
        if isinstance(toc_info, _TOCInfo):
            version = toc_info.version
        if self.version != version:
            self.version = version
            for listener in self._listeners:
                listener.addon_version_did_change(version)


def _is_git_dir(addon_dir_path: Path) -> bool:
    git_dir_path = Path(os.path.join(addon_dir_path, ".git"))
    return os.path.exists(git_dir_path)


@dataclass
class _TOCInfo:
    version: Optional[str]

    @classmethod
    def from_toc_path(cls, path: Path):
        with open(path, "r") as f:
            content = f.read()
            version = _extract_value("Version", content)
            return cls(version)
        raise Exception(f"Couldn't read TOC file at {path}")


def _parse_toc(addon_dir_path: Path, addon_name: str) -> Optional[_TOCInfo]:
    toc_path = Path(os.path.join(addon_dir_path, f"{addon_name}.toc"))
    try:
        toc = _TOCInfo.from_toc_path(toc_path)
        return toc
    except Exception as _:
        return None


def _extract_value(key: str, text: str) -> Optional[str]:
    pattern = rf"{re.escape(key)}\s*:\s*([^\n]*)"
    match = re.search(pattern, text)
    if match:
        return match.group(1).strip()
    else:
        return None
