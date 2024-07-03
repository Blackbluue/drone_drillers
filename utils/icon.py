"""An icon on the map."""

from enum import Enum
from typing import Mapping


class Icon(Enum):
    """An icon on the map."""

    HOME_BASE = "_"
    ATRON = "A"
    SCOUT = "S"
    MINER = "M"
    PLAYER = "P"
    WALL = "#"
    MINERAL = "*"
    ACID = "~"
    EMPTY = " "
    UNKNOWN = "?"

    def traversable(self) -> bool:
        """Whether a tile with this icon is traversable by a drone.

        Returns:
            bool: True if traversable, else False.
        """
        return self in [Icon.HOME_BASE, Icon.ACID, Icon.EMPTY]

    def health_cost(self) -> int:
        """Return the health cost for traversing over this tile.

        Any tile that causes damage for traveling over it will return a
        negative number representing the health cost. Healing tiles will return
        a positive number representing the health cost.

        Returns:
            int: A number representing the health cost.
        """
        match self:
            case Icon.WALL:
                return -1
            case Icon.ACID:
                return -3
            case _:
                return 0

    def unicode(self) -> str:
        """Return the unicode representation of this icon.

        Returns:
            str: The icon as a unicode character.
        """
        return {
            Icon.HOME_BASE: "\u02c5",
            Icon.ATRON: "\u00C4",
            Icon.SCOUT: "\u00A7",
            Icon.MINER: "\u00A3",
            Icon.PLAYER: "\u20B1",
            Icon.WALL: "\u039E",
            Icon.MINERAL: "\u0275",
            Icon.ACID: "\u05e1",
            Icon.EMPTY: " ",
            Icon.UNKNOWN: "\u02D1",
        }[self]

    @classmethod
    def unicode_mappings(cls) -> Mapping[str, str]:
        """Return a mapping of Icon name to Icon unicode representation.

        Returns:
            Mapping[str, str]: The unicode mappings.
        """
        return {icon.name: icon.unicode() for icon in cls.__members__.values()}
