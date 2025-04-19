"""Central gui data model"""

from pathlib import Path

from pydantic import ValidationError

from project_explorer.data.project import ProjectSummary, Project

from project_explorer.model.signal import Signal, Cause


class InvalidProject:
    """A project which could not be loaded"""


class Root:
    """A root project group"""


class ProjectNode:
    """A node within a project tree"""

    path: Path
    project: ProjectSummary | InvalidProject | Root

    children: list["ProjectNode"]
    parent: "ProjectNode | None"

    def __init__(
        self,
        path: Path,
        project: ProjectSummary | InvalidProject | Root,
        parent: "ProjectNode | None" = None,
    ):
        self.path = path
        self.project = project
        self.children = []
        self.parent = parent

        if parent is not None:
            parent.children.append(self)


def _load_project(path: Path) -> ProjectSummary | InvalidProject:
    info_path = path / "project-info.json"

    if not info_path.exists() or not info_path.is_file():
        return InvalidProject()

    try:
        project = ProjectSummary.model_validate_json(
            info_path.read_text(encoding="utf-8")
        )
    except (ValidationError, OSError):
        return InvalidProject()

    return project


class ProjectRepository:
    """Stores loaded projects in an easy to access structure"""

    index: dict[Path, ProjectNode]

    root_nodes: dict[Path, ProjectNode]

    def __init__(self) -> None:
        self.index = {}
        self.root_nodes = {}

    def unload_node(self, path: Path) -> None:
        """Remove a node from the repository"""

        if path not in self.index:
            return

        for subnode in self.index[path].children:
            self.unload_node(subnode.path)

        node = self.index.pop(path)

        if node.parent is not None:
            node.parent.children.remove(node)

    def load_root(self, path: Path) -> None:
        """Load a new root project node"""

        if path in self.index and path not in self.root_nodes:
            raise ValueError("Adding root which is a sub item of another root")

        self.unload_node(path)

        self.index[path] = self.root_nodes[path] = ProjectNode(path, Root())

        todo_list: list[None | Path] = [None]

        while todo_list:
            parent = todo_list.pop()
            directory = parent if parent is not None else path

            for sub_directory in directory.iterdir():
                if not sub_directory.is_dir():
                    continue

                if sub_directory.suffix != ".project":
                    continue

                project = _load_project(sub_directory)

                self.index[sub_directory] = ProjectNode(
                    sub_directory, project, parent=self.index[directory]
                )
                todo_list.append(sub_directory)

    def update_project(
        self,
        path: Path,
        project: ProjectSummary | InvalidProject,
    ) -> None:
        """Update an existing project"""

        if path not in self.index:
            raise ValueError("unknown node")

        node = self.index[path]

        node.project = project

    def add_new_project(
        self, path: Path, project: ProjectSummary | InvalidProject, parent: Path
    ) -> None:
        """Add a new project to the repository"""

        if path in self.index:
            raise ValueError("node already exists")

        if parent not in self.index:
            raise ValueError("unknown parent")

        self.index[path] = ProjectNode(path, project, parent=self.index[parent])

    def get_project(self, path: Path) -> ProjectSummary | InvalidProject | Root | None:
        """Get a project from the repository"""

        if path in self.index:
            return self.index[path].project
        return None


class ProjectsModel:
    """Stores the current gui state"""

    _projects_root_path: Path | None = None
    _projects: ProjectRepository
    _project_under_edit: Path | None = None

    projects_loaded: Signal
    project_updated: Signal
    project_selected: Signal

    def __init__(self) -> None:
        self.projects_loaded = Signal()
        self.project_updated = Signal()
        self.project_selected = Signal()
        self._projects = ProjectRepository()

    def get_path(self) -> Path | None:
        """Get the current projects root path"""
        return self._projects_root_path

    def get_loaded_projects(self) -> ProjectRepository | None:
        """Get the projects loaded from the projects root path"""
        return self._projects

    def get_project_under_edit(self) -> None | Path:
        """Get the project path of the project currently being edited"""
        return self._project_under_edit

    def load_projects_from_path(self, path: Path, cause: Cause) -> None:
        """Load or reload project from a given root path"""

        self._projects.load_root(path)

        self.projects_loaded.notify(cause)

    def _set_project_under_edit(self, path: Path | None, cause: Cause) -> None:
        self._project_under_edit = path

        self.project_selected.notify(cause)

    def select_project_to_edit(self, path: Path | None, cause: Cause) -> None:
        """Select a project to be edited"""

        if path is None:
            self._set_project_under_edit(None, cause)

        if path is not None and (
            self._projects is None or self._projects.get_project(path) is None
        ):
            # TODO: communicate this to the user
            return

        self._set_project_under_edit(path, cause)

    def _set_project(
        self, path: Path, project: ProjectSummary | InvalidProject, cause: Cause
    ) -> None:
        if self._projects is None:
            return

        if path in self._projects.index:
            self._projects.update_project(path, project)
        else:
            self._projects.add_new_project(path, project, path.parent)

        self.project_updated.notify(cause)

    def load_project(self, path: Path, cause: Cause) -> None:
        """Load or reload a specific project"""

        if self._projects is None:
            # TODO: communicate this to the user
            return

        project = _load_project(path)

        self._set_project(path, project, cause)

    def save_project(self, path: Path, project: Project, cause: Cause) -> None:
        """Save and/or overwrite a project"""

        if self._projects is None:
            # TODO: communicate this to the user
            return

        path.mkdir(exist_ok=True)

        with open(path / "project-info.json", "w", encoding="utf-8") as file:
            file.write(project.project_summary.model_dump_json())

        with open(path / "description.md", "w", encoding="utf-8") as file:
            file.write(project.description)

        (path / "thumbnails").mkdir(exist_ok=True)

        self.load_project(path, cause)
