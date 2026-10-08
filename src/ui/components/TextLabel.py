from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor, QPalette
from PyQt5.QtWidgets import QLabel
from typing import Literal

class TextLabel(QLabel):
    """Custom label with transparent background, no border, and customizable alignment, font, and color."""

    def __init__(
        self,
        text: str = "",
        font_name: str = "Arial",
        font_size: int = 12,
        text_color: str = "#ffffff",
        alignment: Literal["left", "right", "center"] = "center",
        parent=None
    ):
        """
        Initialize the text label.

        :param text: Text to display, defaults to "".
        :param font_name: Font family name, defaults to "Arial".
        :param font_size: Font point size, defaults to 10.
        :param text_color: Color of the text in hex or named color format, defaults to "#000000".
        :param alignment: Text alignment ("left", "right", "center"), defaults to "left".
        :param parent: Parent widget, defaults to None.
        """
        super().__init__(text, parent)

        # Store properties
        self.font_name = font_name
        self.font_size = font_size
        self.text_color_val = text_color
        self.alignment_val = alignment

        # Configure appearance
        self.custom_font = QFont(self.font_name, self.font_size)
        self.setFont(self.custom_font)

        # Set transparent background and remove borders
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setFrameStyle(QLabel.NoFrame)

        # Set text color and alignment
        self.set_text_color(self.text_color_val)
        self.set_alignment_by_str(self.alignment_val)

    def set_alignment_by_str(self, alignment: str):
        """
        Set text alignment using a string value.

        :param alignment: Alignment direction ("left", "right", "center").
        """
        self.alignment_val = alignment
        align_map = {
            "left": Qt.AlignLeft | Qt.AlignVCenter,
            "right": Qt.AlignRight | Qt.AlignVCenter,
            "center": Qt.AlignCenter
        }
        self.setAlignment(align_map.get(alignment.lower(), Qt.AlignLeft | Qt.AlignVCenter))

    def set_text_color(self, color: str):
        """
        Update the label text color.

        :param color: Color in hex or named format (e.g. "#FF0000" or "red").
        """
        self.text_color_val = color
        palette = self.palette()
        palette.setColor(QPalette.WindowText, QColor(self.text_color_val))
        self.setPalette(palette)

    def set_font_properties(self, font_name: str, font_size: int):
        """
        Update the font family and size.

        :param font_name: Font family name.
        :param font_size: Font point size.
        """
        self.font_name = font_name
        self.font_size = font_size
        self.custom_font = QFont(self.font_name, self.font_size)
        self.setFont(self.custom_font)