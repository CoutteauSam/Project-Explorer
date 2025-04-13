"""UI code for displaying a list of projects"""

from collections.abc import Callable
from typing import Any
from pathlib import Path
from tkinter import (
    ttk,
    Frame,
)

from pydantic import ValidationError

from project_explorer.utility.typing import copy_method_params

from project_explorer.data.project import ProjectSummary
from project_explorer.data.query import Query

from project_explorer.ui.search_bar import SearchBar


class ProjectOverview(Frame):
    """UI element which gives an overview of the available projects"""

    path: Path | None = None
    projects: dict[Path, ProjectSummary] = {}

    @copy_method_params(Frame.__init__)
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        self.callbacks: list[Callable[[Path | None], Any]] = []
        self.query: Query | None = None

        self.search_bar = SearchBar(self)
        self.search_bar.on_action_required(self._search_update)
        self.search_bar.pack(fill="x")

        self.tree = ttk.Treeview(
            self,
            columns=("id", "name", "state", "tags"),
            show="headings",
            selectmode="browse",
        )
        self.tree.pack(fill="both", expand=True)
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

    def update_project(self, path: Path, project: ProjectSummary) -> None:
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
                project = ProjectSummary.model_validate_json(
                    info_path.read_text(encoding="utf-8")
                )
            except (ValidationError, OSError):
                continue

            self.projects[sub_directory] = project

        self._update_table()

    def _search_update(self, query: Query | None, forced: bool) -> None:
        self.query = query

        if forced:
            self.set_path(self.path, True)
        else:
            self._update_table()

    def _update_table(self) -> None:
        old_selection = self.tree.selection()

        for i in self.tree.get_children():
            self.tree.delete(i)

        for path, project in self.projects.items():
            if (self.query is not None) and not self.query.evaluate(
                project.model_dump()
            ):
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
