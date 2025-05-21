from pathlib import Path
from typing import cast

from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QLabel,
    QPushButton,
    QScrollArea,
    QFrame,
    QLayout,
    QSizePolicy,
    QLayoutItem,
    QMenu,
    QDialog,
    QMainWindow,
    QToolBar,
    QCheckBox,
    QStatusBar,
    QFileDialog,
)

from PySide6.QtGui import QPixmap, QEnterEvent, QPalette, QIcon, QAction, QCloseEvent
from PySide6.QtCore import (
    Qt,
    QMargins,
    QPoint,
    QRect,
    QSize,
    QEvent,
    Slot,
    QSettings,
    QByteArray,
)

from project_explorer.ui.project_browser import ProjectBrowser


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.settings = QSettings("Project Explorer", "Project Explorer")

        self.restoreGeometry(
            cast(QByteArray, self.settings.value("window_geometry", type=QByteArray))
        )

        self.setWindowTitle("Project Explorer")

        self.browser = ProjectBrowser()

        self.setCentralWidget(self.browser)

        button_action = QAction("&Open...", self)
        button_action.triggered.connect(self._open_new_vault)

        menu = self.menuBar()

        file_menu = menu.addMenu("&File")
        file_menu.addAction(button_action)

        self.recent_menu = QMenu("&Recently Opened", self)
        file_menu.addMenu(self.recent_menu)
        self._update_recent_menu()

        recent_dirs = cast(list[str], self.settings.value("recent_dirs", [], type=list))

        if recent_dirs:
            self._load_vault(Path(recent_dirs[0]))

    def _update_recent_menu(self) -> None:
        self.recent_menu.clear()
        recent_dirs = cast(list[str], self.settings.value("recent_dirs", [], type=list))
        for path in recent_dirs:
            action = QAction(path, self)
            action.triggered.connect(lambda checked, p=path: self._load_vault(Path(p)))
            self.recent_menu.addAction(action)

    def _load_vault(self, path: Path) -> None:
        self.browser.set_projects_path(path)

    def _open_new_vault(self) -> None:
        directory = QFileDialog.getExistingDirectory(self, "Select projects vault")

        if not directory:
            return

        recent_dirs = cast(list[str], self.settings.value("recent_dirs", [], type=list))

        if len(recent_dirs) > 9:
            recent_dirs.pop(-1)

        recent_dirs.insert(0, directory)
        self.settings.setValue("recent_dirs", recent_dirs)
        self._update_recent_menu()

        self._load_vault(Path(directory))

    def closeEvent(self, event: QCloseEvent) -> None:
        self.settings.setValue("window_geometry", self.saveGeometry())
        return super().closeEvent(event)
