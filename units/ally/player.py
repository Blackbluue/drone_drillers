"""Player unit class."""

from __future__ import annotations

from typing import TYPE_CHECKING

from units.ally.atron import Atron
from utils import Icon
from utils.configs import Configs
from utils.directions import Directions

if TYPE_CHECKING:
    from tkinter import Event, Tk

    from utils.map_data import MapData


class Player(Atron):
    """Player unit class."""

    def __init__(self, root_window: Tk) -> None:
        configs = Configs()
        super().__init__(
            configs["StartingPlayerHealth"], configs["StartingPlayerCapacity"]
        )
        self._window: Tk = root_window
        self._map_data: MapData | None = None
        self._l_bind: str | None = None
        self._r_bind: str | None = None
        self._u_bind: str | None = None
        self._d_bind: str | None = None
        self._s_bind: str | None = None

    @property
    def icon(self) -> Icon:
        """The icon of the player."""
        return Icon.PLAYER

    def deploy(self, map_data: MapData) -> None:
        """Deploy the player on the map.

        Args:
            map_data (MapData): The map to deploy the player on.
        """
        super().deploy(map_data)
        self._map_data = map_data
        self.set_controls()

    def undeploy(self) -> int:
        """Retrieve the player from the map."""
        payload = super().undeploy()
        self.unset_controls()
        self._map_data = None
        return payload

    def move_player(self, event: Event) -> None:
        """Move the player on the map.

        Args:
            event (Event): The event that triggered the player movement.
        """
        if self._map_data is None:
            return

        match event.keysym:
            case "Left":
                direction = Directions.WEST
            case "Right":
                direction = Directions.EAST
            case "Up":
                direction = Directions.NORTH
            case "Down":
                direction = Directions.SOUTH
            case "Shift_L":
                direction = Directions.CENTER
            case _:
                return  # Ignore other keys
        if direction is not Directions.CENTER:
            new_location = self.context.center.coordinate.translate_one(
                direction
            )
            self._map_data.move_to(self, new_location)
        curr_spot = self.context.center.terrain
        if health_adjust := curr_spot.health_cost():
            self.health.count(health_adjust)
            if self.health.get() <= 0:
                self._window.event_generate("<<PlayerDied>>")
                return
        if curr_spot == Icon.DEPLOY_ZONE:
            self._window.event_generate("<<PlayerReturned>>")
        else:
            self._window.event_generate("<<PlayerMoved>>")

    def set_controls(self) -> None:
        """Set the controls for the player."""
        if self._l_bind is None:
            self._l_bind = self._window.bind(
                "<Left>", self.move_player, add=True
            )
        if self._r_bind is None:
            self._r_bind = self._window.bind(
                "<Right>", self.move_player, add=True
            )
        if self._u_bind is None:
            self._u_bind = self._window.bind(
                "<Up>", self.move_player, add=True
            )
        if self._d_bind is None:
            self._d_bind = self._window.bind(
                "<Down>", self.move_player, add=True
            )
        if self._s_bind is None:
            self._s_bind = self._window.bind(
                "<Shift_L>", self.move_player, add=True
            )

    def unset_controls(self) -> None:
        """Unset the controls for the player."""
        if self._l_bind is not None:
            self._window.unbind("<Left>", self._l_bind)
            self._l_bind = None
        if self._r_bind is not None:
            self._window.unbind("<Right>", self._r_bind)
            self._r_bind = None
        if self._u_bind is not None:
            self._window.unbind("<Up>", self._u_bind)
            self._u_bind = None
        if self._d_bind is not None:
            self._window.unbind("<Down>", self._d_bind)
            self._d_bind = None
        if self._s_bind is not None:
            self._window.unbind("<Down>", self._s_bind)
            self._s_bind = None
