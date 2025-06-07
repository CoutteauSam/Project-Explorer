from typing import Any, Generator

from PySide6.QtWidgets import QWidget, QLayout, QSizePolicy, QLayoutItem, QWidgetItem

from PySide6.QtCore import Qt, QMargins, QPoint, QRect, QSize

from project_explorer.utility.typing import copy_method_params


class LinearLayout(QLayout):
    @copy_method_params(QLayout.__init__)
    def __init__(self, parent: QWidget | None, *args: Any, **kwargs: Any) -> None:
        self._item_list: list[QLayoutItem] = []
        
        super().__init__(parent, *args, **kwargs)

        if parent is not None:
            self.setContentsMargins(QMargins(0, 0, 0, 0))


    def get_items(self)->Generator[QLayoutItem,None,None]:
        yield from self._item_list

    def __del__(self) -> None:
        while self.count():
            self.takeAt(0)

    def insertItem(self, index: int, item: QLayoutItem) -> None:
        self._item_list.insert(index, item)

    def addItem(self, item: QLayoutItem) -> None:
        self._item_list.append(item)

    def insertWidget(self, index: int, widget: QWidget) -> None:
        self.addChildWidget(widget)
        self.insertItem(index, QWidgetItem(widget))

    def count(self) -> int:
        return len(self._item_list)

    def itemAt(self, index: int) -> QLayoutItem | None:
        if 0 <= index < len(self._item_list):
            return self._item_list[index]

        return None

    def takeAt(self, index: int) -> QLayoutItem:
        if 0 <= index < len(self._item_list):
            return self._item_list.pop(index)

        raise ValueError("invalid index")
