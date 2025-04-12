"""UI code for showing project summary data"""

from pathlib import Path
from tkinter import (
    Text,
    Frame,
    Label,
)

from project_explorer.data.project import (
    ProjectSummary,
    Project,
    LATEST_PROJECT_SUMMARY_VERSION,
)


from project_explorer.ui.attribute import Attribute


# pylint: disable=too-many-instance-attributes
class ProjectData:
    """UI element showing project meta data"""

    def __init__(self, parent: Frame) -> None:
        self.parent = parent

        self.frame = Frame(parent)
        self.frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        self.path = Label(self.frame, text="")
        self.path.pack()

        self.name = Attribute(self.frame, "Name")
        self.state = Attribute(self.frame, "State")
        self.tags = Attribute(self.frame, "Tags")

        self.label = Label(self.frame, text="Description:")
        self.label.pack(anchor="w")

        self.desc_box = Text(self.frame, wrap="word")
        self.desc_box.pack(fill="both", expand=True)

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

        info = ProjectSummary.model_validate_json(info_path.read_text(encoding="utf-8"))

        self.path.config(text=path.as_posix())
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
