from pathlib import Path

from pydantic import ValidationError

from project_explorer.data.project import (
    Project,
    InvalidProject,
    MissingProject,
    ProjectSummary,
)

def load_project(path: Path) -> Project | InvalidProject | MissingProject:
    if not path.exists() or not path.is_dir():
        return MissingProject(path=path)

    info_path = path / "project-info.json"

    if not info_path.exists() or not info_path.is_file():
        return InvalidProject(path=path)

    try:
        project_summary = ProjectSummary.model_validate_json(
            info_path.read_text(encoding="utf-8")
        )
        return Project(path=path, project_summary=project_summary)
    except (ValidationError, OSError) as e:
        return InvalidProject(path=path)