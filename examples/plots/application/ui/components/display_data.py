"""
    Widget for displaying key-value data in a PyQt5 interface.
"""

from typing import Dict, Any, Optional
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QColor, QFont, QPen, QPaintEvent
from PyQt5.QtCore import Qt, QRectF


class DisplayData(QWidget):
    """
        Widget that renders a key-value dictionary as a rounded grid.

        :param parent: Parent widget, defaults to None.
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Initialize the widget with default style parameters."""
        super().__init__(parent=parent)

        self.background_color: QColor = QColor(172, 83, 30)
        self.box_color: QColor = QColor(255, 255, 255)

        self.padding: int = 10
        self.spacing: int = 10
        self.font_size: int = 8

        self.ferdieling: float = 0.5
        self.data: Dict[str, Any] = {}

    def set_data(self, data_dict: Dict[str, Any]) -> None:
        """
            Replace current data dictionary and trigger a redraw.
            :param data_dict: Dictionary containing key-value pairs.
        """
        self.data = data_dict
        self.update()

    def update_data(self, data_dict: Dict[str, Any]) -> None:
        """
            Update values for existing keys in the dataset.

            :param data_dict: Dictionary with updated key-value pairs.
        """
        for key, value in data_dict.items():
            if key in self.data:
                self.data[key] = str(value)
        self.update()

    def paintEvent(self, event: QPaintEvent) -> None:
        """
            Paint background, data cells, and text onto the widget.

            :param event: Paint event object.
            :type event: QPaintEvent
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        painter.setBrush(self.background_color)
        painter.setPen(QPen(Qt.black, 2))
        painter.drawRect(self.rect().adjusted(1, 1, -1, -1))

        if not self.data:
            return

        rows = len(self.data)
        cell_width = self.width() - (2 * self.padding) - self.spacing
        cell_height = (self.height() - (2 * self.padding) - ((rows - 1) * self.spacing)) / rows

        cell_width_left = int((1.0 - self.ferdieling) * cell_width)
        cell_width_right = int(self.ferdieling * cell_width)

        painter.setFont(QFont("Segoe UI", self.font_size, QFont.Bold))
        margin = 5

        for i, (key, value) in enumerate(self.data.items()):
            y_offset = self.padding + i * (cell_height + self.spacing)

            left_rect = QRectF(self.padding, y_offset, cell_width_left, cell_height)
            right_rect = QRectF(
                self.padding + cell_width_left + self.spacing,
                y_offset,
                cell_width_right,
                cell_height,
            )

            left_rect_area = left_rect.adjusted(margin, 0, -margin, 0)
            right_rect_area = right_rect.adjusted(margin, 0, -margin, 0)

            painter.setBrush(self.box_color)
            painter.setPen(QPen(Qt.black, 2))
            painter.drawRoundedRect(left_rect, 10, 10)
            painter.drawRoundedRect(right_rect, 10, 10)

            painter.setPen(Qt.black)
            painter.drawText(left_rect_area, Qt.AlignCenter, str(key))
            painter.drawText(right_rect_area, Qt.AlignCenter, str(value))