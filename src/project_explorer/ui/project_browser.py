from pathlib import Path

from pydantic import ValidationError

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLineEdit,
    QScrollArea,
    QFrame,
    QInputDialog,
)

from project_explorer.data.project import ProjectSummary, Project

from project_explorer.data.query import Query, parse_query, InvalidQuery

from project_explorer.ui.flow_layout import FlowLayout
from project_explorer.ui.project_card import ProjectCard
from project_explorer.ui.image_loader import ImageLoader


def load_project(path: Path) -> ProjectSummary | None:
    info_path = path / "project-info.json"

    if not info_path.exists() or not info_path.is_file():
        return None

    try:
        project = ProjectSummary.model_validate_json(
            info_path.read_text(encoding="utf-8")
        )
    except (ValidationError, OSError) as e:
        print(e)
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


class ProjectBrowser(QWidget):
    projects_path: Path | None = None
    widgets: list[ProjectCard]

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Project Browser")
        self.setGeometry(100, 100, 900, 400)

        self.image_loader = ImageLoader()

        main_layout = QVBoxLayout(self)

        tools_layout = QHBoxLayout()

        self.add_new_project_button = QPushButton()
        self.add_new_project_button.setText("New Project")
        self.add_new_project_button.clicked.connect(
            lambda: self._create_new_project_action()
        )
        self.add_new_project_button.setEnabled(False)

        tools_layout.addWidget(self.add_new_project_button)

        self.widgets = []

        # Search bar
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search projects...")
        self.search_bar.returnPressed.connect(lambda: self._filter_cards())

        tools_layout.addWidget(self.search_bar)

        main_layout.addLayout(tools_layout)

        # Scroll area with project cards
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_content = QWidget()
        scroll_content.setContentsMargins(20, 0, 20, 0)
        self.scroll_layout = FlowLayout(scroll_content)

        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)

    def _filter_cards(self)->None:
        query_text = self.search_bar.text()

        query = parse_query(query_text)

        if isinstance(query, InvalidQuery):
            # TODO: communicate
            return
        
        for card in self.widgets:
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

        self.widgets.append(card)
        self.scroll_layout.addWidget(card)

    def set_projects_path(self, projects_path: Path) -> None:
        layout = self.scroll_layout

        self.projects_path = None

        self.widgets = []
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        self.projects_path = projects_path

        self.add_new_project_button.setEnabled(True)

        projects = load_projects_from_path(projects_path)

        for project in projects:
            card = ProjectCard()
            card.set_image_loader(self.image_loader)
            card.set_project(project)

            self.widgets.append(card)
            layout.addWidget(card)
