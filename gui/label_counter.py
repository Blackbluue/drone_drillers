"""A labeled counter widget."""

from __future__ import annotations

import tkinter as tk

from utils.counter import Counter


class LabeledCounter(tk.Frame):
    """A labeled counter widget."""

    def __init__(
        self,
        owner: tk.Misc,
        label: str,
        counter: Counter,
    ) -> None:
        """Create a labeled counter.

        Args:
            owner (tk.Misc): The owner of the counter.
            label (str): The label to put on the counter.
            counter (Counter): The counter to use.
        """
        super().__init__(owner)

        self._counter = counter

        self._text_label = tk.Label(self, text=f"{label}")
        self._text_label.pack(side=tk.LEFT)

        self._counter_label = tk.Label(self, textvariable=self._counter)
        self._counter_label.pack(side=tk.RIGHT)

    @property
    def counter(self) -> Counter:
        """Return the counter."""
        return self._counter
