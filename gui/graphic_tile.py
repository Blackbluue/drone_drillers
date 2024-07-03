"""Graphical representation of a tile on the map."""

from __future__ import annotations

from tkinter import Label
from typing import TYPE_CHECKING

from utils.icon import Icon
from utils.icon_var import IconVar

if TYPE_CHECKING:
    from tkinter import Frame

    from utils.tile import Tile


class GraphicTile(Label):
    """Graphical representation of a tile on the map."""

    def __init__(self, master: Frame, tile: Tile) -> None:
        """Initialize the tile.

        Args:
            master: The parent widget.
            tile (Tile): The Tile.
        """
        super().__init__(master)
        self._map_frame = master
        self._tile = tile
        self._visible_icon = IconVar(master=self)
        self["textvariable"] = self._visible_icon
        tile.surface_var.trace_add("write", self._update_tile)
        tile.discovered.trace_add("write", self._update_tile)
        self["width"] = 1
        self["relief"] = "raised"
        self.grid(row=tile.coordinate.y, column=tile.coordinate.x)

    def _update_tile(self, *_) -> None:
        """Change the tile icon."""
        if self._tile.discovered.get():
            self._visible_icon.set(self._tile.surface)
            self["bg"] = "white"
        else:
            self._visible_icon.set(Icon.UNKNOWN)
            self["bg"] = "grey"
