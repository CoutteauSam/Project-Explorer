from typing import Any
import math
from itertools import batched

from PySide6.QtWidgets import QWidget, QLayout, QSizePolicy, QLayoutItem, QWidgetItem

from PySide6.QtCore import Qt, QMargins, QPoint, QRect, QSize


from project_explorer.ui.layout.linear_layout import LinearLayout


class DynamicGridLayout(LinearLayout):
    desired_cell_size = 250

    def expandingDirections(self) -> Qt.Orientation:
        return Qt.Orientation(0)

    def hasHeightForWidth(self) -> bool:
        return True

    def heightForWidth(self, width: int) -> int:
        columns = self._column_count(width)

        rows = math.ceil( self.count() / columns )
        cell_size = width // columns

        return int( rows * cell_size )

    def setGeometry(self, rect: QRect) -> None:
        super().setGeometry(rect)
        self._do_layout(rect)

    def sizeHint(self) -> QSize:
        return self.minimumSize()

    def minimumSize(self) -> QSize:
        size = QSize(self.desired_cell_size,self.desired_cell_size)

        size += QSize(
            2 * self.contentsMargins().top(), 2 * self.contentsMargins().top()
        )

        return size

    def _column_count(self, width:int)->int:
        base_size = self.desired_cell_size + self.spacing()

        a = int( math.floor(width / base_size) )
        f = width / base_size - a
        c = a + ( 1 if f > a / ( 2 * a  + 1 ) else 0 )

        return c

    def _do_layout(self, rect: QRect):
        x0 = rect.x()
        y = rect.y()

        spacing = self.spacing()

        columns = self._column_count(rect.width())
        cell_size = rect.width() // columns

        for row in batched( self.get_items(), columns ):
            x = x0

            for item in row:
                rect = QRect(QPoint(x, y), QSize(cell_size,cell_size))
                rect = rect.marginsRemoved(QMargins(spacing//2,spacing//2,spacing//2,spacing//2))
                item.setGeometry(rect)
                x += cell_size

            y += cell_size
