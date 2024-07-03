"""Overlord, who oversees atron drones and assigns tasks to them."""

from __future__ import annotations

from queue import PriorityQueue, SimpleQueue
from typing import TYPE_CHECKING

from utils import Context, Icon
from utils.configs import Configs

from .atron import Atron
from .drones import Drone

if TYPE_CHECKING:
    from collections.abc import (
        Iterable,
        MutableMapping,
        MutableSequence,
        MutableSet,
    )

    from utils import Coordinate, MapData


_NODE_WEIGHTS = {
    Icon.EMPTY: 1,
    Icon.ATRON: 1,
    Icon.DEPLOY_ZONE: 1,
    Icon.ACID: 10,
    None: 1,
}


class Overlord(Atron):
    """Overlord, who oversees atron drones and assigns tasks to them."""

    def __init__(self) -> None:
        """Initialize the Overlord."""
        super().__init__(Configs()["StartingOverlordHealth"])
        self._drones: MutableMapping[int, Drone] = {}

        self._idle_drones: MutableSet[Drone] = set()
        self._update_queue: SimpleQueue[tuple[MapData, Drone, Context]] = (
            SimpleQueue()
        )
        # a queue of map updates from drones

        self._pickup_queue: SimpleQueue[tuple[MapData, Drone]] = SimpleQueue()
        # a queue of pick up requests from drones

        self._mad_data: MapData | None = None
        # the current mining map
        self._untasked_minerals: MutableSet[Coordinate] = set()
        # a set of the coords of untasked minerals
        self._tasked_minerals: MutableSet[Coordinate] = set()
        # a set of the coords of tasked minerals

    @property
    def icon(self) -> Icon:
        """The icon of this drone type."""
        return Icon.DEPLOY_ZONE

    @property
    def drones(self) -> MutableMapping[int, Drone]:
        """The drones under the overlord's control.

        The key is the drone's id and the value is the drone itself.
        """
        return self._drones

    def order_drones(self) -> str:
        """Give orders to the drones.

        Makes decisions on what tasks to assign to drones. If the overlord
        decides to deploy or retrieve a drone, it will return the action
        for the drone to perform. Otherwise, it will return an empty string.


        Returns:
            str: The action for the overlord to perform.
        """
        return ""

    def _task_miner(self, miner: Drone) -> None:
        """Task the miner with mining an available mineral.

        The miner will have their path variable set, and the mineral
        they are tasked with will be removed from the untasked_minerals
        set.

        Args:
            miner (Drone): The miner to task.
        """
        if not self._mad_data:
            raise ValueError("Overlord not on map")

        mineral = self._untasked_minerals.pop()
        self._tasked_minerals.add(mineral)
        miner.path = self._dijkstra(self._mad_data.landing_zone, mineral)

    def _dijkstra(
        self, start: Coordinate, end: Coordinate
    ) -> MutableSequence[Coordinate]:
        """Apply Dijkstra's Algorithm to find a path between two points.

        Args:
            start (Coordinate): The start point for the search
            end (Coordinate): The end point for the search
        Returns:
            list[Coordinate]: Path in the form of a Coordinate list
        """
        visited: MutableSet[Coordinate] = set()
        parents_map: MutableMapping[Coordinate, Coordinate] = {}
        path_found = False
        pqueue: PriorityQueue[tuple[int, Coordinate]] = PriorityQueue()
        pqueue.put((0, start))
        while not pqueue.empty():
            _, node = pqueue.get()
            if node in visited:
                continue
            if node == end:
                path_found = True
                break

            neighbors = node.cardinals()
            if end in neighbors:
                path_found = True
                parents_map[end] = node
                break

            visited.add(node)
            neighbors_gen = (
                neighbor for neighbor in neighbors if neighbor not in visited
            )
            self._add_to_path(
                node,
                neighbors_gen,
                parents_map,
                pqueue,
            )
        return (
            self._build_final_path(start, end, parents_map)
            if path_found
            else []
        )

    def _track_mineral(self, icon: Icon, coordinate: Coordinate) -> None:
        """Track the mineral at the given coordinates.

        Args:
            icon (Icon): The icon of the mineral.
            coordinate (Coordinate): The coordinates of the mineral.
        """
        if icon == Icon.MINERAL and coordinate not in self._tasked_minerals:
            self._untasked_minerals.add(coordinate)

    def _add_to_path(
        self,
        node: Coordinate,
        neighbors: Iterable[Coordinate],
        parents_map: MutableMapping[Coordinate, Coordinate],
        pqueue: PriorityQueue[tuple[int, Coordinate]],
    ) -> None:
        """Add neighbors to the path.

        Args:
            node (Coordinate): Starting node.
            neighbors (Iterable[Coordinate]): Neighbors of the node.
            parents_map (MutableMapping[Coordinate, Coordinate]): Map of path.
            pqueue (PriorityQueue[tuple[int, Coordinate]]): Final path.
        """
        if not self._mad_data:
            raise ValueError("Overlord not on map")

        for neighbor_coord in neighbors:
            if (neighbor := self._mad_data.get(neighbor_coord, None)) is None:
                # tile not in map
                continue
            if neighbor.surface and neighbor.surface not in _NODE_WEIGHTS:
                # tile not pathable
                continue
            parents_map[neighbor.coordinate] = node
            pqueue.put((_NODE_WEIGHTS[neighbor.surface], neighbor.coordinate))

    @staticmethod
    def _build_final_path(
        start: Coordinate,
        end: Coordinate,
        parents_map: MutableMapping[Coordinate, Coordinate],
    ) -> MutableSequence[Coordinate]:
        """Build the final path from start to end.

        Args:
            start (Coordinate): The starting point.
            end (Coordinate): The ending point.
            parents_map (MutableMapping[Coordinate, Coordinate]): The path.

        Returns:
            MutableSequence[Coordinate]: The final path.
        """
        curr = end
        final_path: list[Coordinate] = [end]
        while curr != start:
            coord = parents_map[curr]
            final_path.append(coord)
            curr = coord
            if start in coord.cardinals():
                break
        final_path.append(start)
        final_path = final_path[::-1]
        return final_path
