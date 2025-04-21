"""Main application ui code"""

from pathlib import Path
from tkinter import (
    Tk,
    filedialog,
    Frame,
    Menu,
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

    def __init__(self) -> None:
        self.application = Tk()
        self.application.title("Project Explorer")
        self.application.geometry("1000x700")

        self.model = ProjectsModel()
        self.because_open_folder = Cause(ProjectExplorerTk, "open folder")

        self._setup_ui()

    def run(self) -> None:
        """Start the application"""
        self.application.mainloop()

    def _setup_ui(self) -> None:
        self._setup_menu()

        main_frame = Frame(self.application)
        main_frame.pack(fill="both", expand=True)

        main_frame.grid_columnconfigure(1, weight=5)
        main_frame.grid_columnconfigure(0, weight=2)

        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)

        self.project_view = ProjectOverview(main_frame)
        self.project_view.grid(row=0, column=0, sticky="NSEW")
        self.project_view.set_model(self.model)

        self.statistics = Statistics(main_frame)
        self.statistics.grid(row=0, column=1, sticky="NSEW")
        self.statistics.set_model(self.model)

        self.project_data = ProjectData(main_frame)
        self.project_data.grid(row=1, column=0, sticky="NSEW")
        self.project_data.set_model(self.model)

        self.thumbnails = Thumbnails(main_frame)
        self.thumbnails.grid(row=1, column=1, sticky="NSEW")
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
        if folder:
            self.model.load_projects_from_path(Path(folder), self.because_open_folder)
