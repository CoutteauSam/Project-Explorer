"""UI code for displaying a list of projects"""

from typing import Any
from pathlib import Path
from tkinter import (
    ttk,
    Frame,
)
import tkinter.font as tkfont

from project_explorer.utility.typing import copy_method_params

from project_explorer.data.project import ProjectSummary
from project_explorer.data.query import Query

from project_explorer.model.signal import Cause
from project_explorer.model.projects import (
    ProjectsModel,
    InvalidProject,
    ProjectNode,
    Root,
)

from project_explorer.ui.search_bar import SearchBar


def auto_adjust_columns(treeview: ttk.Treeview) -> None:
    """Dirty hack for getting the columns properly sized"""
    for col in treeview["columns"]:
        max_width = tkfont.Font().measure(col)
        for item in treeview.get_children():
            cell_value = treeview.set(item, col)
            cell_width = tkfont.Font().measure(cell_value)
            if cell_width > max_width:
                max_width = cell_width
        treeview.column(col, width=max_width + 10)


class ProjectOverview(Frame):
    """UI element which gives an overview of the available projects"""

    path: Path | None = None
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
            show="tree headings",
            selectmode="browse",
        )
        self.tree.heading("id", text="Path on Disk")
        self.tree.heading("name", text="Name")
        self.tree.heading("state", text="State")
        self.tree.heading("tags", text="Tags")
        self.tree.column("#0", width=20, stretch=False)
        self.tree.bind("<<TreeviewSelect>>", self._on_select_project)
        self.tree.pack(fill="both", expand=True)

        auto_adjust_columns(self.tree)

    def set_model(self, model: ProjectsModel | None) -> None:
        """Sets the ui model for this widget"""
        self.model = model
        self._update_table()

        if model is None:
            return

        model.projects_loaded.listen(lambda _: self._update_table())
        # not very efficient but it works
        model.project_updated.listen(lambda _: self._update_table())

    def _search_update(self, query: Query | None) -> None:
        if self.model is None:
            return

        self.query = query

        self._update_table()

    def _add_to_tree(self, project_node: ProjectNode, depth: int = 0) -> None:
        if isinstance(project_node.project, InvalidProject):
            values = ("Unknown", "Invalid", "")
        elif isinstance(project_node.project, Root):
            values = ("Project Group", "", "")
        else:
            values = (
                project_node.project.name,
                project_node.project.state,
                ", ".join(project_node.project.tags),
            )

        self.tree.insert(
            (
                project_node.parent.path.as_posix()
                if project_node.parent is not None
                else ""
            ),
            "end",
            iid=project_node.path.as_posix(),
            values=("    " * depth + project_node.path.name, *values),
        )

    def _update_table(self) -> None:
        old_selection = self.tree.selection()

        for i in self.tree.get_children():
            self.tree.delete(i)

        if self.model is None:
            return

        projects = self.model.get_loaded_projects()

        if projects is None:
            return

        added_projects: set[Path] = set()

        for _, project_node in sorted(projects.index.items()):
            if (self.query is not None) and (
                not isinstance(project_node.project, ProjectSummary)
                or (not self.query.evaluate(project_node.project.model_dump()))
            ):
                continue

            node: ProjectNode | None = project_node
            to_add: list[ProjectNode] = []
            while node is not None and node.path not in added_projects:
                to_add.append(node)
                node = node.parent

            base_depth = -1
            _n = to_add[-1] if to_add else None
            while _n is not None:
                _n = _n.parent
                base_depth += 1

            for depth, node in enumerate(reversed(to_add)):
                self._add_to_tree(node, base_depth + depth)
                added_projects.add(node.path)

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
