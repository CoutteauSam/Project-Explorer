from pathlib import Path

from pydantic import ValidationError

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

from PySide6.QtGui import QPixmap, QEnterEvent, QPalette, QIcon, QAction
from PySide6.QtCore import Qt, QMargins, QPoint, QRect, QSize, QEvent, Slot

from project_explorer.data.project import ProjectSummary, Project

from project_explorer.ui.project_browser import ProjectBrowser


def load_project( path: Path) -> ProjectSummary | None:
    info_path = path / "project-info.json"

    if not info_path.exists() or not info_path.is_file():
        return None

    try:
        project = ProjectSummary.model_validate_json(
            info_path.read_text(encoding="utf-8")
        )
    except (ValidationError, OSError):
        return None

    return project


def load_projects_from_path(path: Path) -> list[Project]:
    """Load or reload project from a given root path"""

    projects = []

    for sub_directory in path.iterdir():
        if not sub_directory.is_dir():
            continue

        if sub_directory.suffix != ".project":
            continue

        project = load_project(sub_directory)

        if project is None:
            # TODO: communicate this to the user
            continue

        projects.append(Project(path=sub_directory, project_summary=project))

    return projects


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Project Explorer")

        self.browser = ProjectBrowser()

        self.setCentralWidget(self.browser)

        button_action = QAction("&Open...", self)
        button_action.triggered.connect(self._open_new_vault)

        menu = self.menuBar()

        file_menu = menu.addMenu("&File")
        file_menu.addAction(button_action)

    def _open_new_vault(self):
        directory = Path(
            QFileDialog.getExistingDirectory(self, "Select projects vault")
        )

        self.browser.set_projects(load_projects_from_path(directory))
