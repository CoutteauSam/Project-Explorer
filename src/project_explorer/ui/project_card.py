from typing import Any, cast

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy, QMenu, QDialog, QGridLayout

from PySide6.QtGui import QPixmap, QPalette
from PySide6.QtCore import Qt, QPoint, Slot, QSize, QEvent

from project_explorer.assets import dummy

from project_explorer.utility.typing import copy_method_params

from project_explorer.data.project import Project

from project_explorer.ui.project_navigation_bar import ProjectNavigationBar
from project_explorer.ui.project_tag_list import ProjectTagList
from project_explorer.ui.image_loader import ImageLoadedEvent, ImageLoader
from project_explorer.ui.multi_image import MultiImage


class ProjectCard(QWidget):

    place_holder_image: QPixmap | None = None

    @copy_method_params(QWidget.__init__)
    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.setFixedSize(200, 200)

        pal = QPalette()
        pal.setColor(QPalette.ColorRole.Window, "#555555")
        self.setPalette(pal)
        self.setAutoFillBackground(True)

        if ProjectCard.place_holder_image is None:
            ProjectCard.place_holder_image = QPixmap(dummy).scaled(
                100,
                100,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )

        stack = QGridLayout(self)

        # Background image
        self.bg = MultiImage()
        self.bg.lower()
        self.bg.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        stack.setContentsMargins(0, 0, 0, 0)

        stack.addWidget(self.bg,0,0)

        # Overlay layout
        overlay = QVBoxLayout()
        overlay.setSpacing(2)

        # Navigation
        self.nav_bar = ProjectNavigationBar()
        overlay.addWidget(self.nav_bar)
        self.nav_bar.next_button.clicked.connect(lambda: self.bg.view_next_image())
        self.nav_bar.previous_button.clicked.connect(lambda: self.bg.view_previous_image())

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
        self.name_label.setContentsMargins(10, 10, 10, 10)
        self.name_label.setPalette(pal)
        self.name_label.setAutoFillBackground(True)
        overlay.addWidget(self.name_label)

        stack.addLayout(overlay,0,0)

        self.popMenu = QMenu(self)
        self.popMenu.addAction("Edit", self._edit_screen)

        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._open_context_menu)

    def set_project(self, image_loader: ImageLoader, project: Project):
        self.name_label.setText(project.project_summary.name)
        self.tags_widget.set_tags(project.project_summary.tags)

        if (project.path / "thumbnails").is_dir():
            for image in (project.path / "thumbnails").iterdir():
                image_loader.load_image_for(self, image)

    def event(self, event: QEvent) -> bool:
        if event.type() == ImageLoadedEvent.s_type:
            image_loaded_event = cast(ImageLoadedEvent, event)

            self.bg.add_image(
                QPixmap.fromImage(image_loaded_event.image)
            )

            if self.bg.has_multiple_images():
                self.nav_bar.previous_button.setVisible(True)
                self.nav_bar.next_button.setVisible(True)

            return True

        return super().event(event)

    @Slot()
    def _open_context_menu(self, point: QPoint):
        self.popMenu.exec(self.mapToGlobal(point))

    def _edit_screen(self) -> None:
        my_progress_dialog = QDialog(self)
        my_progress_dialog.setModal(True)
        my_progress_dialog.show()
