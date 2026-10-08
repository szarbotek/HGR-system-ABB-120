"""
    Circular buffer visualizer widget for Qt interface components.
"""

from typing import List, Literal, Optional, Sequence
from PyQt5.QtCore import QRectF, Qt
from PyQt5.QtGui import QBrush, QColor, QFont, QFontMetrics, QPaintEvent, QPainter, QPen
from PyQt5.QtWidgets import QWidget

from src.utils.Logs import Logs

class WordQueue(QWidget):
    """Widget displaying a circular buffer queue of strings in horizontal or vertical layouts.

    Renders items inside rounded containment boxes aligned to a specified widget edge.

    :param parent: Parent widget container, defaults to None.
    :param max_place_box: Maximum number of element slots rendered in the view, defaults to 5.
    :param stick_to_side: Alignment orientation ('Left', 'Right', 'Up', 'Down', or ''), defaults to 'Left'.
    """

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        max_place_box: int = 10,
        max_chars: int = 12,
        stick_to_side: Literal["Right", "Left", "", "Up", "Down"] = "Left",
    ) -> None:
        super().__init__(parent=parent)

        self.data: List[str] = []
        self.max_place_box: int = max(1, max_place_box)
        self.max_chars: int = max(1, max_chars)

        self.stick_to_side: Literal["Right", "Left", "", "Up", "Down"] = (
            stick_to_side if stick_to_side in ["Right", "Left", "Up", "Down"] else "Left"
        )

        self.color_background: QColor = QColor("#2b2d42")
        self.color_border: QColor = QColor("#8d99ae")
        self.color_slot_bg: QColor = QColor("#B8C7D6")
        self.color_slot_border: QColor = QColor("#d90429")
        self.color_text: QColor = QColor("#2b2d42")

        self.font_family: str = "Segoe UI"

    def new_data(self, dataset: Sequence[str], text_f: str = r"{}") -> None:
        """Update buffer data items and trigger a view repaint."""
        try:
            if not isinstance(dataset, Sequence):
                raise TypeError(f"<ERR:{self.__class__.__name__}> Expected a Sequence instance.")

            self.data = [text_f.format(d) for d in dataset]
            self.update()
        except Exception as e:
            Logs.print(f"\n<ERR:{self.__class__.__name__}>", e, dataset, text_f)

    def paintEvent(self, event: QPaintEvent) -> None:
        """Render the background and text elements without borders."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 1. Pobieramy RZECZYWISTE wymiary widgetu
        w = float(self.width())
        h = float(self.height())

        if w <= 0 or h <= 0:
            return

        # 2. Tło główne dostosowane do pełnego okna widgetu
        bg_rect = QRectF(0.0, 0.0, w, h)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(self.color_background))
        painter.drawRoundedRect(bg_rect, 10.0, 10.0)

        if not self.data or self.max_place_box <= 0:
            return

        # 3. Określenie wymiarów pojedynczego slotu
        is_horizontal = self.stick_to_side in ["Left", "Right"]

        if is_horizontal:
            box_w = w / self.max_place_box
            box_h = h
        else:
            box_w = w
            box_h = h / self.max_place_box

        padd = 5.0
        padd2 = padd * 2.0
        slot_h = box_h - padd2

        font_size = max(7, int(slot_h * 0.40))
        font = QFont(self.font_family, font_size, QFont.Bold)
        painter.setFont(font)
        metrics = QFontMetrics(font)

        items_to_draw = self.data[: self.max_place_box]

        # 5. Rysowanie komórek z tekstem
        for i, word in enumerate(items_to_draw):
            # Obliczanie pozycji slotu
            if self.stick_to_side == "Left":
                x = box_w * i
                y = 0.0
            elif self.stick_to_side == "Right":
                x = w - (box_w * (i + 1))
                y = 0.0
            elif self.stick_to_side == "Up":
                x = 0.0
                y = box_h * i
            else:  # Down
                x = 0.0
                y = h - (box_h * (i + 1))

            slot_rect = QRectF(x + padd, y + padd, box_w - padd2, slot_h)

            # Rysowanie tła slotu (bez ramki)
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(self.color_slot_bg))
            painter.drawRoundedRect(slot_rect, 6.0, 6.0)

            # Przycinanie tekstu do max_chars
            display_text = str(word)
            if len(display_text) > self.max_chars:
                display_text = display_text[: self.max_chars - 1] + "…"

            # Dopisanie elipsy (…), jeśli tekst fizycznie nie mieści się w komórce
            elided_text = metrics.elidedText(
                display_text,
                Qt.ElideRight,
                int(slot_rect.width() - 8),
            )

            # Rysowanie tekstu
            painter.setPen(self.color_text)
            painter.drawText(
                slot_rect,
                Qt.AlignCenter,
                elided_text,
            )
