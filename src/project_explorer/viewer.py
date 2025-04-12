"""
Application for quick browsing of projects
"""

from project_explorer.ui.application import ProjectExplorerTk


def main() -> None:
    """Runs the application"""
    app = ProjectExplorerTk()
    app.run()
