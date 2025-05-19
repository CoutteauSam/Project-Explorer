from pathlib import Path
from typing import cast

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
)
from PySide6.QtGui import QPixmap, QPalette, QIcon, QShortcut, QKeySequence
from PySide6.QtCore import Qt, QSettings, QEvent

from project_explorer.assets import favorite_off, favorite_on

from project_explorer.data.project import ProjectSummary, Project, InvalidProject, MissingProject

from project_explorer.data.query import Query, parse_query, InvalidQuery

from project_explorer.ui.flow_layout import FlowLayout
from project_explorer.ui.project_card import ProjectCard, load_project
from project_explorer.ui.image_loader import ImageLoader
from project_explorer.ui.line_edit_history import LineEditHistory, LineEditHistorySubmittedEvent
from project_explorer.ui.sorted_flow_container import SortedFlowContainer


def load_projects_from_path(path: Path) -> list[Project|InvalidProject|MissingProject]:
    """Load or reload project from a given root path"""

    projects = []

    for sub_directory in path.iterdir():
        if not sub_directory.is_dir():
            continue

        if sub_directory.suffix != ".project":
            continue

        project = load_project(sub_directory)
        projects.append(project)

    return projects


class ProjectBrowser(QWidget):
    projects_path: Path | None = None
    widgets: list[ProjectCard]

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Project Browser")
        self.setGeometry(100, 100, 900, 400)

        self.settings = QSettings("Project Explorer", "Project Explorer")

        self.image_loader = ImageLoader()

        main_layout = QVBoxLayout(self)

        tools_layout = QGridLayout()

        self.add_new_project_button = QPushButton()
        self.add_new_project_button.setText("New Project")
        self.add_new_project_button.clicked.connect(
            lambda: self._create_new_project_action()
        )
        self.add_new_project_button.setEnabled(False)

        tools_layout.addWidget(self.add_new_project_button,0,0)

        # Search bar
        self.search_bar = LineEditHistory()
        self.search_bar.set_storage(self.settings, "favorite_queries")
        self.search_bar.field.setPlaceholderText("Search projects...")

        tools_layout.addWidget(self.search_bar,0,1)

        tools_layout.setColumnStretch(0,0)
        tools_layout.setColumnStretch(1,1)
        tools_layout.setColumnStretch(2,0)

        main_layout.addLayout(tools_layout)

        # Scroll area with project cards
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.project_cards = SortedFlowContainer()
        self.project_cards.setContentsMargins(20, 0, 20, 0)

        scroll_area.setWidget(self.project_cards)
        main_layout.addWidget(scroll_area)

    def event(self, event: QEvent) -> bool:
        if event.type() == LineEditHistorySubmittedEvent.s_type:
            query_submitted_event = cast(LineEditHistorySubmittedEvent, event)
            self._filter_cards(query_submitted_event.text)
            return True

        return super().event(event)

    def _filter_cards(self, query_text:str)->None:
        if query_text.strip() == "":
            for card in self.project_cards.widgets():
                card.setVisible(True)
            return

        query = parse_query(query_text.strip())

        if isinstance(query, InvalidQuery):
            # TODO: communicate
            return
        
        for card in self.project_cards.widgets():
            card.setVisible(query.evaluate(dict(card.project.project_summary)))

    def _create_new_project_action(self) -> None:
        if self.projects_path is None:
            return

        dialog = QInputDialog()
        dialog.setModal(True)
        dialog.setInputMode(QInputDialog.InputMode.TextInput)
        dialog.setWindowTitle("Creating new project")
        dialog.setOkButtonText("Create")
        dialog.setLabelText("Project folder name:")

        if not dialog.exec():
            return

        folder_name = dialog.textValue()

        summary = ProjectSummary(name=folder_name, tags=[])
        path = self.projects_path / f"{folder_name}.project"

        if path.exists():
            return

        path.mkdir()

        with open(path / "project-info.json", "w", encoding="utf-8") as file:
            file.write(summary.model_dump_json())

        card = ProjectCard()
        card.set_image_loader(self.image_loader)
        card.set_project(Project(path=path, project_summary=summary))

        self.project_cards.insert(path, card)

    def set_projects_path(self, projects_path: Path) -> None:
        self.projects_path = None

        self.project_cards.clear_all()

        self.projects_path = projects_path

        self.add_new_project_button.setEnabled(True)

        projects = load_projects_from_path(projects_path)

        for project in projects:
            card = ProjectCard()
            card.set_image_loader(self.image_loader)
            card.set_project(project)

            self.project_cards.insert(project.path, card)
