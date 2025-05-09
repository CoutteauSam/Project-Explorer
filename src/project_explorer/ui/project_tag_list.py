from typing import Any
import hashlib

from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QScrollArea,
    QFrame,
    QSizePolicy,
)

from PySide6.QtGui import  QEnterEvent, QPalette, QColor
from PySide6.QtCore import Qt, QEvent

from project_explorer.utility.typing import copy_method_params

from project_explorer.ui.flow_layout import FlowLayout

def color_for_string(text: str, dark_mode: bool = True):
    hash_bytes = hashlib.md5(text.encode('utf-8')).digest()
    seed = int.from_bytes(hash_bytes, 'big')

    one, two = (seed & 2**8 - 1) / 2**8, ( (seed >> 8 ) & 2**8 - 1) / 2**8 

    h = int(255 * one)
    s = int(255* two)
    l = 100 if dark_mode else 230

    return f"hsl( {h},{s},{l} )"

class ProjectTagList(QScrollArea):
    @copy_method_params(QScrollArea.__init__)
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        # Tag scroll area
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._collapse()

        self.setWidgetResizable(True)
        pal = QPalette()
        pal.setColor(QPalette.ColorRole.Window, "#00000000")
        self.setPalette(pal)
        self.setFrameShape(QFrame.Shape.NoFrame)

        # Tag container
        self.tag_container = QWidget()
        self.tag_container.setPalette(pal)
        self.tag_layout = FlowLayout(self.tag_container)
        self.tag_layout.setContentsMargins(5, 0, 5, 0)
        self.tag_layout.setSpacing(4)

        self.setWidget(self.tag_container)

    def set_tags(self, tags: list[str]) -> None:
        layout = self.tag_layout

        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        for tag in tags:
            label = QLabel(tag)
            label.setStyleSheet(
                f"background-color: {color_for_string(tag)}; padding: 2px 6px; border-radius: 10px;"
            )
            self.tag_layout.addWidget(label)

    def enterEvent(self, event: QEnterEvent) -> None:
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.verticalScrollBar().setEnabled(True)
        self.setMaximumHeight(200)
        return super().enterEvent(event)

    def _collapse(self) -> None:
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.verticalScrollBar().setEnabled(False)
        self.setMaximumHeight(24)
        self.verticalScrollBar().setValue(0)

    def leaveEvent(self, event: QEvent) -> None:
        self._collapse()
        return super().leaveEvent(event)


