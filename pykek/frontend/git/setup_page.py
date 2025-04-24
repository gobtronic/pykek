from typing import Protocol
from gi.repository import Gtk, Adw  # type: ignore


class GitSetupPageHandler(Protocol):
    def on_git_setup_page_entry_row_change(self, page, text: str) -> None:
        pass

    def on_git_setup_page_close_button_click(self, page) -> None:
        pass

    def on_git_setup_page_save_button_click(self, page, git_url: str) -> None:
        pass


class GitSetupPageController:
    def __init__(
        self,
        handler: GitSetupPageHandler,
        navigation_view: Adw.NavigationView,
        addon_name: str,
    ) -> None:
        self._handler = handler
        self._navigation_view = navigation_view
        self._addon_name = addon_name
        self._view = GitSetupPage(self)

    def run(self):
        self._navigation_view.push(self._view)

    def addon_name(self) -> str:
        return self._addon_name

    ### Actions

    def on_entry_row_change(self, page, text: str) -> None:
        self._handler.on_git_setup_page_entry_row_change(page, text)

    def on_close_button_click(self, page) -> None:
        self._handler.on_git_setup_page_close_button_click(page)

    def _on_save_button_click(self, page, git_url: str) -> None:
        self._handler.on_git_setup_page_save_button_click(page, git_url)


class GitSetupPage(Adw.NavigationPage):
    def __init__(
        self,
        controller: GitSetupPageController,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self._controller = controller
        self.set_title("Git")
        self._setup_box()

        self._setup_header_bar()
        self._setup_content_box()

        self._setup_description_label()
        self._setup_entry_row()
        self._setup_entry_row_description_label()

    ### UI

    def _setup_box(self) -> None:
        self._box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.set_child(self._box)

    def _setup_header_bar(self) -> None:
        header_bar = Adw.HeaderBar()
        cancel_button = Gtk.Button(label="Cancel")
        cancel_button.connect("clicked", self._on_cancel_button_click)
        header_bar.pack_start(cancel_button)

        self._save_button = Gtk.Button(label="Save")
        self._save_button.set_css_classes(["suggested-action"])
        self._save_button.set_sensitive(False)
        self._save_button.connect("clicked", self._on_save_button_click)
        header_bar.pack_end(self._save_button)

        self._box.append(header_bar)

    def _setup_content_box(self) -> None:
        self._content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self._content_box.set_vexpand(True)
        self._content_box.set_valign(Gtk.Align.CENTER)
        self._content_box.set_spacing(12)
        self._content_box.set_margin_top(30)
        self._content_box.set_margin_start(25)
        self._content_box.set_margin_end(25)
        self._content_box.set_margin_bottom(35)
        self._box.append(self._content_box)

    def _setup_description_label(self) -> None:
        label = Gtk.Label()
        label.set_css_classes(["dimmed"])
        label.set_text(f"Setup {self._controller.addon_name()} git repository.")
        label.set_justify(Gtk.Justification.FILL)
        label.set_hexpand(True)
        label.set_halign(Gtk.Align.START)
        self._content_box.append(label)

    def _setup_entry_row(self) -> None:
        self._entry_row = Adw.EntryRow(title="Git repository URL", name="ok")
        self._entry_row.set_css_classes(["card"])
        self._entry_row.connect("changed", self._on_entry_row_change)
        self._content_box.append(self._entry_row)

    def _setup_entry_row_description_label(self) -> None:
        label = Gtk.Label()
        label.set_css_classes(["warning"])
        label.set_text("⚠️  This will overwrite the current addon version!")
        label.set_justify(Gtk.Justification.FILL)
        label.set_hexpand(True)
        label.set_halign(Gtk.Align.START)
        self._content_box.append(label)

    ### Actions

    def _on_cancel_button_click(self, button) -> None:
        self._controller.on_close_button_click(self)

    def _on_save_button_click(self, button) -> None:
        self._controller._on_save_button_click(self, self._entry_row.get_text())

    def _on_entry_row_change(self, entry_row: Adw.EntryRow) -> None:
        self._controller.on_entry_row_change(self, entry_row.get_text())

    ### UI updates

    def enable_save_button(self, enabled: bool) -> None:
        self._save_button.set_sensitive(enabled)
