"""
    Custom push button component with selection-aware custom rendering.
"""

from typing import Dict, Optional
from PyQt5.QtWidgets import QPushButton, QWidget
from PyQt5.QtGui import QPainter, QPen, QColor, QBrush, QPaintEvent
from PyQt5.QtCore import Qt, QRectF

from application.ui.components.jumping_machine import JumpingMachine


class JpPushButton(QPushButton, JumpingMachine):
    """
        Push button widget rendering custom borders and background state styles.

        :param parent: Parent widget, defaults to None.
    """

    thickness: int = 5

    color_mode: Dict[bool, QColor] = {
        False: QColor(0, 0, 0),
        True: QColor(255, 0, 0),
    }

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """
            Initialize button state, default colors, and base components.
        """
        super().__init__(text="None", parent=parent, parentJP=parent, instanceJP=self)

        self.FLAG_is_object_selected: bool = False
        self.color_normal: QColor = QColor(34, 198, 78)
        self.color_selected: QColor = QColor(255, 0, 0)

    def paintEvent(self, event: QPaintEvent) -> None:
        """
            Draw rounded background, selection border, and centered text label.

            :param event: Qt paint event trigger.
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        is_pressed = self.isDown()
        border_color = self.color_mode[self.FLAG_is_object_selected]
        bg_color = self.color_selected if is_pressed else self.color_normal

        offset = self.thickness / 2
        rect = QRectF(self.rect()).adjusted(offset, offset, -offset, -offset)

        painter.setBrush(QBrush(bg_color))
        pen = QPen(border_color)
        pen.setWidth(self.thickness)
        painter.setPen(pen)

        painter.drawRoundedRect(rect, 10.0, 10.0)

        ## przycisk
        if is_pressed:
            painter.translate(0, 1)

        painter.setPen(QColor(255, 255, 255))
        painter.setFont(self.font())
        painter.drawText(self.rect(), Qt.AlignCenter, self.text())