from typing import Any, cast
import subprocess
import os
import platform
from pathlib import Path

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy, QMenu, QDialog, QGridLayout, QLineEdit, QTextEdit, QHBoxLayout, QPushButton

from PySide6.QtGui import QPixmap, QPalette
from PySide6.QtCore import Qt, QPoint, Slot, QSize, QEvent

from project_explorer.assets import dummy

from project_explorer.utility.typing import copy_method_params

from project_explorer.data.project import Project

from project_explorer.ui.project_navigation_bar import ProjectNavigationBar
from project_explorer.ui.project_tag_list import ProjectTagList
from project_explorer.ui.image_loader import ImageLoadedEvent, ImageLoader
from project_explorer.ui.multi_image import MultiImage

def open_path_in_explorer( path: Path ):

    if not path.exists():
        return

    if os.name in ["nt", "ce"]:
        os.startfile(os.path.normpath(path))
    elif "darwin" in platform.system().casefold():
        subprocess.run(["open", str(path)], check=True)
    else:  # assume Linux or other POSIX-like
        subprocess.run(["xdg-open", str(path)], check=True)

class ProjectCard(QWidget):

    place_holder_image: QPixmap | None = None
    project : Project | None = None
    image_loader: ImageLoader

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
        self.nav_bar.previous_button.clicked.connect(lambda: self.bg.view_previous_image())
        self.nav_bar.open_in_button.clicked.connect(lambda: self._open_in_explorer())
        self.nav_bar.next_button.clicked.connect(lambda: self.bg.view_next_image())

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

    def set_project(self, project: Project):
        self.project = project
        self._update_project()

    def set_image_loader(self, image_loader: ImageLoader):
        self.image_loader = image_loader

    def _update_project( self )->None:
        self.name_label.setText(self.project.project_summary.name)
        self.tags_widget.set_tags(self.project.project_summary.tags)

        if (self.project.path / "thumbnails").is_dir():
            for image in (self.project.path / "thumbnails").iterdir():
                self.image_loader.load_image_for(self, image)

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
        if self.project is None:
            return

        my_progress_dialog = QDialog(self)
        my_progress_dialog.setModal(True)
        my_progress_dialog.setWindowTitle(f"Editing {self.project.project_summary.name} ({self.project.path.as_posix()})")

        layout = QGridLayout(my_progress_dialog)

        name = QLineEdit()
        name.setText( self.project.project_summary.name )
        tags = QTextEdit()
        tags.setText( ", ".join( self.project.project_summary.tags ) )

        layout.addWidget(QLabel("Name:"),0,0)
        layout.addWidget(QLabel("Tags:"),1,0)
        layout.addWidget(name,0,1)
        layout.addWidget(tags,1,1)

        additional_layout = QHBoxLayout()

        def create_and_open():
            path = self.project.path / "thumbnails"
            path.mkdir(exist_ok=True)
            open_path_in_explorer(path)

        show_thumbnail = QPushButton()
        show_thumbnail.setText("Open thumbnails folder")
        show_thumbnail.clicked.connect( lambda: create_and_open() )
        additional_layout.addWidget(show_thumbnail)

        save = QPushButton()
        save.setText("&Save")
        save.clicked.connect(lambda: (self._save_project(name.text(),tags.toPlainText()),my_progress_dialog.close()))
        additional_layout.addWidget(save)

        cancel = QPushButton()
        cancel.setText("&Cancel")
        cancel.clicked.connect( lambda: my_progress_dialog.close() )
        additional_layout.addWidget(cancel)

        layout.addLayout(additional_layout,2,0,1,2)

        my_progress_dialog.show()

    def _save_project(self, name:str, tags:str) -> None:
        if self.project is None:
            return

        self.project.project_summary.name = name
        self.project.project_summary.tags = list(set(tag.strip() for tag in tags.split(",") if tag.strip()))

        with open(self.project.path / "project-info.json", "w", encoding="utf-8") as file:
            file.write(self.project.project_summary.model_dump_json())

        self._update_project()

    def _open_in_explorer(self) -> None:

        if self.project is None:
            return

        open_path_in_explorer( self.project.path )
