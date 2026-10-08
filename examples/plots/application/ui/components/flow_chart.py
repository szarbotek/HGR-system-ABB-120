"""
    FlowChart widget for visualizing gesture sequence streams in PyQt5.
"""

from typing import List, Optional
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QColor, QPaintEvent
from PyQt5.QtCore import Qt


class FlowChart(QWidget):
    """
        Widget displaying temporal gesture sequences as color-coded bars.

        :param parent: Parent widget, defaults to None.
        :param max_segments: Number of major segments, defaults to 3.
        :param segment_per_box: Boxes per segment, defaults to 1.
    """

    gesture_colors = {
        "call": QColor(255, 0, 150),
        "dislike": QColor(100, 60, 20),
        "fist": QColor(0, 0, 255),
        "grip": QColor(0, 255, 0),
        "like": QColor(255, 200, 150),
        "little_finger": QColor(0, 100, 0),
        "one": QColor(255, 255, 0),
        "peace": QColor(255, 150, 50),
        "rock": QColor(130, 0, 255),
        "stop": QColor(128, 128, 128),
        "three": QColor(255, 50, 50),
        "three3": QColor(150, 0, 70),
        "thumb_index": QColor(0, 255, 255),
        "None": QColor(32, 32, 32),
        None: QColor(0, 0, 0),
    }

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        max_segments: int = 3,
        segment_per_box: int = 1,
    ) -> None:
        """
            Initialize the FlowChart widget with custom dimensions and buffers.
        """
        super().__init__(parent=parent)

        self.max_segments: int = max_segments
        self.segment_per_box: int = segment_per_box
        self.max_boxs: int = self.max_segments * self.segment_per_box

        self.data: List[str] = []

        self.time_refresh_ms: int = 100
        self.time_next_refresh_ms: int = 0

    def new_data(self, dataset: List[str]) -> None:
        """
            Replace the dataset with a list of gesture label strings.

            :param dataset: List of valid gesture label strings.
            :raises TypeError: If dataset or any of its items are not strings.
        """
        assert isinstance(dataset, list), TypeError(self.__class__.__name__)
        assert all(isinstance(_, str) for _ in dataset), TypeError(self.__class__.__name__)

        self.data = dataset

    def refresh(self, time_interval_ms: int) -> None:
        """
            Accumulate elapsed time and trigger a redraw when reaching threshold.

            :param time_interval_ms: Time passed since last update in milliseconds.
        """
        self.time_next_refresh_ms += time_interval_ms

        if self.time_next_refresh_ms >= self.time_refresh_ms:
            self.update()

    def paintEvent(self, event: QPaintEvent) -> None:
        """
            Render background and color-coded gesture bars onto the widget canvas.

            :param event: Qt paint event trigger.
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        width = self.width()
        height = self.height()

        box_width = width / self.max_boxs
        d = 2

        painter.setBrush(FlowChart.gesture_colors["None"])
        painter.drawRect(0, 0, width, height)

        for i, label in enumerate(self.data):
            color = FlowChart.gesture_colors.get(label, FlowChart.gesture_colors["None"])
            painter.setBrush(color)
            painter.setPen(Qt.NoPen)

            x_pos = int(i * box_width)
            current_w = width - (int((i + 1) * box_width) - x_pos)

            painter.drawRect(x_pos, d, current_w, height - 2 * d)