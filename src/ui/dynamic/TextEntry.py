from typing import Literal
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor, QPalette
from PyQt5.QtWidgets import QLineEdit


class TextEntry(QLineEdit):
    """Custom text input field with configurable font, colors, and focus handling."""

    def __init__(
        self,
        text: str = "",
        placeholder: str = "",
        font_name: str = "Arial",
        font_size: int = 10,
        text_color: str = "#000000",
        bg_color: str = "#FFFFFF",
        border_color: str = "#CCCCCC",
        alignment: Literal["left", "right", "center"] = "left",
        parent=None
    ):
        """
        Initialize the text entry field.

        :param text: Initial text content, defaults to "".
        :param placeholder: Placeholder text shown when empty, defaults to "".
        :param font_name: Font family name, defaults to "Arial".
        :param font_size: Font point size, defaults to 10.
        :param text_color: Text color in hex or named format, defaults to "#000000".
        :param bg_color: Background color in hex or named format, defaults to "#FFFFFF".
        :param border_color: Border color when inactive, defaults to "#CCCCCC".
        :param alignment: Text alignment ("left", "right", "center"), defaults to "left".
        :param parent: Parent widget, defaults to None.
        """
        super().__init__(text, parent)

        # Store configuration properties
        self.font_name: str = font_name
        self.font_size: int = font_size
        self.text_color_val: str = text_color
        self.bg_color_val: str = bg_color
        self.border_color_val: str = border_color
        self.alignment_val: Literal["left", "right", "center"] = alignment

        # Setup font and placeholder
        self.custom_font = QFont(self.font_name, self.font_size)
        self.setFont(self.custom_font)
        if placeholder:
            self.setPlaceholderText(placeholder)

        # Apply alignment
        self.set_alignment_by_str(self.alignment_val)

        # Apply default styling
        self.update_style()

    def set_alignment_by_str(self, alignment: Literal["left", "right", "center"]):
        """
        Set text alignment using a string value.

        :param alignment: Alignment direction ("left", "right", "center").
        """
        self.alignment_val = alignment
        align_map = {
            "left": Qt.AlignLeft,
            "right": Qt.AlignRight,
            "center": Qt.AlignCenter
        }
        self.setAlignment(align_map.get(alignment.lower(), Qt.AlignLeft))

    def update_style(self, focused: bool = False):
        """
        Update stylesheet based on input focus state.

        :param focused: State flag indicating if the widget has focus.
        """
        border_col = "#2ECC71" if focused else self.border_color_val
        self.setStyleSheet(f"""
            QLineEdit {{
                background-color: {self.bg_color_val};
                color: {self.text_color_val};
                border: 1px solid {border_col};
                border-radius: 4px;
                padding: 4px 8px;
            }}
        """)

    def focusInEvent(self, event):
        """
        Handle focus enter event (clicking or tabbing into the field).

        :param event: Focus event object.
        """
        super().focusInEvent(event)
        self.update_style(focused=True)

    def focusOutEvent(self, event):
        """
        Handle focus leave event (clicking outside or switching focus).

        :param event: Focus event object.
        """
        super().focusOutEvent(event)
        self.update_style(focused=False)