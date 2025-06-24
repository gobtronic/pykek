from typing import Protocol


class GitDialogCoordinator(Protocol):
    def repository_entry_row_did_change(self, page, text: str) -> None:
        pass

    def close_button_clicked(self, page) -> None:
        pass

    def install_button_clicked(self, page, git_url: str) -> None:
        pass

    def install_succeed(self) -> None:
        pass

    def install_failed(self) -> None:
        pass

    def back_to_start_button_clicked(self, page) -> None:
        pass
