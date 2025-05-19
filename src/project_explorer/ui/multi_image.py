from typing import Any, cast

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy, QMenu, QDialog, QGridLayout

from PySide6.QtGui import QPixmap, QPalette, QResizeEvent
from PySide6.QtCore import Qt, QPoint, Slot, QSize, QEvent

from project_explorer.assets import dummy, missing

from project_explorer.utility.typing import copy_method_params

from project_explorer.data.project import Project

from project_explorer.ui.project_navigation_bar import ProjectNavigationBar
from project_explorer.ui.project_tag_list import ProjectTagList
from project_explorer.ui.image_loader import ImageLoadedEvent, ImageLoader


class MultiImage(QWidget):
    place_holder_image: QPixmap | None = None
    invalid_image: QPixmap | None = None

    images: list[QPixmap]
    index: int = 0
    valid: bool = False

    @copy_method_params(QWidget.__init__)
    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)

        self.images = []

        if MultiImage.place_holder_image is None:
            MultiImage.place_holder_image = QPixmap(dummy)
            MultiImage.invalid_image = QPixmap(missing)
        
        layout = QGridLayout(self)

        self.picture = QLabel(self)
        
        self.picture.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.picture.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(self.picture)

        self._fit_image()

    def _fit_image(self)->None:
        if self.images:
            pixmap = self.images[ self.index ]
        else:
            pixmap = MultiImage.place_holder_image if self.valid else MultiImage.invalid_image
            
        self.picture.setPixmap(
            pixmap.scaled(self.picture.width(), self.picture.height(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        )

    def mark_valid(self):
        self.valid = True
        self._fit_image()

    def mark_invalid(self):
        self.valid = False
        self._fit_image()

    def clear(self):
        self.images = []
        self.index = 0
        self._fit_image()

    def has_multiple_images(self)->bool:
        return len(self.images) > 1
    
    def add_image( self, pixmap: QPixmap ):
        self.images.append(pixmap)
        self.mark_valid()

    def view_next_image(self):
        if not self.has_multiple_images():
            return
        
        self.index = ( self.index + 1 ) % len(self.images)

        self._fit_image()

    def view_previous_image(self):
        if not self.has_multiple_images():
            return
        
        self.index = ( self.index - 1 ) % len(self.images)

        self._fit_image()

    def resizeEvent(self, event:QResizeEvent):
        self._fit_image()
        return super().resizeEvent(event)