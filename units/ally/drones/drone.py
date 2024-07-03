"""Contains the Drone class and the drone State class"""

from __future__ import annotations

from abc import abstractmethod
from enum import Enum, auto
from typing import TYPE_CHECKING

from units.ally.atron import Atron
from utils.configs import Configs
from utils.context import Context
from utils.coordinate import Coordinate

if TYPE_CHECKING:
    from collections.abc import MutableSequence

    from units.ally.home_base import HomeBase


class Drone(Atron):
    """Parent class for all drone atron units."""

    def __init__(self, home_base: HomeBase) -> None:
        """Initialize a Drone."""
        configs = Configs()
        super().__init__(
            configs["StartingDroneHealth"], configs["StartingDroneCapacity"]
        )
        self._home_base = home_base
        self._moves = configs["StartingDroneMoves"]
        self._path_to_goal: MutableSequence[Coordinate] = []

    @property
    def moves(self) -> int:
        """The max moves this drone can take in 1 tick.

        Returns:
            int: The drone's max moves.
        """
        return self._moves

    @property
    def path(self) -> MutableSequence[Coordinate]:
        """The path this drone will take to its destination.

        The destination of this drone will always be the final element of this
        list. Setting the path implicitly sets the destination.
        """
        return self._path_to_goal

    @path.setter
    def path(self, new_path: MutableSequence[Coordinate]) -> None:
        self._path_to_goal = new_path
        self._path_traveled: MutableSequence[Coordinate] = []
        # traveling if path length is greater than 2 (start, dest)
        self.state = State.TRAVELING if len(new_path) > 2 else State.WAITING

    @abstractmethod
    def action(self, context: Context) -> str:
        """Perform some action, based on the type of drone.

        The drone will internally have it's own orders set by the home base.
        These orders may take the context into account.

        Args:
            context (Context): The context surrounding the drone.

        Returns:
            str: The action the drone wants to take.
        """
        raise NotImplementedError("Drone subtypes must implement action")


class State(Enum):
    """States that an atron Drone can be in."""

    TRAVELING = auto()
    WORKING = auto()
    WAITING = auto()
    REVERSING = auto()
