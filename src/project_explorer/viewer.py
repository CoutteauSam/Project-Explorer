"""
Application for quick browsing of projects
"""

import os
import platform
import subprocess
from collections.abc import Callable
from typing import Any
from pathlib import Path
from dataclasses import dataclass
from tkinter import (
    Tk,
    filedialog,
    ttk,
    Text,
    Scrollbar,
    Canvas,
    Frame,
    Label,
    Entry,
    Menu,
    Button,
    simpledialog,
    VERTICAL,
    BOTH,
    RIGHT,
    LEFT,
    Y,
    X,
)

from PIL import Image, ImageTk
from pydantic import BaseModel, ValidationError


class Project(BaseModel):
    """Project meta data, stored in project-info.json on disk"""

    name: str
    state: str
    tags: list[str]


# pylint: disable=too-few-public-methods
class SearchBar:
    """UI element which allows the user to specify a search query"""

    def __init__(self, parent: Frame) -> None:
        self.parent = parent

        self.frame = Frame(self.parent)
        self.frame.pack(fill=X, expand=True)

        self.callbacks: list[Callable[[str, bool], Any]] = []

        self.search_var = Entry(self.frame)
        self.search_var.pack(side=LEFT, expand=True, fill=X, padx=5, pady=5)
        self.search_var.bind("<Return>", self._trigger_search)

        self.search_button = Button(
            self.frame, text="Search", command=self._trigger_search
        )
        self.search_button.pack(side=LEFT)

        self.refresh_button = Button(
            self.frame, text="Refresh", command=self._trigger_refresh
        )
        self.refresh_button.pack(side=LEFT)

    def on_action_required(self, callback: Callable[[str, bool], Any]) -> None:
        """Add a callback to trigger when the user confirms some action within the search bar"""
        self.callbacks.append(callback)

    def _trigger_search(self, *_: Any) -> None:
        for callback in self.callbacks:
            callback(self.search_var.get(), False)

    def _trigger_refresh(self, *_: Any) -> None:
        for callback in self.callbacks:
            callback(self.search_var.get(), True)


class ProjectOverview:
    """UI element which gives an overview of the available projects"""

    path: Path | None = None
    projects: dict[Path, Project] = {}

    def __init__(self, parent: Frame) -> None:
        self.parent = parent

        self.frame = Frame(parent)
        self.frame.pack(fill=X)

        self.callbacks: list[Callable[[Path | None], Any]] = []
        self.query: list[str] = []

        self.search_bar = SearchBar(self.frame)
        self.search_bar.on_action_required(self._search_update)

        self.tree = ttk.Treeview(
            self.frame,
            columns=("id", "name", "state", "tags"),
            show="headings",
            selectmode="browse",
        )
        self.tree.pack(fill=X, padx=5)
        self.tree.heading("id", text="Path on Disk")
        self.tree.heading("name", text="Name")
        self.tree.heading("state", text="State")
        self.tree.heading("tags", text="Tags")
        self.tree.bind("<<TreeviewSelect>>", self._on_select_project)

    def on_project_selected(self, callback: Callable[[Path | None], Any]) -> None:
        """Add a callback for when a project is selected by the user"""

        self.callbacks.append(callback)

    def set_path(self, path: Path | None, forced: bool = False) -> None:
        """Set the root path from which projects are loaded"""

        if path == self.path and not forced:
            return

        self.path = path

        self._scan_projects()

    def update_project(self, path: Path, project: Project) -> None:
        """Update or add project information"""
        self.projects[path] = project
        self._update_table()

    def _scan_projects(self) -> None:
        self.projects.clear()

        if self.path is None:
            self._update_table()
            return

        for sub_directory in self.path.iterdir():
            if not sub_directory.is_dir():
                continue

            info_path = sub_directory / "project-info.json"

            if not info_path.exists() or not info_path.is_file():
                continue

            try:
                project = Project.model_validate_json(
                    info_path.read_text(encoding="utf-8")
                )
            except (ValidationError, OSError):
                continue

            self.projects[sub_directory] = project

        self._update_table()

    def _search_update(self, query: str, forced: bool) -> None:
        self.query = [tag.strip() for tag in query.split(",") if tag.strip()]

        if forced:
            self.set_path(self.path, True)
        else:
            self._update_table()

    def _update_table(self) -> None:
        old_selection = self.tree.selection()

        for i in self.tree.get_children():
            self.tree.delete(i)

        for path, project in self.projects.items():
            if self.query and not any(tag in project.tags for tag in self.query):
                continue

            self.tree.insert(
                "",
                "end",
                iid=path.as_posix(),
                values=(
                    path.as_posix(),
                    project.name,
                    project.state,
                    ", ".join(project.tags),
                ),
            )

        valid_selection = tuple(
            item for item in old_selection if self.tree.exists(item)
        )
        self.tree.selection_set(valid_selection)

    def _on_select_project(self, _: Any) -> None:
        selection = self.tree.selection()
        selected = Path(selection[0]) if selection else None

        for callback in self.callbacks:
            callback(selected)


@dataclass
class SaveData:
    """Data about a project which can be saved"""

    project: Project
    description: str


class Attribute:
    """UI element for editing key: value"""

    def __init__(self, parent: Frame, label: str) -> None:
        self.parent = parent

        self.frame = Frame(parent)
        self.frame.pack(fill=X)

        self.label = Label(self.frame, text=f"{label}:", width=10)
        self.label.pack(side=LEFT)

        self.input = Entry(self.frame)
        self.input.pack(side=LEFT, expand=True, fill=X)

    def get_value(self) -> str:
        """Get the current value of the attribute"""
        return self.input.get()

    def set_value(self, value: str) -> None:
        """Set the current value of the attribute"""

        self.input.delete(0, "end")
        self.input.insert(0, value)


# pylint: disable=too-many-instance-attributes
class ProjectData:
    """UI element showing project meta data"""

    def __init__(self, parent: Frame) -> None:
        self.parent = parent

        self.frame = Frame(parent)
        self.frame.pack(side=LEFT, fill=BOTH, expand=True, padx=5, pady=5)

        self.path = Label(self.frame, text="")
        self.path.pack()

        self.name = Attribute(self.frame, "Name")
        self.state = Attribute(self.frame, "State")
        self.tags = Attribute(self.frame, "Tags")

        self.label = Label(self.frame, text="Description:")
        self.label.pack(anchor="w")

        self.desc_box = Text(self.frame, wrap="word")
        self.desc_box.pack(fill=BOTH, expand=True)

    def load_project_data(self, path: Path | None) -> None:
        """Load and display project meta data from a given project path"""

        self.desc_box.delete("1.0", "end")
        self.path.config(text="")
        self.name.set_value("")
        self.state.set_value("")
        self.tags.set_value("")

        if path is None:
            return

        description_path = path / "description.md"
        info_path = path / "project-info.json"

        info = Project.model_validate_json(info_path.read_text(encoding="utf-8"))

        self.path.config(text=path.as_posix())
        self.name.set_value(info.name)
        self.state.set_value(info.state)
        self.tags.set_value(", ".join(info.tags))

        if description_path.exists() and description_path.is_file():
            with open(description_path, "r", encoding="utf-8") as file:
                description = file.read()
            self.desc_box.insert("end", description)

    def get_save_data(self) -> SaveData:
        """Get the current data within the widget as SaveData"""

        project = Project(
            name=self.name.get_value(),
            state=self.state.get_value(),
            tags=list(
                tag.strip() for tag in self.tags.get_value().split(",") if tag.strip()
            ),
        )

        return SaveData(description=self.desc_box.get("1.0", "end-1c"), project=project)
        # pylint: disable=line-too-long
        # -1c : https://stackoverflow.com/questions/14824163/how-to-get-the-input-from-the-tkinter-text-widget


# pylint: disable=too-few-public-methods
class Thumbnails:
    """UI element displaying the thumbnails of a project"""

    def __init__(self, parent: Frame) -> None:
        self.parent = parent

        self.frame = Frame(parent)
        self.frame.pack(side=RIGHT, fill=Y, padx=5, pady=5)

        self.images: list[ImageTk.PhotoImage] = []

        self.label = Label(self.frame, text="Thumbnails:")
        self.label.pack(anchor="w")

        self.thumb_canvas = Canvas(self.frame, width=300)
        self.thumb_canvas.pack(side=LEFT, fill=Y)

        self.scrollbar = Scrollbar(
            self.frame, orient=VERTICAL, command=self.thumb_canvas.yview
        )
        self.scrollbar.pack(side=RIGHT, fill=Y)

        self.thumb_canvas.configure(yscrollcommand=self.scrollbar.set)

        self.thumb_inner = Frame(self.thumb_canvas)
        self.thumb_canvas.create_window((0, 0), window=self.thumb_inner, anchor="nw")

        self.thumb_inner.bind(
            "<Configure>",
            lambda e: self.thumb_canvas.configure(
                scrollregion=self.thumb_canvas.bbox("all")
            ),
        )

    def load_thumbnails(self, path: Path | None) -> None:
        """Load new thumbnails from a given path"""

        for widget in self.thumb_inner.winfo_children():
            widget.destroy()

        self.images.clear()

        if path is None:
            return

        thumbnails_path = path / "thumbnails"

        if thumbnails_path.exists() and thumbnails_path.is_dir():
            for image_path in thumbnails_path.iterdir():
                if not image_path.is_file():
                    continue

                img = Image.open(image_path)

                img.thumbnail((280, 280))
                tk_img = ImageTk.PhotoImage(img)
                self.images.append(tk_img)
                lbl = Label(self.thumb_inner, image=tk_img)
                lbl.pack(pady=4)


class Preview:
    """UI element showing a summary of a project"""

    def __init__(self, parent: Frame) -> None:
        self.parent = parent

        self.frame = Frame(parent)
        self.frame.pack(fill=BOTH, expand=True)

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

    def get_save_data(self) -> SaveData:
        """Get the current data within the widget as SaveData"""

        return self.project_data.get_save_data()


# pylint: disable=too-many-instance-attributes
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
        main_frame.pack(fill=BOTH, expand=True)

        self.project_view = ProjectOverview(main_frame)
        self.project_view.on_project_selected(self._on_select_project)

        self.button_bar = Frame(main_frame)
        self.button_bar.pack(fill=X)

        self.save_button = Button(self.button_bar, text="Save", command=self._save)
        self.save_button.pack(side=LEFT)

        self.open_button = Button(self.button_bar, text="Open", command=self._open)
        self.open_button.pack(side=LEFT)

        self.new_button = Button(self.button_bar, text="New", command=self._new)
        self.new_button.pack(side=LEFT)

        self.preview = Preview(main_frame)

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
        self.preview.load_project(path)

    def _save(self, *_: Any) -> None:
        path = self.preview.get_path()

        if path is None:
            return

        data = self.preview.get_save_data()

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
            SaveData(Project(name="new project", state="new", tags=[]), description=""),
        )

    def _save_specific(self, path: Path, data: SaveData) -> None:
        path.mkdir(exist_ok=True)

        with open(path / "project-info.json", "w", encoding="utf-8") as file:
            file.write(data.project.model_dump_json())

        with open(path / "description.md", "w", encoding="utf-8") as file:
            file.write(data.description)

        (path / "thumbnails").mkdir(exist_ok=True)

        self.preview.load_project(path)
        self.project_view.update_project(path, data.project)

    def _open(self) -> None:
        path = self.preview.get_path()

        if path is None:
            return

        if os.name in ["nt", "ce"]:
            os.startfile(os.path.normpath(path))
        elif "darwin" in platform.system().casefold():
            subprocess.run(["open", str(path)], check=True)
        else:  # assume Linux or other POSIX-like
            subprocess.run(["xdg-open", str(path)], check=True)

def main()->None:
    """Runs the application"""
    app = ProjectExplorerTk()
    app.run()
