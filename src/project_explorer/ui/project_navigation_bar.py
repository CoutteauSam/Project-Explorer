from typing import Any
from pathlib import Path

from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QSizePolicy, QLabel

from PySide6.QtGui import QPixmap, QPalette, QIcon
from PySide6.QtCore import Qt

from project_explorer.utility.typing import copy_method_params

from project_explorer.assets import (
    chevron_left,
    chevron_right,
    open_in,
    edit,
    reload,
    error,
)


class ProjectNavigationBar(QWidget):
    @copy_method_params(QWidget.__init__)
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        self.setStyleSheet(
            """QPushButton { 
                background-color: #00000000;
                border-radius: 10px;
            } 
            QPushButton:hover { 
                background-color: #333333;
            }
            """
        )
        pal = QPalette()
        pal.setColor(QPalette.ColorRole.Window, "#CC555555")
        self.setPalette(pal)
        self.setAutoFillBackground(True)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        self.previous_button = self._add_button(chevron_left, "previous thumbnail")
        self.reload_button = self._add_button(reload, "reload project from disk")
        self.open_in_button = self._add_button(open_in, "open project in explorer")
        self.error_label = QLabel()
        self.error_label.setPixmap(QPixmap(error))
        self.edit_button = self._add_button(edit, "edit project meta data")
        self.next_button = self._add_button(chevron_right, "next thumbnail")

        for element in [
            self.previous_button,
            self.reload_button,
            self.open_in_button,
            self.error_label,
            self.edit_button,
            self.next_button,
        ]:
            layout.addWidget(element)

        self.error_label.hide()

        policy = QSizePolicy()
        policy.setRetainSizeWhenHidden(True)

        self.previous_button.setSizePolicy(policy)
        self.previous_button.setVisible(False)
        self.next_button.setSizePolicy(policy)
        self.next_button.setVisible(False)

    def _add_button(self, icon_path: Path, tooltip: str) -> QPushButton:
        button = QPushButton()
        button.setIcon(QIcon(QPixmap(icon_path)))
        button.setFixedSize(28, 28)
        button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        button.setToolTip(tooltip)

        return button
