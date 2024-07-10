"""A class to manage configuration settings for the game."""

from __future__ import annotations

import json
import os.path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import MutableMapping
    from typing import Any


class Configs:
    """A class to manage configuration settings for the game."""

    _configs: MutableMapping[str, Any] = {}
    _path: str = ""

    @classmethod
    def set_path(cls, path: str) -> None:
        """Set the path to the configuration file.

        Args:
            path (str): The path to the configuration file.

        Raises:
            FileNotFoundError: If the file does not exist.
        """
        if not os.path.isfile(path):
            raise FileNotFoundError(f"File not found: {path}")
        cls._path = path

    @classmethod
    def load(cls) -> None:
        """Load the configuration settings from the file."""
        with open(cls._path, "r", encoding="utf-8") as f:
            cls._configs.clear()
            cls._configs.update(json.load(f))

    @classmethod
    def save(cls) -> None:
        """Save the configuration settings to the file."""
        with open(cls._path, "w", encoding="utf-8") as f:
            json.dump(cls._configs, f, indent=4)

    def __getitem__(self, key: str) -> Any:
        return self._configs[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self._configs[key] = value
