from pathlib import Path

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QSizePolicy,
    QMenu,
    QDialog
)

from PySide6.QtGui import QPixmap, QPalette
from PySide6.QtCore import Qt, QPoint, Slot

from project_explorer.assets import dummy

from project_explorer.ui.project_navigation_bar import ProjectNavigationBar
from project_explorer.ui.project_tag_list import ProjectTagList

class ProjectCard(QWidget):
    def __init__(self, name: str, project_path: Path, tags: list[str]):
        super().__init__()
        self.setFixedSize(200, 200)
        self.tags = tags

        pal = QPalette()
        pal.setColor(QPalette.ColorRole.Window, "#555555")
        self.setPalette(pal)
        self.setAutoFillBackground(True)

        # Background image
        self.bg = QLabel(self)
        self.bg.setPixmap(
            QPixmap(dummy).scaled(
                200,
                200,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )
        self.bg.setGeometry(0, 0, 200, 200)
        self.bg.lower()
        self.bg.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        # Overlay layout
        overlay = QVBoxLayout(self)
        overlay.setContentsMargins(0, 0, 0, 0)
        overlay.setSpacing(2)

        # Navigation
        nav_bar = ProjectNavigationBar()
        overlay.addWidget(nav_bar)

        # Spacer
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        overlay.addWidget(spacer)

        # Tags
        tags_widget = ProjectTagList()
        overlay.addWidget(tags_widget)
        tags_widget.set_tags(tags)

        # Project name
        pal = QPalette()
        pal.setColor(QPalette.ColorRole.Window, "#88555555")
        name_label = QLabel(name)
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_label.setContentsMargins(4, 4, 4, 4)
        name_label.setPalette(pal)
        name_label.setAutoFillBackground(True)
        overlay.addWidget(name_label)


        self.popMenu = QMenu(self)
        self.popMenu.addAction('Edit', self._edit_screen)

        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._open_context_menu)

    @Slot()
    def _open_context_menu(self, point:QPoint):
        self.popMenu.exec(self.mapToGlobal(point))

    def _edit_screen(self)->None:
        my_progress_dialog=QDialog( self )
        my_progress_dialog.setModal( True )
        my_progress_dialog.show()
