"""
    Circular buffer visualizer widget for Qt interface components.
"""

from typing import List, Literal, Sequence, Optional
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QFont, QPainter, QPen, QColor, QBrush, QPaintEvent
from PyQt5.QtCore import Qt, QRect, QRectF


class WordQueue(QWidget):
    """
        Widget displaying a circular buffer queue of strings in horizontal or vertical layouts.

        Renders items inside rounded containment boxes aligned to a specified widget edge.

        :param parent: Parent widget container, defaults to None.
        :param max_place_box: Maximum number of element slots rendered in the view, defaults to 5.
        :param stick_to_side: Alignment orientation ('Left', 'Right', 'Up', 'Down', or ''), defaults to 'Left'.
    """

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        max_place_box: int = 5,
        stick_to_side: Literal["Right", "Left", "", "Up", "Down"] = "Left",
    ) -> None:
        """
            Initialize component dimensions, colors, and layout configurations.
        """
        super().__init__(parent=parent)

        self.data: List[str] = []
        self.max_place_box: int = max_place_box
        self.stick_to_side: Literal["Right", "Left", "", "Up", "Down"] = stick_to_side

        self.color_background: QColor = QColor("#ff0000")
        self.font_size: int = 8

    def new_data(self, dataset: Sequence[str], text_f: str = r"{}") -> None:
        """
            Update buffer data items and trigger a view repaint.

            :param dataset: Collection of string tokens or values to insert into the view.
            :param text_f: Format string template applied to each element, defaults to r"{}".
        """
        try:
            if not isinstance(dataset, Sequence):
                raise TypeError(f"<ERR:{self.__class__.__name__}> Expected a Sequence instance.")

            self.data = [text_f.format(d) for d in dataset]
            self.update()
        except Exception as e:
            print(f"\n<ERR:{self.__class__.__name__}>", e, dataset, text_f)

    def paintEvent(self, event: QPaintEvent) -> None:
        """
            Render the background frame and array of queue slot elements.

            :param event: Qt paint event trigger.
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        width = self.width()
        height = self.height()

        # Render background frame
        rect = QRectF(self.rect())
        painter.setBrush(QBrush(self.color_background))
        pen = QPen(QColor(255, 255, 255))
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawRoundedRect(rect, 15.0, 15.0)

        # Calculate slot dimensions based on layout orientation
        if self.stick_to_side in ["Right", "Left"]:
            box_width = int(width / self.max_place_box)
            box_height = height
        else:
            box_width = width
            box_height = int(height / self.max_place_box)

        padd = 5
        padd2 = padd * 2

        # Draw individual buffer items
        for i, word in enumerate(self.data[: self.max_place_box]):
            x = 0
            y = 0

            if self.stick_to_side == "Left":
                x = box_width * i
                y = 0
            elif self.stick_to_side == "Right":
                x = width - (box_width * (i + 1))
                y = 0
            elif self.stick_to_side == "Up":
                x = 0
                y = box_height * i
            elif self.stick_to_side == "Down":
                x = 0
                y = height - (box_height * (i + 1))

            slot_rect = QRect(x + padd, y + padd, box_width - padd2, box_height - padd2)

            # Draw slot container box
            painter.setPen(QPen(QColor(0, 0, 0), 2))
            painter.setBrush(QColor(255, 255, 255))
            painter.drawRoundedRect(slot_rect, 10.0, 10.0)

            # Draw text label
            painter.setPen(QColor(0, 0, 0))
            painter.setFont(QFont("Segoe UI", self.font_size, QFont.Bold))
            painter.drawText(slot_rect, Qt.AlignCenter, word)