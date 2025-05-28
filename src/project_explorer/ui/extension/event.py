from typing import Self, Any, Type, Protocol, TypeAlias
from abc import ABCMeta, abstractmethod, ABC

from enum import Enum

from PySide6.QtCore import QEvent

from project_explorer.utility.typing import Abstract


class Propagation(Enum):
    UP = "Up"
    DOWN = "Down"


class Event(Abstract,QEvent):
    __abstract__ = True

    def propagation(self) -> Propagation | None:
        return None

class PropagatingEvent(Event):
    __abstract__ = True

    def propagation(self) -> Propagation | None:
        return Propagation.UP

class BroadcastEvent(Event):
    __abstract__ = True

    def propagation(self) -> Propagation | None:
        return Propagation.DOWN