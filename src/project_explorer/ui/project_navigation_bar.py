from typing import Any

from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QPushButton,
)

from PySide6.QtGui import QPixmap, QPalette, QIcon
from PySide6.QtCore import Qt

from project_explorer.utility.typing import copy_method_params

from project_explorer.assets import chevron_left, chevron_right, open_in, terminal

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
        pal.setColor(QPalette.ColorRole.Window, "#88555555")
        self.setPalette(pal)
        self.setAutoFillBackground(True)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        previous_button = self._add_button(chevron_left)
        open_in_button = self._add_button(open_in)
        terminal_button = self._add_button(terminal)
        next_button = self._add_button(chevron_right)

        for button in [previous_button, open_in_button, terminal_button, next_button]:
            layout.addWidget(button)

    def _add_button(self, icon_path: str) -> QPushButton:
        button = QPushButton()
        button.setIcon(QIcon(QPixmap(icon_path)))
        button.setFixedSize(28, 28)
        button.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        return button
