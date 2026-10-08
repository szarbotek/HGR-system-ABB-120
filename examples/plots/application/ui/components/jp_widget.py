"""
    Custom container widget with selection-aware rounded borders.
"""

from typing import Dict, Optional

from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QPen, QColor, QBrush, QPaintEvent
from PyQt5.QtCore import QRectF

from src.application.ui.components.jumping_machine import JumpingMachine


class JpWidget(QWidget, JumpingMachine):
    """
        Container widget rendering a rounded box with dynamic selection borders.

        :param parent: Parent widget, defaults to None.
    """

    thickness: int = 2

    color_mode: Dict[bool, QColor] = {
        False: QColor(255, 255, 255),
        True: QColor(255, 0, 0),
    }

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """
            Initialize the custom widget and set default color attributes.
        """
        super().__init__(parent=parent, parentJP=parent, instanceJP=self)

        self.backgroundColor: QColor = QColor(255, 255, 255)
        self.FLAG_is_object_selected: bool = False

    def setBgColor(self, color: QColor | str):
        if isinstance(color, str):
            self.backgroundColor= QColor(color)
        elif isinstance(color, QColor):
            self.backgroundColor = color
        else:
            raise TypeError


    def paintEvent(self, event: QPaintEvent) -> None:
        """
            Render background fill

            :param event: Qt paint event trigger.
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        color_border = self.color_mode[self.FLAG_is_object_selected]
        half = self.thickness / 2

        rect = QRectF(self.rect()).adjusted(half, half, -half, -half)

        painter.setBrush(QBrush(self.backgroundColor))

        pen = QPen(color_border)
        pen.setWidth(self.thickness)
        painter.setPen(pen)
        painter.drawRect(rect)
        # painter.drawRoundedRect(rect, 10.0, 10.0)
