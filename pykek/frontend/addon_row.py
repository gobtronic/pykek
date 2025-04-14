import threading
from typing import List, Optional
from gi.repository import Gtk, Adw  # type: ignore
from pykek.backend.addon import Addon, AddonStatus, AddonStatusRepresentation


class AddonRowController:
    def __init__(self, addon: Addon) -> None:
        self._addon = addon
        self._addon.reload_branches()
        self._view = AddonRow(self, addon)
        addon.add_listener(self._view)

    def view(self):
        return self._view

    def title(self) -> str:
        return self._addon.name

    def version(self) -> Optional[str]:
        return self._addon.version

    def available_branches(self) -> List[str]:
        return self._addon.branches

    def current_addon_status(self) -> AddonStatus:
        return self._addon.current_status

    def current_branch_index(self):
        try:
            return self._addon.branches.index(self._addon.current_branch)
        except Exception as _:
            return 0

    def should_show_dropdown(self) -> bool:
        return self._addon.is_git

    ### Actions

    def update_addon(self) -> None:
        thread = threading.Thread(target=self._update_addon)
        thread.start()

    def _update_addon(self) -> None:
        self._addon.update()
        self._addon.refresh_toc_info()

    def switch_branch(self, branch: str) -> None:
        thread = threading.Thread(target=self._switch_branch, args=[branch])
        thread.start()

    def _switch_branch(self, branch: str) -> None:
        self._addon.switch_to_branch(branch)
        self._addon.refresh_toc_info()


class AddonRow(Adw.ActionRow):
    def __init__(self, controller: AddonRowController, *args, **kwargs) -> None:
        super().__init__()
        self._controller = controller
        self.set_activatable(True)
        self.set_title(controller.title())

        self._setup_suffix_box()
        self._setup_version_tag()
        self._setup_branches_dropdown()
        self._setup_action_button()

        self._update_action_box(self._controller.current_addon_status())

    ### UI

    def _setup_suffix_box(self) -> None:
        self._suffix_box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 10)
        self.add_suffix(self._suffix_box)

    def _setup_version_tag(self) -> None:
        version = self._controller.version()
        if not isinstance(version, str):
            return
        if version == "None" or version == "GIT":
            return
        self._version_button = Gtk.Button(
            label=version, valign=Gtk.Align.CENTER, vexpand=False
        )
        self._version_button.set_css_classes(["accent", "caption"])
        self._version_button.set_can_target(False)
        self._suffix_box.append(self._version_button)

    def _setup_branches_dropdown(self) -> None:
        if not self._controller.should_show_dropdown():
            return
        branches = Gtk.StringList()
        for branch in self._controller.available_branches():
            branches.append(branch)
        self._branches_dropdown = Gtk.DropDown.new(branches, None)
        self._branches_dropdown.set_valign(Gtk.Align.CENTER)
        self._branches_dropdown.set_selected(self._controller.current_branch_index())
        self._branches_dropdown.connect(
            "notify::selected", self._on_branches_dropdown_selection
        )
        self._suffix_box.append(self._branches_dropdown)

    def _setup_action_button(self) -> None:
        self._action_button = Gtk.Button(
            valign=Gtk.Align.CENTER,
        )
        self._action_button.connect("clicked", self._on_action_button_clicked)
        self._suffix_box.append(self._action_button)

    ### UI updates

    def _update_action_box(self, addon_status: AddonStatus) -> None:
        status_repr = AddonStatusRepresentation.from_status(addon_status)
        self._action_button.set_icon_name(status_repr.icon_name)
        self._action_button.set_css_classes([status_repr.css_class])
        self._action_button.set_tooltip_text(status_repr.label)

        if addon_status == AddonStatus.LOADING:
            spinner = Gtk.Spinner()
            self._action_button.set_child(spinner)
            spinner.start()
        if addon_status == AddonStatus.OUTDATED:
            self._action_button.set_sensitive(True)
        elif addon_status == AddonStatus.NON_GIT:
            self._action_button.set_sensitive(
                False
            )  # TODO: Add support for setting-up addon repository link
        else:
            self._action_button.set_sensitive(False)

    ### Action

    def _on_action_button_clicked(self, button: Gtk.Button) -> None:
        self._controller.update_addon()

    def _on_branches_dropdown_selection(self, dropdown: Gtk.DropDown, param) -> None:
        item = dropdown.get_selected_item()
        if not isinstance(item, Gtk.StringObject):
            return
        self._controller.switch_branch(item.get_string())

    ### AddonListener

    def addon_status_did_change(self, new_status: AddonStatus) -> None:
        self._update_action_box(new_status)

    def addon_version_did_change(self, new_version: Optional[str]) -> None:
        if not isinstance(new_version, str):
            self._version_button.set_visible(False)
            return
        self._version_button.set_label(new_version)
        self._version_button.set_visible(True)
