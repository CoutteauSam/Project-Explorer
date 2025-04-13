"""Signal infrastructure for event based communication"""

from collections.abc import Callable
from typing import Type, Any
from dataclasses import dataclass


@dataclass(frozen=True)
class Cause:
    """The reason an event was triggered"""

    cause_type: Type[Any]
    identifier: str


class Signal:
    """A signal which can be triggered and listened too"""

    def __init__(self) -> None:
        self._callbacks: list[Callable[[Cause], None]] = []

    def listen(self, callback: Callable[[Cause], None]) -> None:
        """Register a callback to be called on signal trigger."""
        self._callbacks.append(callback)

    def notify(self, cause: Cause) -> None:
        """Trigger the signal with a cause."""

        for callback in self._callbacks:
            callback(cause)
