"""A map made up of tiles."""

from __future__ import annotations

from random import randint, uniform
from typing import TYPE_CHECKING

from utils.configs import Configs

from .context import Context
from .coordinate import Coordinate
from .directions import Directions
from .icon import Icon
from .tile import Tile

if TYPE_CHECKING:
    from collections.abc import (
        Iterable,
        Iterator,
        MutableMapping,
        MutableSequence,
        Sequence,
    )

    from units.ally.atron import Atron
    from units.ally.drones import Drone

DEFAULT_LANDING_ZONE = Coordinate(-1, -1)


class MapData:
    """A map object, used to describe the tile layout of an area."""

    def __init__(self, map_file: str | None) -> None:
        """Initialize a Map object."""
        self._configs = Configs()
        self._width = 0
        self._height = 0
        self._landing_zone: Coordinate = DEFAULT_LANDING_ZONE
        self._all_tiles: list[MutableSequence[Tile]] = []
        self._total_minerals: MutableMapping[Coordinate, int] = {}
        self._acid: MutableSequence[Coordinate] = []
        if map_file:
            self._with_file(map_file)
        else:
            self._no_file(
                randint(
                    self._configs["MinimumRandomMapDimension"],
                    self._configs["MaximumRandomMapDimension"],
                ),
                randint(
                    self._configs["MinimumRandomMapDimension"],
                    self._configs["MaximumRandomMapDimension"],
                ),
                uniform(
                    self._configs["MinimumMineralDensity"],
                    self._configs["MaximumMineralDensity"],
                ),
            )

    @property
    def landing_zone(self) -> Coordinate:
        """The landing zone for drones."""
        return self._landing_zone

    def _with_file(self, filename: str) -> MapData:
        """Read a map from a file.

        Args:
            filename (str): The name of the file to read.

        Returns:
            MapData: The map object.
        """
        with open(filename, encoding="utf-8") as file_handle:
            for row, line in enumerate(file_handle):
                self._height += 1
                destination = list(line.rstrip())
                cur_width = 0
                tile_row: MutableSequence[Tile] = []
                for column, char in enumerate(destination):
                    cur_width += 1
                    coord = Coordinate(column, row)
                    icon = Icon.MINERAL if char.isdigit() else Icon(char)
                    match icon:
                        case Icon.ACID:
                            self._acid.append(coord)
                        case Icon.DEPLOY_ZONE:
                            self._landing_zone = coord
                        case Icon.MINERAL:
                            self._total_minerals[coord] = int(char)
                    tile_row.append(Tile(coord, icon))
                self._width = max(self._width, cur_width)

                self._all_tiles.append(tile_row)

        return self

    def _no_file(self, width: int, height: int, density: float) -> MapData:
        """Create a map from scratch.

        Args:
            width (int): The width of the map.
            height (int): The height of the map.
            density (float): The density of minerals in the map.

        Returns:
            MapData: The map object.
        """
        self._create_box(width, height)

        self._landing_zone = self._get_rand_coords()
        self[self._landing_zone] = Icon.DEPLOY_ZONE

        wall_count = ((width * 2) + (height * 2)) - 4
        total_coordinates = self._width * self._height
        total_minerals = int(density * (total_coordinates - wall_count))
        for _ in range(total_minerals):
            self._add_mineral()

        total_acid = int(
            self._configs["MaximumAcidDensity"]
            * (total_coordinates - len(self._total_minerals) - wall_count)
        )
        for _ in range(total_acid):
            self._add_acid()
        return self

    def get(self, key: Coordinate, default: Tile | None) -> Tile | None:
        """Get the tile with the specified coordinates from the map.

        Args:
            key (Coordinate): The key to look up.
            default (Tile, optional): A value to return if the
                key is not found. Defaults to None.

        Returns:
            Tile | None: The Tile within this map, or the default value if not found.
        """
        try:
            return self[key]
        except KeyError:
            return default

    def build_context(self, location: Coordinate) -> Context:
        """Build a context object for the given location.

        Args:
            location (Coordinate): The location to build the context for.

        Returns:
            Context: The context object.
        """
        cardinals = [
            *map(
                lambda coord: self[coord],
                location.cardinals(),
            )
        ]
        return Context(self[location], *cardinals)

    def get_unexplored_tiles(self) -> Sequence[Tile]:
        """Return a list of all unexplored tiles on the map.

        Returns:
            Sequence[Tile]: The unexplored tile list.
        """
        tiles: Sequence[Tile] = []
        for row in self._all_tiles:
            tiles.extend(
                list(filter(lambda tile: not tile.discovered.get(), row))
            )
        return tiles

    def get_explored_tiles(self) -> Sequence[Tile]:
        """Return a list of all explored tiles on the map.

        Returns:
            Sequence[Tile]: The explored tile list.
        """
        tiles: Sequence[Tile] = []
        for row in self._all_tiles:
            tiles.extend(list(filter(lambda tile: tile.discovered.get(), row)))
        return tiles

    def remove_atron(self, atron: Atron) -> int:
        """Removes atron from map and returns the mined minerals.

        Args:
            atron (Atron): The atron to be removed.

        Returns:
            int: The mined mineral count.
        """
        self._clear_tile(atron.context.center.coordinate)
        return atron.undeploy()

    def reveal_tile(self, coord: Coordinate) -> None:
        """Reveal a tile on the map.

        Args:
            coord (Coordinate): The coordinates of the tile to reveal.
        """
        if tile := self.get(coord, None):
            if not tile.discovered.get():
                tile.discovered.set(True)

    def deploy_atron(self, atron: Atron) -> None:
        """Add an atron to the map.

        The atron cannot be added to the map if the deploy zone is occupied.

        Args:
            atron (Atron): The atron to add to the map.
        """
        if self[self._landing_zone].surface != Icon.DEPLOY_ZONE:
            raise ValueError("Landing zone is occupied")

        atron.context = self.build_context(self._landing_zone)
        self[self._landing_zone].occupied_drone = atron
        self.reveal_tile(self._landing_zone)
        for coord in self._landing_zone.cardinals():
            self.reveal_tile(coord)

    def move_to(self, atron: Atron, new_location: Coordinate) -> None:
        """Move the atron in the given location.

        Checks if the location is traversable before moving. Also applies any
        other side effects from attempting to move to this tile.

        Args:
            atron (Atron): The atron to move.
            new_location (Coordinate): The new location to move the atron to.
        """
        new_icon = self[new_location].surface

        if new_icon.traversable():
            self._move_atron(atron, new_location)
        else:
            if health_adjust := new_icon.health_cost():
                atron.health.count(health_adjust)
            if new_icon == Icon.MINERAL:
                self._total_minerals[new_location] -= 1
                atron.payload.count(1)
                if self._total_minerals[new_location] <= 0:
                    self._clear_tile(new_location)
                    del self._total_minerals[new_location]

    def tick(self, drones: Iterable[Drone]) -> None:
        """Do one tick of the map."""
        for drone in drones:
            for _ in range(drone.moves):
                # acid damage is applied before movement
                if drone.context.center.coordinate in self._acid:
                    drone.health.count(Icon.ACID.health_cost())
                if drone.health.get() <= 0:
                    self._clear_tile(drone.context.center.coordinate)
                    drone.undeploy()  # mined minerals lost
                    break  # atron is dead move on to next

                direction = Directions(drone.action(drone.context))
                if direction != Directions.CENTER:
                    new_location = (
                        drone.context.center.coordinate.translate_one(
                            direction
                        )
                    )
                    self.move_to(drone, new_location)

    def _create_box(self, width: int, height: int) -> None:
        """Create a box around the map.

        This function is used to create a box around the map, with walls
        on the outer edges and empty space inside.

        Args:
            width (int): The width of the map.
            height (int): The height of the map.
        """
        self._width = width
        self._height = height

        for row in range(self._height):
            #  first/last columns are always a wall
            tile_row = [Tile(Coordinate(0, row), Icon.WALL)]
            for column in range(1, self._width - 1):
                coord = Coordinate(column, row)
                if row in [0, self._height - 1]:  # build top/bottom walls
                    tile_row.append(Tile(coord, Icon.WALL))
                else:  # build empty space between walls
                    tile_row.append(Tile(coord, Icon.EMPTY))
            tile_row.append(Tile(Coordinate(self._width - 1, row), Icon.WALL))

            self._all_tiles.append(tile_row)

    def _add_mineral(self) -> None:
        """Adds a single mineral deposit to a random open spot in the map."""
        coordinates = self._get_rand_coords()

        self[coordinates] = Icon.MINERAL
        self._total_minerals[coordinates] = randint(1, 9)

    def _add_acid(self) -> None:
        """Adds a single acid tile to a random open spot in the map."""
        coordinates = self._get_rand_coords()

        self[coordinates] = Icon.ACID
        self._acid.append(coordinates)

    def _get_rand_coords(self) -> Coordinate:
        """Get a random set of coordinates on the map.

        Returns:
            Coordinate: A set of coordinates on the map.
        """
        x_coords: int = self._width - 2
        y_coords: int = self._height - 2
        coordinates = Coordinate(0, 0)
        while self[coordinates].surface != Icon.EMPTY:
            # Choose a random location on map excluding walls
            coordinates = Coordinate(
                randint(1, x_coords),
                randint(1, y_coords),
            )
        return coordinates

    def _move_atron(self, atron: Atron, new_location: Coordinate) -> None:
        """Move the atron to the new traversable location.

        Args:
            atron (Atron): The atron to move.
            new_location (Coordinate): The new location to move the atron to.
        """
        self[atron.context.center.coordinate].occupied_drone = None
        self._clear_tile(atron.context.center.coordinate)
        self[new_location].occupied_drone = atron
        atron.context = self.build_context(new_location)
        self.reveal_tile(new_location)
        for coord in new_location.cardinals():
            self.reveal_tile(coord)

    def _clear_tile(self, pos: Coordinate) -> None:
        """Clear the tile at the given coordinates.

        Args:
            pos (Coordinate): The coordinates of the tile to update.
        """
        if pos == self._landing_zone:
            self[pos] = Icon.DEPLOY_ZONE
        elif pos in self._acid:
            self[pos] = Icon.ACID
        else:
            self[pos] = Icon.EMPTY

    def __getitem__(self, key: Coordinate) -> Tile:
        """Get the tile with the specified coordinates from the map.

        Args:
            key (Coordinate): The key to look up.

        Raises:
            KeyError: If no Tile with the given coordinates exists in this map.

        Returns:
            Tile: The Tile within this map.
        """
        return self._all_tiles[key.y][key.x]

    def __setitem__(self, coord: Coordinate, icon: Icon) -> None:
        """Set the actual icon of a tile at the given coordinates.

        Args:
            coord (Coordinate): The coordinates to set.
            icon (Icon): The icon to set.
        """
        self._all_tiles[coord.y][coord.x].surface = icon

    def __iter__(self) -> Iterator[Tile]:
        """Iterate over the visible tiles in this map.

        Yields:
            Iterator[Tile]: The visible tiles in this map.
        """
        for row in self._all_tiles:
            yield from row

    def __repr__(self) -> str:
        """Return a representation of this object.

        The string returned by this method is not valid for a call to eval.

        Returns:
            str: The string representation of this object.
        """
        return "\n".join(
            "".join([tile.surface.value for tile in row if tile.surface])
            for row in self._all_tiles
        )
