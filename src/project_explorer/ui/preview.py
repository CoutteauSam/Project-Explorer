"""Project preview UI code"""

from pathlib import Path
from tkinter import Frame

from project_explorer.data.project import Project

from project_explorer.ui.project_data import ProjectData
from project_explorer.ui.thumbnails import Thumbnails


class Preview:
    """UI element showing a summary of a project"""

    def __init__(self, parent: Frame) -> None:
        self.parent = parent

        self.frame = Frame(parent)
        self.frame.pack(fill="both", expand=True)

        self.path: Path | None = None

        self.project_data = ProjectData(self.frame)
        self.thumbnails = Thumbnails(self.frame)

    def load_project(self, path: Path | None) -> None:
        """Load a new project into the preview"""

        self.path = path
        self.project_data.load_project_data(path)
        self.thumbnails.load_thumbnails(path)

    def get_path(self) -> None | Path:
        """Return the path of the current project being viewed"""
        return self.path

    def get_save_data(self) -> Project:
        """Get the current data within the widget as SaveData"""

        return self.project_data.get_save_data()
