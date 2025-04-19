"""UI code for a summary of all projects loaded"""

from typing import Any
from tkinter import (
    Frame,
    Text,
)
from collections import Counter

from project_explorer.utility.typing import copy_method_params

from project_explorer.data.project import ProjectSummary

from project_explorer.model.projects import ProjectsModel


def show_counter(counter: Counter[str]) -> str:
    """Summarizes a counter object to show in UI"""
    return ", ".join(f"{key}({count})" for key, count in counter.most_common())


# pylint: disable=too-few-public-methods
class Statistics(Frame):
    """UI element displaying a summary of all the loaded project"""

    model: ProjectsModel | None = None

    @copy_method_params(Frame.__init__)
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        self.label = Text(self, wrap="word")
        self.label.pack(anchor="w", expand=True, fill="both")

    def set_model(self, model: ProjectsModel | None) -> None:
        """Sets the ui model for this widget"""
        self.model = model
        self._load_statistics()

        if model is None:
            return

        model.projects_loaded.listen(lambda _: self._load_statistics())
        model.project_updated.listen(lambda _: self._load_statistics())

    def _load_statistics(self) -> None:
        self.label.configure(state="normal")
        self.label.delete("1.0", "end")
        self.label.configure(state="disabled")

        # pylint: disable=duplicate-code
        if self.model is None:
            return

        projects = self.model.get_loaded_projects()

        if projects is None:
            return

        states: Counter[str] = Counter()
        tags: Counter[str] = Counter()

        for project_node in projects.index.values():
            if not isinstance(project_node.project, ProjectSummary):
                continue

            states[project_node.project.state] += 1
            tags.update(project_node.project.tags)

        self.label.configure(state="normal")
        self.label.insert("end", f"states:\n{show_counter(states)}\n\n")
        self.label.insert("end", f"tags:\n{show_counter(tags)}")
        self.label.configure(state="disabled")
