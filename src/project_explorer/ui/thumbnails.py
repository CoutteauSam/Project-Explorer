"""UI code for showing image thumbnails"""

from tkinter import (
    Scrollbar,
    Canvas,
    Frame,
    Label,
)
from typing import Any

from PIL import Image, ImageTk

from project_explorer.utility.typing import copy_method_params

from project_explorer.model.projects import ProjectsModel


# pylint: disable=too-few-public-methods
class Thumbnails(Frame):
    """UI element displaying the thumbnails of a project"""

    model: ProjectsModel | None = None

    @copy_method_params(Frame.__init__)
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        self.images: list[ImageTk.PhotoImage] = []

        self.label = Label(self, text="Thumbnails:")
        self.label.pack(anchor="w")

        self.thumb_canvas = Canvas(self, width=300)
        self.thumb_canvas.pack(side="left", fill="y")

        self.scrollbar = Scrollbar(
            self, orient="vertical", command=self.thumb_canvas.yview
        )
        self.scrollbar.pack(side="right", fill="y")

        self.thumb_canvas.configure(yscrollcommand=self.scrollbar.set)

        self.thumb_inner = Frame(self.thumb_canvas)
        self.thumb_canvas.create_window((0, 0), window=self.thumb_inner, anchor="nw")

        self.thumb_inner.bind(
            "<Configure>",
            lambda e: self.thumb_canvas.configure(
                scrollregion=self.thumb_canvas.bbox("all")
            ),
        )

    def set_model(self, model: ProjectsModel | None) -> None:
        """Sets the ui model for this widget"""
        self.model = model
        self._load_thumbnails()

        if model is None:
            return

        model.project_selected.listen(lambda _: self._load_thumbnails())

    def _load_thumbnails(self) -> None:
        """Load new thumbnails from a given path"""

        # pylint: disable=duplicate-code
        if self.model is None:
            return

        path = self.model.get_project_under_edit()

        if path is None:
            return

        for widget in self.thumb_inner.winfo_children():
            widget.destroy()

        self.images.clear()

        if path is None:
            return

        thumbnails_path = path / "thumbnails"

        if thumbnails_path.exists() and thumbnails_path.is_dir():
            for image_path in thumbnails_path.iterdir():
                if not image_path.is_file():
                    continue

                img = Image.open(image_path)

                img.thumbnail((280, 280))
                tk_img = ImageTk.PhotoImage(img)
                self.images.append(tk_img)
                lbl = Label(self.thumb_inner, image=tk_img)
                lbl.pack(pady=4)
