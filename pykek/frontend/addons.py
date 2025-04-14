import threading
from typing import List, Optional
from gi.repository import Gtk, Adw  # type: ignore
from pykek.backend.addon import Addon
from pykek.backend.config import Config
from pykek.backend.game_instance import GameInstance
from pykek.frontend.addon_row import AddonRowController


class AddonsController:
    def __init__(self, navigation_view: Adw.NavigationView) -> None:
        Config.add_listener(listener=self)
        self._navigation_view = navigation_view
        self._view = AddonsPage(self)

        self._reload_instance_addons()
        self._view.reload_list()
        self._update_addons_status()

    def run(self) -> None:
        self._navigation_view.replace([self._view])

    ### Addons

    def _reload_instance_addons(self) -> None:
        if len(Config.game_instances) > 0:
            instance = Config.game_instances[0]
            instance.load_addons()

    def _update_addons_status(self) -> None:
        if len(Config.game_instances) > 0:
            instance = Config.game_instances[0]
            for addon in instance.addons:
                thread = threading.Thread(target=addon.update_status)
                thread.start()

    ### List

    def number_of_items(self) -> int:
        if len(Config.game_instances) == 0:
            return 0
        return len(Config.game_instances[0].addons)

    def item(self, item_index: int) -> Optional[Addon]:
        if len(Config.game_instances) == 0:
            return None
        instance = Config.game_instances[0]
        if len(instance.addons) < item_index:
            return None
        return instance.addons[item_index]

    ### ConfigListener

    def game_instances_did_change(self, instances: List[GameInstance]) -> None:
        self._reload_instance_addons()
        self._view.reload_list()


class AddonsPage(Adw.NavigationPage):
    def __init__(self, controller: AddonsController, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.set_title("pykek")
        self._controller = controller

        self._setup_page_box()
        self._setup_header_bar()
        self._setup_preferences_page()
        self._setup_preferences_group()
        self._setup_list_box()

    ### UI

    def _setup_page_box(self) -> None:
        self._page_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self._page_box.set_hexpand(True)
        self._page_box.set_vexpand(True)
        self.set_child(self._page_box)

    def _setup_header_bar(self) -> None:
        header_bar = Adw.HeaderBar()
        self._page_box.append(header_bar)

    def _setup_preferences_page(self) -> None:
        self._pref_page = Adw.PreferencesPage.new()
        self._page_box.append(self._pref_page)

    def _setup_preferences_group(self) -> None:
        self._group = Adw.PreferencesGroup.new()
        self._pref_page.add(self._group)

    def _setup_list_box(self) -> None:
        self._list_box = Gtk.ListBox()
        self._list_box.set_css_classes(["boxed-list"])
        self._list_box.set_selection_mode(Gtk.SelectionMode.NONE)
        self._group.add(self._list_box)

    ### ListView

    def reload_list(self) -> None:
        self._list_box.remove_all()
        for i in range(0, self._controller.number_of_items()):
            addon = self._controller.item(i)
            if not isinstance(addon, Addon):
                continue
            controller = AddonRowController(addon)
            self._list_box.append(controller.view())
