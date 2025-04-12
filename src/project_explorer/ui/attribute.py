"""UI code for displaying simply edit fields"""

from tkinter import (
    Frame,
    Label,
    Entry,
)


class Attribute:
    """UI element for editing key: value"""

    def __init__(self, parent: Frame, label: str) -> None:
        self.parent = parent

        self.frame = Frame(parent)
        self.frame.pack(fill="x")

        self.label = Label(self.frame, text=f"{label}:", width=10)
        self.label.pack(side="left")

        self.input = Entry(self.frame)
        self.input.pack(side="left", expand=True, fill="x")

    def get_value(self) -> str:
        """Get the current value of the attribute"""
        return self.input.get()

    def set_value(self, value: str) -> None:
        """Set the current value of the attribute"""

        self.input.delete(0, "end")
        self.input.insert(0, value)
