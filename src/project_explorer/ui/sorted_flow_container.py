from typing import Generic, TypeVar
from collections.abc import Generator

import sys
from bisect import bisect_left

from sortedcontainers import SortedDict

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QApplication, QWidgetItem

from project_explorer.utility.typing import copy_method_params

from project_explorer.ui.flow_layout import FlowLayout

Key = TypeVar("Key")

class SortedFlowContainer(QWidget,Generic[Key]):
    _elements: SortedDict[Key, QWidget]

    @copy_method_params(QWidget.__init__)
    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)

        self._elements = SortedDict()

        self._layout = FlowLayout(self)
    
    def insert( self, key: Key, widget: QWidget ) -> None:
        if key in self._elements:
            return

        insertion_index = self._elements.bisect_right(key)

        self._layout.insertWidget(insertion_index,widget)

        self._elements[key] = widget

    def remove( self, key: Key )->None:
        if key not in self._elements:
            return
        
        deletion_index = self._elements.index(key)

        self._layout.takeAt(deletion_index)

    def clear_all(self)->None:
        while self._layout.count():
            child = self._layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def widgets(self)->Generator[QWidget,None,None]:
        yield from self._elements.values()




