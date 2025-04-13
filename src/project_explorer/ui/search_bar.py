"""UI code for a query search"""

from collections.abc import Callable
from typing import Any

from tkinter import (
    Frame,
    Entry,
    Button,
)

from project_explorer.utility.typing import copy_method_params

from project_explorer.data.query import Query, parse_query, InvalidQuery


# pylint: disable=too-few-public-methods
class SearchBar(Frame):
    """UI element which allows the user to specify a search query"""

    @copy_method_params(Frame.__init__)
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        self.callbacks: list[Callable[[Query | None, bool], Any]] = []

        self.search_var = Entry(self)
        self.search_var.pack(side="left", expand=True, fill="x")
        self.search_var.bind("<Return>", self._trigger_search)

        self.search_button = Button(self, text="Search", command=self._trigger_search)
        self.search_button.pack(side="left")

        self.refresh_button = Button(
            self, text="Refresh", command=self._trigger_refresh
        )
        self.refresh_button.pack(side="left")

    def on_action_required(self, callback: Callable[[Query | None, bool], Any]) -> None:
        """Add a callback to trigger when the user confirms some action within the search bar"""
        self.callbacks.append(callback)

    def _query_or_none(self) -> Query | None:
        result = parse_query(self.search_var.get())

        if isinstance(result, InvalidQuery):
            return None

        return result

    def _trigger_search(self, *_: Any) -> None:
        for callback in self.callbacks:
            callback(self._query_or_none(), False)

    def _trigger_refresh(self, *_: Any) -> None:
        for callback in self.callbacks:
            callback(self._query_or_none(), True)
