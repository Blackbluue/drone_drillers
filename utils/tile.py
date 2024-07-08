"""A single tile on the map."""

from __future__ import annotations

from tkinter import BooleanVar
from typing import TYPE_CHECKING

from .icon import Icon
from .icon_var import IconVar

if TYPE_CHECKING:
    from units.ally.atron import Atron

    from .coordinate import Coordinate


class Tile:
    """A single tile on the map."""

    def __init__(
        self,
        coordinate: Coordinate,
        surface: Icon = Icon.EMPTY,
        terrain: Icon = Icon.EMPTY,
    ) -> None:
        """Initialize the tile.

        Args:
            coordinate (Coordinate): The coordinate of this tile.
            icon (Icon): The icon on this tile.
        """
        self._coordinate = coordinate
        self._surface = IconVar(value=surface)
        self._terrain = IconVar(value=terrain)
        self._discovered = BooleanVar(value=False)
        self._occupation: Atron | None = None

    @property
    def coordinate(self) -> Coordinate:
        """The coordinates of this tile on the map."""
        return self._coordinate

    @property
    def surface(self) -> Icon:
        """The surface icon for this tile.

        The surface icon will always be visible on the map.

        If the new icon is traversable, setting the surface icon will also set
        the terrain icon to the same icon.
        """
        return self._surface.get()

    @surface.setter
    def surface(self, icon: Icon) -> None:
        self._surface.set(icon)

    @property
    def surface_var(self) -> IconVar:
        """The surface icon variable for this tile."""
        return self._surface

    @property
    def terrain(self) -> Icon:
        """The terrain of this tile.

        The terrain is different from the tile surface icon, in that it is the
        underlying icon of the tile, and not the icon that is currently
        displayed on the tile.
        """
        return self._terrain.get()

    @terrain.setter
    def terrain(self, icon: Icon) -> None:
        self._terrain.set(icon)

    @property
    def discovered(self) -> BooleanVar:
        """The discovered status of the tile.

        An undiscovered tile cannot be occupied, and will not show on the map.
        """
        return self._discovered

    @property
    def occupied_drone(self) -> Atron | None:
        """The atron occupying this tile, which may be None."""
        return self._occupation

    def clear_surface(self) -> None:
        """Clear the surface icon of this tile."""
        self._surface.set(self._terrain.get())

    def occupy(self, atron: Atron) -> bool:
        """Occupy this tile with an atron.

        An occupied tile will return an atron icon for the icon property. An
        occupied tile will remember the icon that was on it before the atron
        occupied it. Trying to occupy a tile that is already occupied, or has
        a wall or mineral icon will fail. An undiscovered tile cannot be
        occupied. Trying to occupy an undiscovered tile will raise an exception

        Raises:
            RuntimeError: If the tile is undiscovered, and therefore cannot
                be occupied.

        Returns:
            bool: Whether occupation of the tile succeeded.
        """
        if not self.discovered:
            raise RuntimeError("An undiscovered tile cannot be occupied")
        if not self.surface.traversable():
            return False
        self._occupation = atron
        self._surface.set(atron.icon)
        return True

    def unoccupy(self) -> bool:
        """Unoccupy this tile with an atron.

        Unoccupying a tile will cause the original icon on the tile to returned
        by the icon property. Trying to unoccupy a tile that was not unoccupied
        will fail with no operation happening. Trying to unoccupy an
        undiscovered tile will raise an exception.

        Raised:
            RuntimeError: If the tile is undiscovered, and therefor cannot be
                unoccupied.

        Returns:
            bool: Whether the tile was able to be unoccupied.
        """
        if not self.discovered:
            raise RuntimeError("An undiscovered tile cannot be unoccupied")
        if not self._occupation:
            return False
        self._occupation = None
        self._surface.set(self._terrain.get())
        return True

    def __eq__(self, __o):
        """Compare if this object is equal to the other object.

        Args:
            __o : The other object.

        Returns:
            bool: If this object is equal to the other object
        """
        return (
            self._coordinate == __o._coordinate
            if isinstance(__o, Tile)
            else NotImplemented
        )

    def __lt__(self, __o):
        # it isn't actually sensible to ever see if a tile is 'less
        # than' another tile, but the built-in pqueue requires it
        # in the case that two priority values in the queue are the
        # same upon insertion.
        coord = self.coordinate
        other_coord = __o.coordinate
        return (
            self
            if abs(coord.x + coord.y) < abs(other_coord.x + other_coord.y)
            else __o
        )

    def __str__(self) -> str:
        icon_msg = (
            f"Icon: {self.surface.value}" if self.surface else "Undiscovered"
        )
        return f"Tile({self.coordinate}, {icon_msg})"

    def __repr__(self) -> str:
        return f"Tile({self.coordinate}, {self.surface})"

    def __hash__(self) -> int:
        """The hash value of this object.

        Returns:
            int: This object's hash value.
        """
        return hash(self.coordinate)
