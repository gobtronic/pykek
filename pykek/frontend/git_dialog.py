import re
from gi.repository import Gtk, Adw  # type: ignore
from pykek.backend.addon import Addon


class GitDialogController:
    def __init__(self, window: Adw.ApplicationWindow, addon: Addon) -> None:
        self._window = window
        self._addon = addon
        self._navigation_view = Adw.NavigationView()
        self._dialog = Adw.Dialog(
            child=self._navigation_view,
            content_width=440,
        )
        setup_page = GitSetupPage(self)
        self._navigation_view.replace([setup_page])

    def run(self) -> None:
        self._dialog.present(self._window)

    def addon_name(self) -> str:
        return self._addon.name

    def close(self) -> None:
        self._dialog.close()

    def entry_row_did_change(self, page, text: str) -> None:  # type: ignore # noqa: F821
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


class GitDialog(Adw.Dialog):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._setup_dialog()

    ### UI

    def _setup_dialog(self) -> None:
        self.set_content_width(440)


class GitSetupPage(Adw.NavigationPage):
    def __init__(self, controller: GitDialogController, *args, **kwargs) -> None:
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
        entry_row = Adw.EntryRow(title="Git repository URL", name="ok")
        entry_row.set_css_classes(["card"])
        entry_row.connect("changed", self._on_entry_row_change)
        self._content_box.append(entry_row)

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
        self._controller.close()

    def _on_entry_row_change(self, entry_row: Adw.EntryRow) -> None:
        self._controller.entry_row_did_change(self, entry_row.get_text())

    ### UI updates

    def enable_save_button(self, enabled: bool) -> None:
        self._save_button.set_sensitive(enabled)
