"""
    Custom log output widget built on top of QPlainTextEdit.
"""

from typing import Optional
from PyQt5.QtWidgets import QPlainTextEdit, QWidget


class LogsBox(QPlainTextEdit):
    """Read-only text console designed for displaying application logs.

    Provides automatic styling and text refreshing while maintaining cursor position
    and vertical scroll state.

    :param parent: Parent widget, defaults to None.
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Initialize read-only state, font formatting, and component stylesheets."""
        super().__init__(parent=parent)

        self.setReadOnly(True)
        self.setStyleSheet("""
            QPlainTextEdit {
                background-color: white;
                color: black;
                font-family: Consolas;
                font-size: 10pt;
            }
        """)

    def refresh(self, new_text: str) -> None:
        """Replace widget text content while preserving scrollbar and cursor positions.

        :param new_text: New string content to populate in the console.
        """
        cursor = self.textCursor()
        old_position = cursor.position()
        scrollbar = self.verticalScrollBar()
        scrollbar_pos = scrollbar.value()

        self.setPlainText(new_text)

        new_cursor = self.textCursor()
        new_cursor.setPosition(min(old_position, len(new_text)))
        self.setTextCursor(new_cursor)

        scrollbar.setValue(min(scrollbar_pos, scrollbar.maximum()))