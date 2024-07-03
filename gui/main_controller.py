"""Main controller for the Atron Mining Expedition."""

from __future__ import annotations

import os
import random
import sys
import tkinter as tk

from gui.dashboard import Dashboard
from gui.graphic_tile import GraphicTile
from utils.configs import Configs
from utils.counter import Counter
from utils.game_data import GameData
from utils.map_data import MapData

NO_DELAY = 0


class MainController(tk.Tk):
    """Main game controller."""

    def __init__(self, map_dir: str | None) -> None:
        """Root window that contains fields for initial values.

        Args:
            map_dir (str | None): The directory containing the maps.
        """
        super().__init__()
        self.title("Atron Mining Expedition")
        self._initialize_values(map_dir)

    @property
    def delay(self) -> int:
        """The delay between ticks, in milliseconds.

        Setting the delay to non-zero causes the game to run in a loop. Set it
        back to 0 to return to manual play.
        """
        return self._delay

    @delay.setter
    def delay(self, value: int) -> None:
        if value < NO_DELAY:
            raise ValueError("Delay must be non-negative")
        if self._delay == NO_DELAY and value != NO_DELAY:
            self._delay = value
            self._game_data.player.unset_controls()
            self.event_generate("<<PlayerMoved>>")
        elif self._delay != NO_DELAY and value == NO_DELAY:
            self._delay = value
            self._game_data.player.set_controls()
        else:
            self._delay = value

    def _initialize_values(self, map_dir: str | None) -> None:
        """Initialize game values from the GUI.

        Args:
            map_dir (str | None): The directory containing the maps.
        """
        configs = Configs()
        self._ticks = Counter(
            value=configs["TicksPerMap"],
            max_value=configs["TicksPerMap"],
        )
        self._delay = NO_DELAY
        self._start_button = tk.Button(
            self, command=self._start_button_handler, text="Start"
        )

        self._game_data = GameData(self)
        self._map_dir: str | None = map_dir
        self._dashboard = Dashboard(
            self,
            self._game_data,
            self._ticks,
        )
        self._map_frame = tk.Frame(self)

        self._start_button.pack()
        self._map_frame.pack()
        self._dashboard.pack()

        self.bind("<<PlayerMoved>>", self._process_tick, add=True)
        self.bind("<<PlayerReturned>>", self._extract_player, add=True)
        self.bind("<<PlayerDied>>", self._player_died, add=True)

    def _start_button_handler(self) -> None:
        """Start the game."""
        self._game_data.player.undeploy()
        self._set_new_map()
        self._ticks.reset()

    def _process_tick(self, _) -> None:
        """Process a tick of the game."""
        if not (map_data := self._game_data.current_map):
            return

        home_base = self._game_data.home_base
        action, _, opts = home_base.order_drones().partition(" ")
        match action:
            case "RETURN":
                drone_id = next(map(int, opts.split()))
                home_base.drones[drone_id].undeploy()
            case "DEPLOY":
                drone_id, _ = map(int, opts.split())
                # check if drone is already deployed
                home_base.drones[drone_id].deploy(map_data)
            case "":
                pass  # Do nothing
            case _:  # Ignore other actions
                print(f"Unknown action: {action}", file=sys.stderr)

        deployed_drones = list(
            filter(lambda drone: drone.deployed, home_base.drones.values())
        )
        map_data.tick(deployed_drones)
        print(map_data, file=sys.stderr)
        self._ticks.count(-1)
        if self._ticks.get() == 0:
            self._game_data.finish_excavation()
        elif self._delay:
            self.after(
                self._delay, lambda: self.event_generate("<<PlayerMoved>>")
            )

    def _extract_player(self, _) -> None:
        """Extract the player from the map."""
        self._game_data.collect_minerals(self._game_data.player)
        self.event_generate("<<PlayerMoved>>")

    def _player_died(self, _) -> None:
        """Handle the player's death."""
        self._game_data.finish_excavation()

    def _set_new_map(self) -> None:
        """Set the mining map."""
        if self._map_dir:
            random_file = random.choice(os.listdir(self._map_dir))
            map_file = os.path.join(self._map_dir, random_file)
        else:
            map_file = None
        map_data = MapData(map_file)

        for widget in self._map_frame.winfo_children():
            widget.destroy()
        for tile in iter(map_data):
            GraphicTile(self._map_frame, tile)

        self._game_data.current_map = map_data
