"""UI code for showing project summary data"""

from typing import Any
from pathlib import Path
from tkinter import (
    Text,
    Frame,
    Label,
)

from project_explorer.utility.typing import copy_method_params

from project_explorer.data.project import (
    ProjectSummary,
    Project,
    LATEST_PROJECT_SUMMARY_VERSION,
)


from project_explorer.ui.attribute import Attribute


# pylint: disable=too-many-instance-attributes
class ProjectData(Frame):
    """UI element showing project meta data"""

    path: Path | None = None

    @copy_method_params(Frame.__init__)
    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)

        self.path_label = Label(self, text="")
        self.path_label.pack()

        self.name = Attribute(self, "Name")
        self.state = Attribute(self, "State")
        self.tags = Attribute(self, "Tags")

        self.label = Label(self, text="Description:")
        self.label.pack(anchor="w")

        self.desc_box = Text(self, wrap="word")
        self.desc_box.pack(fill="both", expand=True)

    def load_project_data(self, path: Path | None) -> None:
        """Load and display project meta data from a given project path"""

        self.desc_box.delete("1.0", "end")
        self.path = path
        self.path_label.config(text="")
        self.name.set_value("")
        self.state.set_value("")
        self.tags.set_value("")

        if path is None:
            return

        description_path = path / "description.md"
        info_path = path / "project-info.json"

        info = ProjectSummary.model_validate_json(info_path.read_text(encoding="utf-8"))

        self.path_label.config(text=path.as_posix())
        self.name.set_value(info.name)
        self.state.set_value(info.state)
        self.tags.set_value(", ".join(info.tags))

        if description_path.exists() and description_path.is_file():
            with open(description_path, "r", encoding="utf-8") as file:
                description = file.read()
            self.desc_box.insert("end", description)

    def get_save_data(self) -> Project:
        """Get the current data within the widget as SaveData"""

        project = ProjectSummary(
            name=self.name.get_value(),
            state=self.state.get_value(),
            tags=list(
                tag.strip() for tag in self.tags.get_value().split(",") if tag.strip()
            ),
            version=LATEST_PROJECT_SUMMARY_VERSION,
        )

        return Project(
            description=self.desc_box.get("1.0", "end-1c"), project_summary=project
        )
        # pylint: disable=line-too-long
        # -1c : https://stackoverflow.com/questions/14824163/how-to-get-the-input-from-the-tkinter-text-widget

    def get_path(self) -> None | Path:
        """Return the path of the current project being viewed"""
        return self.path
