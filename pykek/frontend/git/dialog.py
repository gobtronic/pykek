import re
from gi.repository import Adw  # type: ignore
from pykek.backend.addon import Addon
from pykek.frontend.git.setup_page import GitSetupPage


class GitDialogController:
    def __init__(self, window: Adw.ApplicationWindow, addon: Addon) -> None:
        self._window = window
        self._addon = addon
        self._navigation_view = Adw.NavigationView()
        self._dialog = Adw.Dialog(
            child=self._navigation_view,
            content_width=440,
        )
        setup_page = GitSetupPage(self, self._addon.name)
        self._navigation_view.replace([setup_page])

    def run(self) -> None:
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

    ### GitSetupPageHandler

    def git_setup_page_entry_row_did_change(
        self,
        page: GitSetupPage,
        text: str,
    ) -> None:
        valid_url = self._is_valid_url(text)
        page.enable_save_button(valid_url)

    def git_setup_page_wants_to_close(self, page: GitSetupPage) -> None:
        self._dialog.close()


class GitDialog(Adw.Dialog):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._setup_dialog()

    ### UI

    def _setup_dialog(self) -> None:
        self.set_content_width(440)
