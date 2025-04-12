"""Contains datastructures describing a project"""

from pydantic import BaseModel

LATEST_PROJECT_SUMMARY_VERSION = 1


class ProjectSummary(BaseModel):
    """Project meta data, stored in project-info.json on disk"""

    version: int = 0
    name: str
    state: str
    tags: list[str]


class Project(BaseModel):
    """
    A collection of all information related to a project,
    spread over multiple files on disk
    """

    project_summary: ProjectSummary
    description: str
