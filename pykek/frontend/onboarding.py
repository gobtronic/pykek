from gi.repository import Gtk, Adw, Gio  # type: ignore
from pykek.backend.config import Config, GameInstance


class OnboardingController:
    def __init__(self, window: Adw.ApplicationWindow) -> None:
        self._window = window
        self._view = OnboardingDialog(self)
        self._view.connect("closed", self._on_closed)

    def run(self) -> None:
        self._view.present(self._window)

    def close(self) -> None:
        self._view.close()

    def get_window(self) -> Adw.ApplicationWindow:
        return self._window

    def show_file_chooser_dialog(self, _) -> None:
        self._view.show_file_chooser_dialog()

    def on_file_chooser_dialog_response(
        self, dialog: Gtk.FileChooserNative, response: Gtk.ResponseType
    ) -> None:
        if response != Gtk.ResponseType.ACCEPT:
            return
        directory = dialog.get_file()
        if not isinstance(directory, Gio.File):
            return
        dir_path = directory.get_path()
        if not isinstance(dir_path, str):
            return

        try:
            instance = GameInstance.from_dir_path(dir_path)
            Config.add_game_instance(instance)
            Config.write()
            self._on_onboarding_selection()
        except Exception as _:
            self._view.show_not_a_wow_directory_popover()

    def connect_on_selection(self, func) -> None:
        self._on_onboarding_selection = func

    def connect_on_closed(self, func) -> None:
        self._on_onboarding_closed = func

    def _on_closed(self, _) -> None:
        self._on_onboarding_closed()


class OnboardingDialog(Adw.Dialog):
    def __init__(self, controller: OnboardingController, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._controller = controller
        self._setup_dialog()
        self._setup_dialog_box()

        self._setup_logo()
        self._setup_labels_box()
        self._setup_title_label()
        self._setup_subtitle_label()
        self._setup_dir_button()
        self._setup_not_a_wow_directory_popover()

    ### UI

    def _setup_dialog(self) -> None:
        self.set_content_height(440)
        self.set_content_width(440)

    def _setup_dialog_box(self) -> None:
        self._dialog_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self._dialog_box.set_vexpand(True)
        self._dialog_box.set_valign(Gtk.Align.CENTER)
        self._dialog_box.set_spacing(30)
        self._dialog_box.set_margin_start(50)
        self._dialog_box.set_margin_end(50)
        self._dialog_box.set_margin_bottom(50)
        self._dialog_box.set_margin_top(50)
        self.set_child(self._dialog_box)

    def _setup_logo(self) -> None:
        logo = Gtk.Image.new_from_file("./data/icons/kek.svg")
        logo.set_pixel_size(150)
        self._dialog_box.append(logo)

    def _setup_labels_box(self) -> None:
        self._labels_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self._labels_box.set_spacing(5)
        self._dialog_box.append(self._labels_box)

    def _setup_title_label(self) -> None:
        label = Gtk.Label()
        label.set_css_classes(["title-1"])
        label.set_text("pykek")
        label.set_justify(Gtk.Justification.CENTER)
        self._labels_box.append(label)

    def _setup_subtitle_label(self) -> None:
        label = Gtk.Label()
        label.set_css_classes(["header"])
        label.set_text("Your Vanilla addons manager")
        label.set_justify(Gtk.Justification.CENTER)
        self._labels_box.append(label)

    def _setup_dir_button(self) -> None:
        self._dir_button = Gtk.Button()
        self._dir_button.set_css_classes(["pill", "suggested-action"])
        self._dir_button.set_label("Start by selecting your WoW directory")
        self._dir_button.connect("clicked", self._controller.show_file_chooser_dialog)
        self._dialog_box.append(self._dir_button)

    def _setup_not_a_wow_directory_popover(self) -> None:
        label = Gtk.Label()
        label.set_css_classes(["warning"])
        label.set_text("⚠️  Couldn't find WoW.exe")
        box = Gtk.Box()
        box.set_margin_start(5)
        box.set_margin_end(5)
        box.set_margin_top(3)
        box.set_margin_bottom(3)
        box.append(label)

        self._popover = Gtk.Popover()
        self._popover.set_parent(self._dir_button)
        self._popover.set_child(box)
        self._popover.set_css_classes(["warning"])
        self._popover.set_offset(0, 4)
        self._popover.set_autohide(False)

    ### Actions

    def show_file_chooser_dialog(self) -> None:
        self._popover.popdown()
        dialog = Gtk.FileChooserNative.new(
            title="Select your WoW directory",
            action=Gtk.FileChooserAction.SELECT_FOLDER,
            parent=self._controller.get_window(),
            accept_label="Select",
        )
        dialog.connect("response", self._controller.on_file_chooser_dialog_response)
        dialog.set_modal(True)
        dialog.show()

    def show_not_a_wow_directory_popover(self) -> None:
        self._popover.popup()
