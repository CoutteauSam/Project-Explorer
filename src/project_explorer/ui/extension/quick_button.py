from collections.abc import Callable
from typing import Any

from PySide6.QtWidgets import QPushButton

def text_button(text:str, action:Callable[[],Any])->QPushButton:
    button = QPushButton()
    button.setText(text)
    button.clicked.connect(action)
    return button