from gi.repository import Adw  # type: ignore # noqa: E402
from pykek.backend.config import Config  # noqa: E402
from pykek.frontend.addons import AddonsController
from pykek.frontend.onboarding import OnboardingController  # noqa: E402


class MainWindowController:
    def __init__(self, app) -> None:
        self._view = MainWindow(self, application=app)

    def run(self) -> None:
        self._view.present()
        self._run_addons_page()
        if len(Config.game_instances) == 0:
            self._run_onboarding()

    def _run_addons_page(self) -> None:
        addons_controller = AddonsController(self._view, self._view.navigation_view)
        addons_controller.run()

    def _run_onboarding(self) -> None:
        onboarding_controller = OnboardingController(self._view)
        onboarding_controller.connect_on_closed(self._on_onboarding_closed)
        onboarding_controller.connect_on_selection(
            lambda: self._on_onboarding_selection(onboarding_controller)
        )
        onboarding_controller.run()

    def _on_onboarding_closed(self):
        if len(Config.game_instances) == 0:
            quit()

    def _on_onboarding_selection(self, onboarding: OnboardingController) -> None:
        onboarding.close()


class MainWindow(Adw.ApplicationWindow):
    def __init__(self, controller: MainWindowController, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._controller = controller
        self._setup_window()
        self._setup_navigation_view()

    ### UI

    def _setup_window(self) -> None:
        self.set_default_size(750, 850)

    def _setup_navigation_view(self) -> None:
        self.navigation_view = Adw.NavigationView()
        self.set_content(self.navigation_view)
