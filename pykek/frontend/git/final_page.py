from gi.repository import Gtk, Adw  # type: ignore

from pykek.frontend.git.dialog_coordinator import GitDialogCoordinator


class GitFinalPageController:
    def __init__(
        self,
        coordinator: GitDialogCoordinator,
        navigation_view: Adw.NavigationView,
        success: bool,
    ):
        self._coordinator = coordinator
        self._navigation_view = navigation_view
        self._view = GitFinalPage(self, success)

    def run(self) -> None:
        self._navigation_view.push(self._view)

    ### Actions

    def on_close_button_click(self, page) -> None:
        self._coordinator.close_button_clicked(page)

    def on_back_button_click(self, page) -> None:
        self._coordinator.back_to_start_button_clicked(page)


class GitFinalPage(Adw.NavigationPage):
    def __init__(
        self,
        controller: GitFinalPageController,
        success: bool,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self._controller = controller
        self._success = success
        self.set_title("Install an addon")
        self._setup_box()

        self._setup_header_bar()
        self._setup_content_box()

        self._setup_content_label()

    ### UI

    def _setup_box(self) -> None:
        self._box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.set_child(self._box)

    def _setup_header_bar(self) -> None:
        header_bar = Adw.HeaderBar()
        header_bar.set_show_back_button(False)
        if self._success:
            cancel_button = Gtk.Button(label="Close")
            cancel_button.connect("clicked", self._on_close_button_click)
            header_bar.pack_start(cancel_button)
        else:
            back_button = Gtk.Button(label="Back to setup")
            back_button.connect("clicked", self._on_back_button_click)
            header_bar.pack_start(back_button)
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

    def _setup_content_label(self) -> None:
        label = Gtk.Label()
        label.set_hexpand(True)
        if self._success:
            label.set_css_classes(["success"])
            label.set_text("Addon installed!")
        else:
            label.set_css_classes(["error"])
            label.set_text("An error occured during installation")
        self._content_box.append(label)

    ### Actions

    def _on_close_button_click(self, _) -> None:
        self._controller.on_close_button_click(self)

    def _on_back_button_click(self, _) -> None:
        self._controller.on_back_button_click(self)
