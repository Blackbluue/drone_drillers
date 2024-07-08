"""Store game data."""

from __future__ import annotations

from typing import TYPE_CHECKING

from units.ally.home_base import HomeBase
from units.ally.player import Player
from utils.configs import Configs
from utils.counter import Counter

if TYPE_CHECKING:
    from collections.abc import Mapping
    from tkinter import Tk

    from units.ally.atron import Atron
    from units.ally.drones.drone import Drone
    from utils.map_data import MapData


class GameData:
    """Store game data."""

    def __init__(self, root_window: Tk) -> None:
        configs = Configs()
        self._current_map: MapData | None = None
        self._player = Player(root_window)
        self._home_base = HomeBase()
        self._drones = self._home_base.drones
        self._total_refined = Counter(value=configs["StartingRefinedMinerals"])
        self._total_unrefined = Counter(value=0)

    @property
    def player(self) -> Player:
        """The player."""
        return self._player

    @property
    def current_map(self) -> MapData | None:
        """The current mining map."""
        return self._current_map

    @property
    def home_base(self) -> HomeBase:
        """The overlord."""
        return self._home_base

    @property
    def drones(self) -> Mapping[int, Drone]:
        """The drones."""
        return self._drones

    @property
    def total_unrefined(self) -> Counter:
        """The total unrefined minerals."""
        return self._total_unrefined

    @property
    def total_refined(self) -> Counter:
        """The total refined minerals."""
        return self._total_refined

    def set_current_map(self, map_data: MapData) -> None:
        """Set the mining map.

        Args:
            map_data (MapData): The map data.
        """
        self._current_map = map_data
        self._home_base.deploy(self._current_map)
        self._player.deploy(map_data)
        self._player.health.reset()

    def finish_excavation(self) -> None:
        """Finish the excavation on the current map."""
        if self._current_map is None:
            return

        self._total_refined.count(self._total_unrefined.get())
        self._total_unrefined.reset()
        self._player.undeploy()
        self._current_map = None

    def collect_minerals(self, atron: Atron) -> None:
        """Extract the minerals from the player."""
        self._total_unrefined.count(atron.extract_minerals())
