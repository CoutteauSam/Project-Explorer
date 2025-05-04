from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLineEdit,
    QScrollArea,
    QFrame,
)

from project_explorer.data.project import Project

from project_explorer.ui.flow_layout import FlowLayout
from project_explorer.ui.project_card import ProjectCard

class ProjectBrowser(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Project Browser")
        self.setGeometry(100, 100, 900, 400)

        main_layout = QVBoxLayout(self)

        # Search bar
        search_bar = QLineEdit()
        search_bar.setPlaceholderText("Search projects...")
        main_layout.addWidget(search_bar)

        # Scroll area with project cards
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_content = QWidget()
        scroll_content.setContentsMargins(20, 0, 20, 0)
        self.scroll_layout = FlowLayout(scroll_content)

        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)

    def set_projects( self, projects: list[Project] )->None:
        layout = self.scroll_layout

        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        for project in projects:
            card = ProjectCard()
            card.set_project(project)
            layout.addWidget(card)

