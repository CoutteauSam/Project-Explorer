"""UI code for showing image thumbnails"""

from pathlib import Path
from tkinter import (
    Scrollbar,
    Canvas,
    Frame,
    Label,
)

from PIL import Image, ImageTk


# pylint: disable=too-few-public-methods
class Thumbnails:
    """UI element displaying the thumbnails of a project"""

    def __init__(self, parent: Frame) -> None:
        self.parent = parent

        self.frame = Frame(parent)
        self.frame.pack(side="right", fill="y", padx=5, pady=5)

        self.images: list[ImageTk.PhotoImage] = []

        self.label = Label(self.frame, text="Thumbnails:")
        self.label.pack(anchor="w")

        self.thumb_canvas = Canvas(self.frame, width=300)
        self.thumb_canvas.pack(side="left", fill="y")

        self.scrollbar = Scrollbar(
            self.frame, orient="vertical", command=self.thumb_canvas.yview
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

    def load_thumbnails(self, path: Path | None) -> None:
        """Load new thumbnails from a given path"""

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
