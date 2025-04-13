"""Main application ui code"""

import os
import platform
import subprocess
from typing import Any
from pathlib import Path
from tkinter import (
    Tk,
    filedialog,
    Frame,
    Menu,
    Button,
    simpledialog,
)


from project_explorer.data.project import (
    ProjectSummary,
    Project,
)

from project_explorer.ui.project_overview import ProjectOverview
from project_explorer.ui.project_data import ProjectData
from project_explorer.ui.thumbnails import Thumbnails
from project_explorer.ui.statistics import Statistics


# pylint: disable=too-many-instance-attributes, too-few-public-methods
class ProjectExplorerTk:
    """Main application"""

    current_folder: Path | None = None

    def __init__(self) -> None:
        self.application = Tk()
        self.application.title("Project Explorer")
        self.application.geometry("1000x700")

        self._setup_ui()

        self.application.bind("<Control-s>", self._save)

    def run(self) -> None:
        """Start the application"""
        self.application.mainloop()

    def _setup_ui(self) -> None:
        self._setup_menu()

        main_frame = Frame(self.application)
        main_frame.pack(fill="both", expand=True)

        main_frame.grid_columnconfigure(1, weight=2)
        main_frame.grid_columnconfigure(0, weight=5)

        main_frame.grid_rowconfigure(0, weight=2)
        main_frame.grid_rowconfigure(1, weight=0)
        main_frame.grid_rowconfigure(2, weight=3)

        self.project_view = ProjectOverview(main_frame)
        self.project_view.grid(row=0, column=0, sticky="NSEW")
        self.project_view.on_project_selected(self._on_select_project)

        self.statistics = Statistics(main_frame)
        self.statistics.grid(row=0, column=1, sticky="NSEW")

        self.button_bar = Frame(main_frame)
        self.button_bar.grid(row=1, column=0, columnspan=2, sticky="NSEW")

        self.save_button = Button(self.button_bar, text="Save", command=self._save)
        self.save_button.pack(side="left")

        self.open_button = Button(self.button_bar, text="Open", command=self._open)
        self.open_button.pack(side="left")

        self.new_button = Button(self.button_bar, text="New", command=self._new)
        self.new_button.pack(side="left")

        self.project_data = ProjectData(main_frame)
        self.project_data.grid(row=2, column=0, sticky="NSEW")

        self.thumbnails = Thumbnails(main_frame)
        self.thumbnails.grid(row=2, column=1, sticky="NSEW")

    def _setup_menu(self) -> None:
        menubar = Menu(self.application)
        file_menu = Menu(menubar, tearoff=0)
        file_menu.add_command(label="Open Folder", command=self._choose_folder)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.application.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        self.application.config(menu=menubar)

    def _choose_folder(self) -> None:
        folder = filedialog.askdirectory()
        if folder:
            self.project_view.set_path(Path(folder))
            self.current_folder = Path(folder)
        else:
            self.project_view.set_path(None)
            self.current_folder = None

    def _on_select_project(self, path: Path | None) -> None:
        self.project_data.load_project_data(path)
        self.thumbnails.load_thumbnails(path)

    def _save(self, *_: Any) -> None:
        path = self.project_data.get_path()

        if path is None:
            return

        data = self.project_data.get_save_data()

        self._save_specific(path, data)

    def _new(self) -> None:
        if self.current_folder is None:
            return

        answer = simpledialog.askstring(
            "Location", prompt="In what subfolder should the project be placed?"
        )

        if answer is None:
            return

        if (self.current_folder / answer).exists():
            return

        self._save_specific(
            self.current_folder / answer,
            Project(
                project_summary=ProjectSummary(
                    name="new project", state="new", tags=[]
                ),
                description="",
            ),
        )

    def _save_specific(self, path: Path, data: Project) -> None:
        path.mkdir(exist_ok=True)

        with open(path / "project-info.json", "w", encoding="utf-8") as file:
            file.write(data.project_summary.model_dump_json())

        with open(path / "description.md", "w", encoding="utf-8") as file:
            file.write(data.description)

        (path / "thumbnails").mkdir(exist_ok=True)

        self.project_data.load_project_data(path)
        self.thumbnails.load_thumbnails(path)
        self.project_view.update_project(path, data.project_summary)

    def _open(self) -> None:
        path = self.project_data.get_path()

        if path is None:
            return

        if os.name in ["nt", "ce"]:
            os.startfile(os.path.normpath(path))
        elif "darwin" in platform.system().casefold():
            subprocess.run(["open", str(path)], check=True)
        else:  # assume Linux or other POSIX-like
            subprocess.run(["xdg-open", str(path)], check=True)
