from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QSizePolicy,
    QMenu,
    QDialog
)

from PySide6.QtGui import QPixmap, QPalette, QImage
from PySide6.QtCore import Qt, QPoint, Slot, QSize, QEvent, QCoreApplication, QObject

class ImageLoadedEvent(QEvent):
    path: Path
    image: QImage

    s_type: int = QEvent.registerEventType()

    def __init__(self, path:Path, image: QImage):
        super().__init__(QEvent.Type(self.s_type))
        self.path = path
        self.image = image

class ImageLoader:
    def __init__(self):
        self._executor = ThreadPoolExecutor(max_workers=6)

    def load_image_for( self, object: QObject, path: Path ):
        def _task():
            try:
                image = QImage()
                success = image.load( path.as_posix() )
                # TODO: if failure
                event = ImageLoadedEvent( path, image )
                QCoreApplication.postEvent( object, event )
            except Exception as e:
                #TODO
                print(e)

        
        self._executor.submit(_task)