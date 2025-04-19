"""Main application ui code"""

import os
import platform
import subprocess
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

from project_explorer.model.projects import ProjectsModel
from project_explorer.model.signal import Cause

from project_explorer.ui.project_overview import ProjectOverview
from project_explorer.ui.project_data import ProjectData
from project_explorer.ui.thumbnails import Thumbnails
from project_explorer.ui.statistics import Statistics


# pylint: disable=too-many-instance-attributes, too-few-public-methods
class ProjectExplorerTk:
    """Main application"""

    because_open_folder: Cause
    because_new_project: Cause

    def __init__(self) -> None:
        self.application = Tk()
        self.application.title("Project Explorer")
        self.application.geometry("1000x700")

        self.model = ProjectsModel()
        self.because_open_folder = Cause(ProjectExplorerTk, "open folder")
        self.because_new_project = Cause(ProjectExplorerTk, "new project")

        self._setup_ui()

        self.application.bind("<Control-s>", lambda _: self.project_data.trigger_save())

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
        self.project_view.set_model(self.model)

        self.statistics = Statistics(main_frame)
        self.statistics.grid(row=0, column=1, sticky="NSEW")
        self.statistics.set_model(self.model)

        self.button_bar = Frame(main_frame)
        self.button_bar.grid(row=1, column=0, columnspan=2, sticky="NSEW")

        # pylint: disable=unnecessary-lambda
        self.save_button = Button(
            self.button_bar,
            text="Save",
            command=lambda: self.project_data.trigger_save(),
        )
        self.save_button.pack(side="left")

        self.open_button = Button(self.button_bar, text="Open", command=self._open)
        self.open_button.pack(side="left")

        self.new_button = Button(self.button_bar, text="New", command=self._new)
        self.new_button.pack(side="left")

        self.project_data = ProjectData(main_frame)
        self.project_data.grid(row=2, column=0, sticky="NSEW")
        self.project_data.set_model(self.model)

        self.thumbnails = Thumbnails(main_frame)
        self.thumbnails.grid(row=2, column=1, sticky="NSEW")
        self.thumbnails.set_model(self.model)

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
        self.model.load_projects_from_path(
            Path(folder) if folder else None, self.because_open_folder
        )

    def _new(self) -> None:
        path = self.model.get_path()

        if path is None:
            # TODO: communicate this to the user
            return

        answer = simpledialog.askstring(
            "Location", prompt="In what subfolder should the project be placed?"
        )

        if answer is None:
            return

        if (path / answer).exists():
            # TODO: communicate this to the user
            return

        self.model.save_project(
            path / answer,
            Project(
                project_summary=ProjectSummary(
                    name="new project", state="new", tags=[]
                ),
                description="",
            ),
            self.because_new_project,
        )

    def _open(self) -> None:
        path = self.model.get_project_under_edit()

        if path is None:
            # TODO: communicate this to the user
            return

        if os.name in ["nt", "ce"]:
            os.startfile(os.path.normpath(path))
        elif "darwin" in platform.system().casefold():
            subprocess.run(["open", str(path)], check=True)
        else:  # assume Linux or other POSIX-like
            subprocess.run(["xdg-open", str(path)], check=True)
