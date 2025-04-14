import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw  # type: ignore # noqa: E402
from pykek.backend.config import Config  # noqa: E402
from pykek.frontend.window import MainWindowController  # noqa: E402
import sys  # noqa: E402


class App(Adw.Application):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.connect("activate", self._on_activate)
        Config.load()

    def _on_activate(self, app):
        main_win_controller = MainWindowController(app)
        main_win_controller.run()


app = App(application_id="com.github.gobtronic.pykek")
app.run(sys.argv)
