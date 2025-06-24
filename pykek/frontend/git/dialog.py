import re
from gi.repository import Adw  # type: ignore

from pykek.backend.addon import Addon
from pykek.frontend.git.download_page import GitDownloadPageController
from pykek.frontend.git.setup_page import GitSetupPage, GitSetupPageController
from pykek.frontend.git.final_page import GitFinalPageController


class GitDialogController:
    def __init__(self, window: Adw.ApplicationWindow, addon: Addon) -> None:
        self._window = window
        self._addon = addon
        self._navigation_view = Adw.NavigationView()
        self._dialog = Adw.Dialog(
            child=self._navigation_view,
            content_width=440,
        )

    def run(self) -> None:
        setup_controller = GitSetupPageController(
            self,
            self._navigation_view,
            self._addon.name,
        )
        setup_controller.run()
        self._dialog.present(self._window)

    def entry_row_did_change(self, page: GitSetupPage, text: str) -> None:
        valid_url = self._is_valid_url(text)
        page.enable_save_button(valid_url)

    def _is_valid_url(self, text: str) -> bool:
        pattern = re.compile(
            r"^https://"
            r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|"
            r"localhost|"
            r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|"
            r"\[?[A-F0-9]*:[A-F0-9:]+\]?)"
            r"(?::\d+)?"
            r"(?:/?|[/?]\S+)$",
            re.IGNORECASE,
        )

        return re.match(pattern, text) is not None

    ### GitDialogCoordinator

    def repository_entry_row_did_change(
        self,
        page: GitSetupPage,
        text: str,
    ) -> None:
        valid_url = self._is_valid_url(text)
        page.enable_save_button(valid_url)

    def close_button_clicked(self, _) -> None:
        self._dialog.close()

    def install_button_clicked(self, _, git_url: str) -> None:
        dl_controller = GitDownloadPageController(
            self,
            self._navigation_view,
            self._addon,
            git_url,
        )
        dl_controller.run()

    def install_succeed(self) -> None:
        final_controller = GitFinalPageController(
            self,
            self._navigation_view,
            True,
        )
        final_controller.run()

    def install_failed(self) -> None:
        final_controller = GitFinalPageController(
            self,
            self._navigation_view,
            False,
        )
        final_controller.run()

    def back_to_start_button_clicked(self, _) -> None:
        self._navigation_view.pop_to_tag("setup")


class GitDialog(Adw.Dialog):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._setup_dialog()

    ### UI

    def _setup_dialog(self) -> None:
        self.set_content_width(480)
