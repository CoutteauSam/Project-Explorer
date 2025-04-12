"""UI code for a query search"""

from collections.abc import Callable
from typing import Any

from tkinter import (
    Frame,
    Entry,
    Button,
)


# pylint: disable=too-few-public-methods
class SearchBar:
    """UI element which allows the user to specify a search query"""

    def __init__(self, parent: Frame) -> None:
        self.parent = parent

        self.frame = Frame(self.parent)
        self.frame.pack(fill="x", expand=True)

        self.callbacks: list[Callable[[str, bool], Any]] = []

        self.search_var = Entry(self.frame)
        self.search_var.pack(side="left", expand=True, fill="x", padx=5, pady=5)
        self.search_var.bind("<Return>", self._trigger_search)

        self.search_button = Button(
            self.frame, text="Search", command=self._trigger_search
        )
        self.search_button.pack(side="left")

        self.refresh_button = Button(
            self.frame, text="Refresh", command=self._trigger_refresh
        )
        self.refresh_button.pack(side="left")

    def on_action_required(self, callback: Callable[[str, bool], Any]) -> None:
        """Add a callback to trigger when the user confirms some action within the search bar"""
        self.callbacks.append(callback)

    def _trigger_search(self, *_: Any) -> None:
        for callback in self.callbacks:
            callback(self.search_var.get(), False)

    def _trigger_refresh(self, *_: Any) -> None:
        for callback in self.callbacks:
            callback(self.search_var.get(), True)
