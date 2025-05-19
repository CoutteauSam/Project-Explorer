from typing import Any, cast
import subprocess
import os
import platform
from pathlib import Path

from pydantic import ValidationError

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy, QMenu, QDialog, QGridLayout, QLineEdit, QTextEdit, QHBoxLayout, QPushButton

from PySide6.QtGui import QPixmap, QPalette, QKeyEvent
from PySide6.QtCore import Qt, QPoint, Slot, QSize, QEvent, QObject, QCoreApplication

from project_explorer.utility.typing import copy_method_params

from project_explorer.data.project import Project, InvalidProject, MissingProject, ProjectSummary

from project_explorer.ui.project_navigation_bar import ProjectNavigationBar
from project_explorer.ui.project_tag_list import ProjectTagList, TagList
from project_explorer.ui.image_loader import ImageLoadedEvent, ImageLoader
from project_explorer.ui.multi_image import MultiImage

def load_project(path: Path) -> Project | InvalidProject | MissingProject:
    if not path.exists() or not path.is_dir():
        return MissingProject(path=path)

    info_path = path / "project-info.json"

    if not info_path.exists() or not info_path.is_file():
        return InvalidProject(path=path)

    try:
        project_summary = ProjectSummary.model_validate_json(
            info_path.read_text(encoding="utf-8")
        )
        return Project(path=path, project_summary=project_summary)
    except (ValidationError, OSError) as e:
        return InvalidProject(path=path)

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

    project : Project | InvalidProject | MissingProject = MissingProject(path=Path("/"))
    image_loader: ImageLoader

    @copy_method_params(QWidget.__init__)
    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.setFixedSize(200, 200)

        pal = QPalette()
        pal.setColor(QPalette.ColorRole.Window, "#555555")
        self.setPalette(pal)
        self.setAutoFillBackground(True)

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
        self.nav_bar.edit_button.clicked.connect(lambda: self._edit_screen())
        self.nav_bar.next_button.clicked.connect(lambda: self.bg.view_next_image())
        self.nav_bar.reload_button.clicked.connect(lambda: self.set_project(load_project(self.project.path)))

        self.nav_bar.edit_button.hide()
        self.nav_bar.error_label.setToolTip("Project is being loaded")
        self.nav_bar.error_label.show()

        # Spacer
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        overlay.addWidget(spacer)

        # Tags
        self.tags_widget = ProjectTagList()
        overlay.addWidget(self.tags_widget)

        # Project name
        pal = QPalette()
        pal.setColor(QPalette.ColorRole.Window, "#CC555555")
        self.name_label = QLabel("")
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.name_label.setContentsMargins(10, 10, 10, 10)
        self.name_label.setPalette(pal)
        self.name_label.setAutoFillBackground(True)
        font = self.name_label.font()
        font.setPointSize(12)
        font.setBold(True)
        self.name_label.setFont(font)
        
        overlay.addWidget(self.name_label)

        stack.addLayout(overlay,0,0)

    def set_project(self, project: Project | InvalidProject | MissingProject):
        self.project = project
        self._update_project()

    def set_image_loader(self, image_loader: ImageLoader):
        self.image_loader = image_loader

    def _update_project( self )->None:
        self.nav_bar.open_in_button.show()
        self.bg.clear()

        if isinstance(self.project,MissingProject):
            self.nav_bar.edit_button.hide()
            self.nav_bar.error_label.setToolTip("Project was not found on disk")
            self.nav_bar.error_label.show()
            self.bg.mark_invalid()
            return
        
        self.bg.mark_valid()
        self.nav_bar.edit_button.show()

        if isinstance(self.project,InvalidProject):
            self.nav_bar.error_label.setToolTip("Project found but contains no meta data")
            self.nav_bar.error_label.show()
        else:        
            self.name_label.setText(self.project.project_summary.name)
            self.tags_widget.set_tags(self.project.project_summary.tags)
            self.nav_bar.error_label.hide()

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

    def _edit_screen(self) -> None:
        if isinstance(self.project,MissingProject):
            return
        
        if isinstance(self.project,InvalidProject):
            project_name = self.project.path.name
            action = "Creating"
            project_tags = []
        else:
            project_name = self.project.project_summary.name
            action = "Editing"
            project_tags = self.project.project_summary.tags

        my_progress_dialog = QDialog(self)
        my_progress_dialog.setModal(True)
        my_progress_dialog.setWindowTitle(f"{action} {project_name} ({self.project.path.as_posix()})")

        layout = QGridLayout(my_progress_dialog)

        name = QLineEdit()
        name.installEventFilter(self)
        name.setText( project_name )

        name.setFocusPolicy(Qt.FocusPolicy(11))

        tags_input = QLineEdit()
        tags_input.installEventFilter(self)
        tags_input.setPlaceholderText("Add one or more tags <comma separated>")

        tags = TagList()
        tags.set_editable(True)
        for tag in project_tags:
            tags.add_tag(tag)

        def _add_new_tags():
            for tag_str in tags_input.text().split(","):
                tags.add_tag( tag_str.strip() )
            
            tags_input.setText("")

        tags_input.returnPressed.connect(_add_new_tags)

        layout.addWidget(QLabel("Name:"),0,0)
        layout.addWidget(QLabel("Tags:"),1,0)
        layout.addWidget(name,0,1)
        layout.addWidget(tags_input,1,1)
        layout.addWidget(tags,2,1)

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
        save.clicked.connect(lambda: (self._save_project(name.text(),tags.get_tags()),my_progress_dialog.close()))
        additional_layout.addWidget(save)

        cancel = QPushButton()
        cancel.setText("&Cancel")
        cancel.clicked.connect( lambda: my_progress_dialog.close() )
        additional_layout.addWidget(cancel)

        layout.addLayout(additional_layout,3,0,1,2)

        for button in my_progress_dialog.findChildren(QPushButton):
            button.setDefault(False)
            button.setAutoDefault(False)

        my_progress_dialog.show()

    def _save_project(self, name:str, tags:list[str]) -> None:
        if self.project is None:
            return

        self.project.project_summary.name = name
        self.project.project_summary.tags = tags

        with open(self.project.path / "project-info.json", "w", encoding="utf-8") as file:
            file.write(self.project.project_summary.model_dump_json())

        self._update_project()

    def _open_in_explorer(self) -> None:

        if self.project is None:
            return

        open_path_in_explorer( self.project.path )
