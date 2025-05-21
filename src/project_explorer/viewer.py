"""
Application for quick browsing of projects
"""

import sys

from PySide6.QtWidgets import QApplication

from project_explorer.ui.main_window import MainWindow


def main() -> None:
    """Runs the application"""

    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    window = MainWindow()
    window.show()
    sys.exit(app.exec())
