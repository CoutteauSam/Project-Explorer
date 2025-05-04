"""
Application for quick browsing of projects
"""

import sys

from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QLabel,
    QPushButton,
    QScrollArea,
    QFrame,
    QLayout,
    QSizePolicy,
    QLayoutItem,
    QMenu,
    QDialog
)

from PySide6.QtGui import QPixmap, QEnterEvent, QPalette, QIcon, QAction
from PySide6.QtCore import Qt, QMargins, QPoint, QRect, QSize, QEvent, Slot

from project_explorer.ui.project_browser import ProjectBrowser
# from project_explorer.ui.application import ProjectExplorerTk

def main() -> None:
    """Runs the application"""
    #app = ProjectExplorerTk()
    #app.run()

    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    pal = QPalette()
    pal.setColor(QPalette.ColorRole.Window, "#444444")
    app.setPalette(pal)

    window = ProjectBrowser()
    window.show()
    sys.exit(app.exec())