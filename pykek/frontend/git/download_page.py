from gi.repository import Gtk, Adw  # type: ignore


class GitDownloadPageController:
    def __init__(self, navigation_view: Adw.NavigationView, git_url: str):
        self._navigation_view = navigation_view
        self._view = GitDownloadPage()

    def run(self):
        self._navigation_view.push(self._view)


class GitDownloadPage(Adw.NavigationPage):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.set_title("Git")
        self._setup_box()

        self._setup_header_bar()
        self._setup_content_box()

        self._setup_spinner_description_label()
        self._setup_spinner()

    ### UI

    def _setup_box(self) -> None:
        self._box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.set_child(self._box)

    def _setup_header_bar(self) -> None:
        header_bar = Adw.HeaderBar()
        header_bar.set_show_back_button(False)
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

    def _setup_spinner_description_label(self) -> None:
        label = Gtk.Label()
        label.set_css_classes(["dimmed"])
        label.set_text("Retrieving addon from git repository...")
        label.set_hexpand(True)
        self._content_box.append(label)

    def _setup_spinner(self) -> None:
        spinner = Gtk.Spinner(height_request=32)
        self._content_box.append(spinner)
        spinner.start()
