"""UI code for displaying a list of projects"""

from typing import Any
from pathlib import Path
from tkinter import (
    ttk,
    Frame,
)

from project_explorer.utility.typing import copy_method_params

from project_explorer.data.project import ProjectSummary
from project_explorer.data.query import Query

from project_explorer.model.signal import Cause
from project_explorer.model.projects import ProjectsModel

from project_explorer.ui.search_bar import SearchBar


class ProjectOverview(Frame):
    """UI element which gives an overview of the available projects"""

    path: Path | None = None
    projects: dict[Path, ProjectSummary] = {}
    model: ProjectsModel | None = None

    because_list_selection: Cause

    @copy_method_params(Frame.__init__)
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        self.because_list_selection = Cause(ProjectOverview, "item selected in list")

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

    def set_model(self, model: ProjectsModel | None) -> None:
        """Sets the ui model for this widget"""
        self.model = model
        self._update_table()

        if model is None:
            return

        model.projects_loaded.listen(lambda _: self._update_table())
        # not very efficient but it works
        model.project_updated.listen(lambda _: self._update_table())

    def update_project(self, path: Path, project: ProjectSummary) -> None:
        """Update or add project information"""
        self.projects[path] = project
        self._update_table()

    def _search_update(self, query: Query | None) -> None:
        if self.model is None:
            return

        self.query = query

        self._update_table()

    def _update_table(self) -> None:
        old_selection = self.tree.selection()

        for i in self.tree.get_children():
            self.tree.delete(i)

        if self.model is None:
            return

        projects = self.model.get_loaded_projects()

        if projects is None:
            return

        for path, project in projects.items():
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
        if self.model is None:
            return

        selection = self.tree.selection()
        selected = Path(selection[0]) if selection else None

        self.model.select_project_to_edit(selected, self.because_list_selection)
