#!/usr/bin/env python3
"""Starting point for the game."""


import argparse
import os.path
import sys
from contextlib import suppress

from gui.main_controller import MainController
from utils.configs import Configs


def get_args() -> argparse.Namespace:
    """Get command line arguments."""
    parser = argparse.ArgumentParser(description="Atron Mining Expedition")
    # command line arguments are for testing. eventually will move these
    # to a configuration file
    parser.add_argument(
        "map_directory",
        metavar="map_directory",
        type=str,
        nargs="?",
        help="Directory to find map files",
    )
    args = parser.parse_args()
    if args.map_directory and not os.path.isdir(args.map_directory):
        parser.error(f"Map directory {args.map_directory} does not exist")
    return args


def main() -> None:
    """Collect settings from the command line and start the game."""
    args = get_args()
    map_directory: str | None = args.map_directory
    Configs.set_path("./resources/config.json")
    Configs.load()
    MainController(map_directory).mainloop()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt as e:
        print(f"Exiting due to interrupt: {e}", file=sys.stderr)
    finally:
        with suppress(OSError):
            Configs.save()
