from typing import Any, Self, cast
import hashlib

from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QScrollArea,
    QFrame,
    QSizePolicy,
    QPushButton,
    QHBoxLayout
)

from PySide6.QtGui import  QEnterEvent, QPalette, QColor, QIcon, QPixmap
from PySide6.QtCore import Qt, QEvent, QSize, QEvent, QCoreApplication

from project_explorer.utility.typing import copy_method_params

from project_explorer.assets import close

from project_explorer.ui.flow_layout import FlowLayout
from project_explorer.ui.sorted_flow_container import SortedFlowContainer


def color_for_string(text: str, dark_mode: bool = True):
    hash_bytes = hashlib.md5(text.encode('utf-8')).digest()
    seed = int.from_bytes(hash_bytes, 'big')

    one, two = (seed & 2**8 - 1) / 2**8, ( (seed >> 8 ) & 2**8 - 1) / 2**8 

    h = int(255 * one)
    s = int(255* two)
    l = 100 if dark_mode else 230

    return f"hsl( {h},{s},{l} )"

class RemoveTagEvent(QEvent):
    tag: "Tag"

    s_type: int = QEvent.registerEventType()

    def __init__(self, tag: str):
        super().__init__(QEvent.Type(self.s_type))
        self.tag = tag

class Tag(QWidget):
    _editable: bool = False
    tag: str = ""

    @copy_method_params(QWidget.__init__)
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        self._update_stylesheet("")
        self.setObjectName("tag")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground) 
        self.setAutoFillBackground(True)

        layout = QHBoxLayout(self)

        layout.setContentsMargins(6,2,6,2)

        self.label = QLabel("")
        #self.label.setObjectName("tag")

        layout.addWidget(self.label)

        self.remove_button = QPushButton()
        self.remove_button.setIcon(QIcon(QPixmap(close)))
        self.remove_button.setContentsMargins(20,20,20,20)
        layout.addWidget(self.remove_button)

        self.remove_button.clicked.connect(lambda: QCoreApplication.sendEvent(self.parent(), RemoveTagEvent(self)))

        self.remove_button.setVisible(self._editable)

    def _update_stylesheet(self, tag: str):
        self.setStyleSheet(
            f"""
            *#tag{{ 
                background-color: {color_for_string(tag)};
                border-radius: 10px;
            }}

            QPushButton {{ 
                background-color: #00000000;
                border-radius: 6px;
            }}
            QPushButton:hover {{ 
                background-color: #77333333;
            }}
            """
        )

    def set_editable(self, editable: bool) -> Self:
        self._editable = editable
        self.remove_button.setVisible(self._editable)
        return self
    
    def set_tag(self, tag:str)->Self:
        self._update_stylesheet(tag)
        self.label.setText(tag)
        self.tag = tag
        return self
    


class TagList(SortedFlowContainer[str]):
    _editable: bool = False

    _tags: list[Tag]

    @copy_method_params(SortedFlowContainer.__init__)
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        self._tags = []

    def add_tag(self, tag:str):
        tag_widget = Tag().set_editable(self._editable).set_tag(tag)
        self._tags.append(tag_widget)
        self.insert(tag, tag_widget)

    def set_editable(self, editable: bool) -> Self:
        self._editable = editable

        for tag in self._tags:
            tag.set_editable(editable)

        return self
    
    def event(self, event: QEvent) -> bool:
        if event.type() == RemoveTagEvent.s_type:
            remove_tag_event = cast(RemoveTagEvent, event)

            self._tags.remove(remove_tag_event.tag)
            self.remove(remove_tag_event.tag.tag)
            remove_tag_event.tag.deleteLater()

            return True

        return super().event(event)

class ProjectTagList(QScrollArea):
    @copy_method_params(QScrollArea.__init__)
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        # Tag scroll area
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._collapse()

        self.setWidgetResizable(True)
        pal = QPalette()
        pal.setColor(QPalette.ColorRole.Window, "#00000000")
        self.setPalette(pal)
        self.setFrameShape(QFrame.Shape.NoFrame)

        # Tag container
        self.tag_container = TagList()
        self.tag_container.setPalette(pal)
        self.tag_container.layout().setContentsMargins(5, 0, 5, 0)
        self.tag_container.layout().setSpacing(4)

        self.setWidget(self.tag_container)

    def set_tags(self, tags: list[str]) -> None:
        self.tag_container.clear_all()
        
        for tag in tags:
            self.tag_container.add_tag(tag)

    def enterEvent(self, event: QEnterEvent) -> None:
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.verticalScrollBar().setEnabled(True)
        self.setMaximumHeight(200)
        return super().enterEvent(event)

    def _collapse(self) -> None:
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.verticalScrollBar().setEnabled(False)
        self.setMaximumHeight(24)
        self.verticalScrollBar().setValue(0)

    def leaveEvent(self, event: QEvent) -> None:
        self._collapse()
        return super().leaveEvent(event)


