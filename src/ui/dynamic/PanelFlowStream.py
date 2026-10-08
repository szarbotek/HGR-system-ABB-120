import random
from typing import Dict, Optional

from PyQt5.QtCore import QSize
from PyQt5.QtGui import QColor, QFont, QPainter, QPaintEvent, QPen
from PyQt5.QtWidgets import QSizePolicy, QWidget

from src.numeric.CircularBuffer import CircularBuffer
import src.Config as Config

class PanelFlowStream(QWidget):
    """
    Widget displaying temporal gesture sequences as color-coded bars on a black background
    with a minimalist timeline. Driven by a CircularBuffer storing stream samples.
    """

    DEFAULT_GESTURE_COLORS: Dict[Optional[str], QColor] = {
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
        Config.NONE_LABEL: QColor(32, 32, 32),
        None: QColor(15, 15, 15),
    }

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        max_samples: int = 60,
        sample_width_px: int = 8,
        panel_height_px: int = 50,
        timeline_segments: int = 2,
    ) -> None:
        super().__init__(parent=parent)

        self._max_samples: int = max_samples
        self._sample_width_px: int = sample_width_px
        self._panel_height_px: int = panel_height_px
        self._timeline_segments: int = max(1, timeline_segments)

        self.buffer: CircularBuffer[str] = CircularBuffer[str](
            max_length=self._max_samples
        )

        # Ustawiamy stałą politykę rozmiaru zarówno dla szerokości, jak i wysokości
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        self.time_refresh_ms: int = 10
        self.time_next_refresh_ms: int = 0

    def sizeHint(self) -> QSize:
        """Sugerowany wymiar dla QLayout przeliczany z próbki (szerokość x wysokość)."""
        calculated_width = self._max_samples * self._sample_width_px
        return QSize(calculated_width, self._panel_height_px)

    def set_max_samples(self, new_max_samples: int) -> None:
        """Zmienia liczbę próbek i wymusza przeliczenie wymiarów w QLayout."""
        if new_max_samples <= 0 or new_max_samples == self._max_samples:
            return

        self._max_samples = new_max_samples
        old_data = self.buffer.get_reverse_buffer()

        new_buffer = CircularBuffer[str](max_length=self._max_samples)
        for sample in old_data:
            new_buffer.put(sample)

        self.buffer = new_buffer

        self.updateGeometry()
        self.update()

    def set_sample_width(self, px_width: int) -> None:
        """Dynamiczna zmiana szerokości pojedynczego paska próbek."""
        if px_width > 0:
            self._sample_width_px = px_width
            self.updateGeometry()
            self.update()

    def set_panel_height(self, px_height: int) -> None:
        """Dynamiczna zmiana całkowitej wysokości panelu."""
        if px_height > 20:  # Zapewnia minimalne miejsce na osi czasu
            self._panel_height_px = px_height
            self.updateGeometry()
            self.update()

    def add_samples(self, labels: list[str]) -> None:
        if len(self.buffer) > 0:
            B = len(self.buffer)
            L = len(labels)
            if B >= L:
                trr = self.buffer[L-1:B]
                self.buffer.clear()
                self.buffer.extend(trr)
            else:
                self.buffer.clear()
        else:
            self.buffer.clear()
        self.buffer.extend( labels )

    def refresh(self, time_interval_ms: int) -> None:
        """Accumulates elapsed time and triggers redraw when reaching the frame

        threshold.
        """
        self.time_next_refresh_ms += time_interval_ms
        if self.time_next_refresh_ms >= self.time_refresh_ms:
            self.time_next_refresh_ms = 0
            self.update()

    # def random_refresh(self) -> None:
    #     available_gestures = [
    #         label
    #         for label in self.DEFAULT_GESTURE_COLORS.keys()
    #         if label is not None
    #     ]
    #     self.buffer.clear()
    #     for _ in range(self._max_samples):
    #         self.buffer.put(random.choice(available_gestures))
    #     self.update()

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, False)

        w = self.width()
        h = self.height()

        timeline_height = 18
        chart_height = max(1, h - timeline_height)

        # Czarne tło
        painter.fillRect(0, 0, w, h, QColor(0, 0, 0))

        samples = self.buffer.get_reverse_buffer()

        # Rysowanie próbek
        if self._max_samples > 0:
            box_width = self._sample_width_px
            gap = 1 if box_width > 4 else 0

            for i, label in enumerate(samples):
                color = self.DEFAULT_GESTURE_COLORS.get(
                    label, self.DEFAULT_GESTURE_COLORS["None"]
                )

                x_pos = (self._max_samples - len(self.buffer) + i) * box_width
                rect_w = max(1, box_width - gap)

                # Wysokość słupka dopasowuje się do zadanej wysokości wykresu (chart_height)
                painter.fillRect(x_pos, 2, rect_w, int(chart_height - 4), color)

        # Oś czasu
        self._draw_timeline(painter, w, h, chart_height, timeline_height)

    def _draw_timeline(
        self,
        painter: QPainter,
        width: int,
        height: int,
        chart_h: int,
        timeline_h: int,
    ) -> None:
        pen = QPen(QColor(80, 80, 80))
        pen.setWidth(1)
        painter.setPen(pen)

        painter.drawLine(0, chart_h, width, chart_h)

        font = QFont("Monospace", 7)
        painter.setFont(font)

        step_px = width / self._timeline_segments
        for i in range(self._timeline_segments + 1):
            x = int(i * step_px)
            if i == self._timeline_segments:
                x -= 1
            painter.drawLine(x, chart_h, x, chart_h + 4)

        painter.setPen(QColor(140, 140, 140))
        painter.drawText(2, height - 3, f"-{self._max_samples/10:.2f} s")
        painter.drawText(max(0, int(width/2) - 16), height - 3,  f"-{self._max_samples/10/2:.2f} s")
        painter.drawText(max(0, width - 32), height - 3, "NOW")