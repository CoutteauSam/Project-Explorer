from typing import Any

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QSizePolicy,
    QMenu,
    QDialog
)

from PySide6.QtGui import QPixmap, QPalette
from PySide6.QtCore import Qt, QPoint, Slot, QSize

from project_explorer.assets import dummy

from project_explorer.utility.typing import copy_method_params

from project_explorer.data.project import Project

from project_explorer.ui.project_navigation_bar import ProjectNavigationBar
from project_explorer.ui.project_tag_list import ProjectTagList

class ProjectCard(QWidget):

    @copy_method_params(QWidget.__init__)
    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.setFixedSize(200, 200)

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
        self.bg.setAlignment(Qt.AlignmentFlag.AlignCenter)

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
        self.tags_widget = ProjectTagList()
        overlay.addWidget(self.tags_widget)

        # Project name
        pal = QPalette()
        pal.setColor(QPalette.ColorRole.Window, "#88555555")
        self.name_label = QLabel("")
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.name_label.setContentsMargins(4, 4, 4, 4)
        self.name_label.setPalette(pal)
        self.name_label.setAutoFillBackground(True)
        overlay.addWidget(self.name_label)


        self.popMenu = QMenu(self)
        self.popMenu.addAction('Edit', self._edit_screen)

        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._open_context_menu)

    def set_project( self, project :Project ):
        self.name_label.setText( project.project_summary.name )
        self.tags_widget.set_tags( project.project_summary.tags )

        if (project.path / "thumbnails").is_dir():
            for image in (project.path / "thumbnails").iterdir():
                self.bg.setPixmap(
                     QPixmap(image).scaled(
                        200,200,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation,
                    )
                )
                break

    @Slot()
    def _open_context_menu(self, point:QPoint):
        self.popMenu.exec(self.mapToGlobal(point))

    def _edit_screen(self)->None:
        my_progress_dialog=QDialog( self )
        my_progress_dialog.setModal( True )
        my_progress_dialog.show()
