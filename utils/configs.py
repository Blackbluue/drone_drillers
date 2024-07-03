from __future__ import annotations

import json
import os.path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import MutableMapping
    from typing import Any


class Configs:
    _configs: MutableMapping[str, Any] = {}
    _path: str = ""

    @classmethod
    def set_path(cls, path: str) -> None:
        if not os.path.isfile(path):
            raise FileNotFoundError(f"File not found: {path}")
        cls._path = path

    @classmethod
    def load(cls) -> None:
        with open(cls._path, "r") as f:
            cls._configs.clear()
            cls._configs.update(json.load(f))

    @classmethod
    def save(cls) -> None:
        with open(cls._path, "w") as f:
            json.dump(cls._configs, f, indent=4, sort_keys=True)

    def __getitem__(self, key: str) -> Any:
        return self._configs[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self._configs[key] = value
