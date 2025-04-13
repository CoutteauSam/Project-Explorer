"""UI code for a summary of all projects loaded"""

from typing import Any
from tkinter import (
    Frame,
    Label,
)

from project_explorer.utility.typing import copy_method_params


# pylint: disable=too-few-public-methods
class Statistics(Frame):
    """UI element displaying a summary of all the loaded project"""

    @copy_method_params(Frame.__init__)
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        self.label = Label(self, text="Statistics\n\nPlaceholder")
        self.label.pack(anchor="w")
