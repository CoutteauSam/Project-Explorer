"""UI code for displaying a list of projects"""

import os
from typing import Any, Generator
from pathlib import Path
from tkinter import ttk, Frame, Menu, Event, simpledialog
import subprocess
import platform
import tkinter.font as tkfont

from project_explorer.utility.typing import copy_method_params

from project_explorer.data.project import ProjectSummary, Project
from project_explorer.data.query import Query

from project_explorer.model.signal import Cause
from project_explorer.model.projects import (
    ProjectsModel,
    InvalidProject,
    ProjectNode,
    Root,
)

from project_explorer.ui.search_bar import SearchBar


def closed_items(tree: ttk.Treeview) -> set[str]:
    """Get the list of collapsed items in a tree view"""
    def _visit_recursive(item: str) -> Generator[str, None, None]:
        if not tree.item(item, "open"):
            yield item

        for subitem in tree.get_children(item):
            yield from _visit_recursive(subitem)

    return set(c for item in tree.get_children() for c in _visit_recursive(item))


def set_closed_items(tree: ttk.Treeview, closed: set[str]) -> None:
    """set the collapsed state of items in a tree based on a set"""

    def _visit_recursive(item: str) -> None:
        tree.item(item, open=item not in closed)

        for subitem in tree.get_children(item):
            _visit_recursive(subitem)

    for subitem in tree.get_children():
        _visit_recursive(subitem)


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
    model: ProjectsModel

    because_list_selection: Cause
    because_new_project: Cause

    @copy_method_params(Frame.__init__)
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        self.because_list_selection = Cause(ProjectOverview, "item selected in list")
        self.because_new_project = Cause(ProjectOverview, "new project")

        self.query: Query | None = None

        self.search_bar = SearchBar(self)
        self.search_bar.on_action_required(self._search_update)
        self.search_bar.pack(fill="x")

        self.tree = ttk.Treeview(
            self,
            columns=("name", "state", "tags"),
            show="tree headings",
            selectmode="browse",
        )
        self.tree.heading("#0", text="Path on Disk")
        self.tree.heading("name", text="Name")
        self.tree.heading("state", text="State")
        self.tree.heading("tags", text="Tags")
        self.tree.bind("<<TreeviewSelect>>", self._on_select_project)
        self.tree.bind("<Button-3>", self._context_menu)

        self.tree.pack(fill="both", expand=True)

        self.context_menu = Menu(self, tearoff=0)
        self.context_menu.add_command(label="Add project")
        self.context_menu.add_command(label="Open in Explorer")
        self.context_menu.add_command(label="Reload")
        self.context_menu.add_command(label="Close")

        auto_adjust_columns(self.tree)

    def set_model(self, model: ProjectsModel) -> None:
        """Sets the ui model for this widget"""
        self.model = model
        self._update_table()

        model.projects_loaded.listen(lambda _: self._update_table())
        # not very efficient but it works
        model.project_updated.listen(lambda _: self._update_table())

    def _context_menu(self, event: "Event[ttk.Treeview]") -> None:
        row_id = self.tree.identify_row(event.y)

        if not row_id:
            return

        projects = self.model.get_loaded_projects()

        self.tree.selection_set(row_id)

        item = projects.index[Path(row_id)]

        self.context_menu.entryconfig(0, command=lambda: self._new(item))
        self.context_menu.entryconfig(1, command=lambda: self._open(item))

        self.context_menu.entryconfig(
            3, state="disabled" if item.parent is not None else "normal"
        )
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()

    def _search_update(self, query: Query | None) -> None:
        self.query = query

        self._update_table()

    def _add_to_tree(self, project_node: ProjectNode) -> None:
        if isinstance(project_node.project, InvalidProject):
            values = ("", "", "")
        elif isinstance(project_node.project, Root):
            values = ("", "", "")
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
            text=project_node.path.name,
            values=values,
        )

    def _update_table(self) -> None:
        old_selection = self.tree.selection()
        old_closed = closed_items(self.tree)

        for i in self.tree.get_children():
            self.tree.delete(i)

        projects = self.model.get_loaded_projects()

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

            for node in reversed(to_add):
                self._add_to_tree(node)
                added_projects.add(node.path)

        valid_selection = tuple(
            item for item in old_selection if self.tree.exists(item)
        )
        self.tree.selection_set(valid_selection)
        set_closed_items(self.tree, old_closed)

    def _on_select_project(self, _: Any) -> None:
        selection = self.tree.selection()
        selected = Path(selection[0]) if selection else None

        self.model.select_project_to_edit(selected, self.because_list_selection)

    def _new(self, parent: ProjectNode) -> None:
        path = parent.path
        answer = simpledialog.askstring(
            "project folder name", prompt="How should the project folder be called?"
        )

        if answer is None:
            return

        if (path / answer).exists():
            # TODO: communicate this to the user
            return

        self.model.save_project(
            (path / answer).with_suffix(".project"),
            Project(
                project_summary=ProjectSummary(
                    name="new project", state="new", tags=[]
                ),
                description="",
            ),
            self.because_new_project,
        )

    def _open(self, node: ProjectNode) -> None:
        path = node.path

        if os.name in ["nt", "ce"]:
            os.startfile(os.path.normpath(path))
        elif "darwin" in platform.system().casefold():
            subprocess.run(["open", str(path)], check=True)
        else:  # assume Linux or other POSIX-like
            subprocess.run(["xdg-open", str(path)], check=True)
