
from enum import Enum

from PySide6.QtCore import QEvent


class Propagation(Enum):
    UP = "Up"
    DOWN = "Down"

class Event(QEvent):
    def __new__(cls, *args, **kwargs):
        if cls is Event:
            msg = 'Abstract class {} cannot be instantiated'.format(cls.__name__)
            raise TypeError(msg)
        return super(Event, cls).__new__(cls, *args, **kwargs)
    
    def propagation(self) -> Propagation | None:
        return None
    
class PropagatingEvent(Event):
    def __new__(cls, *args, **kwargs):
        if cls is Event:
            msg = 'Abstract class {} cannot be instantiated'.format(cls.__name__)
            raise TypeError(msg)
        return super(Event, cls).__new__(cls, *args, **kwargs)

    def propagation(self):
        return Propagation.UP
    
class BroadcastEvent(Event):
    def __new__(cls, *args, **kwargs):
        if cls is Event:
            msg = 'Abstract class {} cannot be instantiated'.format(cls.__name__)
            raise TypeError(msg)
        return super(Event, cls).__new__(cls, *args, **kwargs)

    def propagation(self):
        return Propagation.DOWN