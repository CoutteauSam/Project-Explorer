"""Central gui data model"""

from pathlib import Path

from pydantic import ValidationError

from project_explorer.data.project import ProjectSummary, Project

from project_explorer.model.signal import Signal, Cause


class ProjectsModel:
    """Stores the current gui state"""

    _projects_root_path: Path | None = None
    _projects: dict[Path, ProjectSummary] | None = None
    _project_under_edit: Path | None = None

    projects_loaded: Signal
    project_updated: Signal
    project_selected: Signal

    def __init__(self) -> None:
        self.projects_loaded = Signal()
        self.project_updated = Signal()
        self.project_selected = Signal()

    def get_path(self) -> Path | None:
        """Get the current projects root path"""
        return self._projects_root_path

    def get_loaded_projects(self) -> dict[Path, ProjectSummary] | None:
        """Get the projects loaded from the projects root path"""
        return self._projects

    def get_project_under_edit(self) -> None | Path:
        """Get the project path of the project currently being edited"""
        return self._project_under_edit

    def _set_new_projects(
        self,
        path: Path | None,
        projects: dict[Path, ProjectSummary] | None,
        cause: Cause,
    ) -> None:
        self._projects_root_path = path
        self._projects = projects

        self.projects_loaded.notify(cause)

        if (
            self._project_under_edit is not None
            and self._projects is not None
            and self._project_under_edit not in self._projects
        ):
            self._set_project_under_edit(None, cause)

    def _load_project(self, path: Path) -> ProjectSummary | None:
        info_path = path / "project-info.json"

        if not info_path.exists() or not info_path.is_file():
            return None

        try:
            project = ProjectSummary.model_validate_json(
                info_path.read_text(encoding="utf-8")
            )
        except (ValidationError, OSError):
            return None

        return project

    def load_projects_from_path(self, path: Path | None, cause: Cause) -> None:
        """Load or reload project from a given root path"""

        if path is None:
            self._set_new_projects(None, None, cause)
            return

        projects = {}

        for sub_directory in path.iterdir():
            if not sub_directory.is_dir():
                continue

            project = self._load_project(sub_directory)

            if project is None:
                # TODO: communicate this to the user
                continue

            projects[sub_directory] = project

        self._set_new_projects(path, projects, cause)

    def _set_project_under_edit(self, path: Path | None, cause: Cause) -> None:
        self._project_under_edit = path

        self.project_selected.notify(cause)

    def select_project_to_edit(self, path: Path | None, cause: Cause) -> None:
        """Select a project to be edited"""

        if path is None:
            self._set_project_under_edit(None, cause)

        if self._projects is None or path not in self._projects:
            # TODO: communicate this to the user
            return

        self._set_project_under_edit(path, cause)

    def _set_project(self, path: Path, project: ProjectSummary, cause: Cause) -> None:
        if self._projects is None:
            return

        self._projects[path] = project
        self.project_updated.notify(cause)

    def load_project(self, path: Path, cause: Cause) -> None:
        """Load or reload a specific project"""

        if self._projects is None:
            # TODO: communicate this to the user
            return

        project = self._load_project(path)

        if project is None:
            # TODO: communicate this to the user
            return

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
