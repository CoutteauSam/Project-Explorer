from pathlib import Path
from typing import cast, Any

from pydantic import ValidationError

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QPushButton,
    QLineEdit,
    QToolButton,
    QScrollArea,
    QFrame,
    QInputDialog,
    QComboBox,
    QMenu,
)
from PySide6.QtGui import QPixmap, QPalette, QIcon, QShortcut, QKeySequence, QAction
from PySide6.QtCore import Qt, QSettings, QEvent, QPoint, QCoreApplication

from project_explorer.assets import favorite_off, favorite_on, arrow_down

from project_explorer.utility.typing import copy_method_params

from project_explorer.data.project import ProjectSummary, Project

from project_explorer.data.query import Query, parse_query, InvalidQuery

from project_explorer.ui.extension.widget import Widget
from project_explorer.ui.extension.event import PropagatingEvent

from project_explorer.ui.layout.flow_layout import FlowLayout
from project_explorer.ui.project_card import ProjectCard
from project_explorer.ui.image_loader import ImageLoader
from project_explorer.ui.sorted_flow_container import SortedFlowContainer


class LineEditHistorySubmittedEvent(PropagatingEvent):
    text: str

    s_type: int = QEvent.registerEventType()

    def __init__(self, text: str):
        super().__init__(QEvent.Type(self.s_type))
        self.text = text


class LineEditHistory(Widget):
    _storage: tuple[QSettings, str] | None = None
    _favorites: set[str]

    @copy_method_params(Widget.__init__)
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        self._favorites = set()

        layout = QGridLayout(self)

        self.field = QLineEdit()
        self.field.textChanged.connect(lambda: self.query_changed())
        self.field.returnPressed.connect(
            lambda: QCoreApplication.sendEvent(
                self, LineEditHistorySubmittedEvent(self.field.text())
            )
        )

        self.setStyleSheet(
            "QPushButton{ background-color: transparent; border: 0px; } "
        )

        layout.addWidget(self.field, 0, 0, 1, 3)

        self.favorite_button = QPushButton()
        icon = QIcon()
        icon.addPixmap(QPixmap(favorite_on), QIcon.Mode.Normal, QIcon.State.On)
        icon.addPixmap(QPixmap(favorite_off), QIcon.Mode.Normal, QIcon.State.Off)
        self.favorite_button.setIcon(icon)
        self.favorite_button.setCheckable(True)
        self.favorite_button.toggled.connect(
            lambda: self.set_favorite(
                self.field.text().strip(), self.favorite_button.isChecked()
            )
        )

        layout.addWidget(self.favorite_button, 0, 1)

        self.history_button = QPushButton()
        self.history_button.setIcon(QIcon(QPixmap(arrow_down)))
        self.history_button.clicked.connect(lambda: self._toggle_menu())

        layout.addWidget(self.history_button, 0, 2)

        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 0)
        layout.setColumnStretch(2, 0)

        self.menu = QMenu(self)

    def _get_from_storage(self) -> set[str]:
        assert self._storage is not None

        settings, key = self._storage

        return set(cast(list[str], settings.value(key, type=list)))

    def _send_to_storage(self, values: set[str]) -> None:
        assert self._storage is not None

        settings, key = self._storage

        settings.setValue(key, list(values))

    def _toggle_menu(self) -> None:
        if not self._favorites:
            return

        if self.menu.isVisible():
            self.menu.hide()
            return

        self.menu.clear()

        for favorite in sorted(self._favorites):
            action = QAction(QIcon(QPixmap(favorite_on)), favorite, self)

            class Closure:  # For some reason normal closures get completely messed up
                def __init__(self, value: str, other: "LineEditHistory") -> None:
                    self.value = value
                    self.other = other

                def __call__(self) -> None:
                    self.other.field.setText(self.value)
                    QCoreApplication.sendEvent(
                        self.other, LineEditHistorySubmittedEvent(self.value)
                    )

            action.triggered.connect(Closure(favorite, self))
            self.menu.addAction(action)

        menu_width = self.field.width()
        pos = self.field.mapToGlobal(QPoint(0, self.field.height()))
        self.menu.setFixedWidth(menu_width)
        self.menu.popup(pos)

    def set_storage(self, settings: QSettings, key: str) -> None:
        backup = self._favorites

        self._storage = (settings, key)

        self._favorites = self._get_from_storage()
        self._favorites.update(backup)
        self._send_to_storage(self._favorites)

    def set_favorite(self, value: str, favorite: bool) -> None:
        if (value in self._favorites) == (favorite):
            return

        if favorite:
            self._favorites.add(value)
        else:
            self._favorites.discard(value)

        self._send_to_storage(self._favorites)

    def query_changed(self) -> None:
        self.favorite_button.setChecked(self.field.text().strip() in self._favorites)
