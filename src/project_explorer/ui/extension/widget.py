from PySide6.QtCore import QEvent, QObject, QCoreApplication, Qt
from PySide6.QtWidgets import QWidget

from project_explorer.ui.extension.event import Event, Propagation

class Widget(QWidget):
    def event(self, event: QEvent) -> bool:
        if isinstance(event, Event):
            if event.propagation() == Propagation.UP and self.parent():
                QCoreApplication.sendEvent(self.parent(), event)
            elif event.propagation() == Propagation.DOWN:
                self._propagateToChildren(event)
            return True  # Always mark custom events as handled
        return super().event(event)

    def _propagateToChildren(self, event: QEvent):
        for child in self.findChildren(QObject):
            QCoreApplication.sendEvent(child, event)