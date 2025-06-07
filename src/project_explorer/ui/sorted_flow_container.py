from typing import Generic, TypeVar, Any
from collections.abc import Generator

import sys
from bisect import bisect_left

from sortedcontainers import SortedDict

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QApplication,
    QWidgetItem,
)

from project_explorer.utility.typing import copy_method_params

from project_explorer.ui.layout.flow_layout import FlowLayout
from project_explorer.ui.layout.linear_layout import LinearLayout

Key = TypeVar("Key")


class SortedFlowContainer(QWidget, Generic[Key]):
    _elements: SortedDict[Key, QWidget]
    _layout: LinearLayout

    @copy_method_params(QWidget.__init__)
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        self._elements = SortedDict()

        if "layout" in kwargs:
            # Python type system is to ass to support this properly
            self._layout = kwargs["layout"]
            self.setLayout(self._layout)
        else:
            self._layout = FlowLayout(self)

    def has_element(self, key: Key) -> bool:
        return key in self._elements

    def insert(self, key: Key, widget: QWidget) -> None:
        if key in self._elements:
            return

        insertion_index = self._elements.bisect_right(key)

        self._layout.insertWidget(insertion_index, widget)

        self._elements[key] = widget

    def remove(self, key: Key) -> None:
        if key not in self._elements:
            return

        deletion_index = self._elements.index(key)

        self._layout.takeAt(deletion_index)
        self._elements.pop(key)

        self._layout.invalidate()

    def clear_all(self) -> None:
        self._elements.clear()
        while self._layout.count():
            child = self._layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def widgets(self) -> Generator[QWidget, None, None]:
        yield from self._elements.values()
