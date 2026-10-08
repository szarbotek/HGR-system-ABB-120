"""
    Camera display widget integrated with frame and landmark buffering capabilities.
"""

import traceback
from typing import Dict, Any, List, Tuple, Optional

from PyQt5.QtWidgets import QLabel, QWidget
from PyQt5.QtGui import QImage, QPixmap, QColor, QPainter, QPen
from PyQt5.QtCore import Qt

from src.application.utils.structure import CircularBuffer
from src.application.ui.components.jumping_machine import JumpingMachine


class JpCameraScreen(QLabel, JumpingMachine):
    """
        Camera screen widget that renders video frames and hand landmarks.

        :param parent: Parent widget, defaults to None.
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """
            Initialize the camera display screen and set default attributes.
        """
        super().__init__(parent=parent, parentJP=parent, instanceJP=self)

        self.setParent(parent)
        self.setText("Brak danych")

        self.frame_data: CircularBuffer = CircularBuffer(60)
        self.landmarks_data: CircularBuffer = CircularBuffer(60)

        self.time_next_frame: int = 0
        self.time_next_landmarks: int = 0

        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("color: white; background-color: black;")

        self.active_landmarks: Dict[str, List[Tuple[int, int]]] = {
            "Right": [],
            "Left": [],
        }

        self.FLAG_draw_landmarks: bool = True

    def padding(self, value: int) -> None:
        """
            Apply inner geometry margin by adjusting position and dimensions.
            :param value: Margin offset value in pixels.
        """
        pos = self.pos()
        x, y = pos.x(), pos.y()
        self.setGeometry(x + value, y + value, self.width() - 2 * value, self.height() - 2 * value)

    def new_frame(self, timestamp_ms: int, frame) -> None:
        """
            Push a new frame entry into the frame buffer.

            :param timestamp_ms: Frame presentation timestamp in milliseconds.
            :param frame: Raw image array.
        """
        self.frame_data.put((timestamp_ms, frame))

    def new_landmarks(self, timestamp_ms: int, landmarks: Dict[str, Any]) -> None:
        """
            Push a new landmark entry into the landmarks buffer.

            :param timestamp_ms: Landmark detection timestamp in milliseconds.
            :param landmarks: Dictionary mapping hand side to landmark points.
        """
        self.landmarks_data.put((timestamp_ms, landmarks))

    def refresh(self, time_intervl_ms: int) -> None:
        """
            Update timers and pop ready frames/landmarks from buffers for rendering.

            :param time_intervl_ms: Time interval passed since last refresh in milliseconds.
        """
        try:
            self.time_next_frame += time_intervl_ms
            self.time_next_landmarks += time_intervl_ms

            if len(self.landmarks_data) > 0:
                timestamp, _ = self.landmarks_data.last
                if self.time_next_landmarks >= timestamp:
                    self.time_next_landmarks -= timestamp
                    _, landmarks = self.landmarks_data.throw()
                    self.update_landmarks(landmarks)

            if len(self.frame_data) > 0:
                timestamp, _ = self.frame_data.last
                if self.time_next_frame >= timestamp:
                    self.time_next_frame -= timestamp
                    _, frame = self.frame_data.throw()
                    self.update_screen(frame)

        except Exception as e:
            print(f"<ERR> JpCameraScreen refresh : {e}")
            print(traceback.format_exc())

    def update_screen(self, frame) -> None:
        """
            Convert array frame to pixmap, overlay landmarks if enabled, and display.

            :param frame: Input image NumPy array to render.
        """
        try:
            h, w, ch = frame.shape
            bytes_per_line = ch * w
            qimg = QImage(frame.landmarks, w, h, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qimg)
            scaled_pixmap = pixmap.scaled(self.size(), Qt.KeepAspectRatio)

            if self.FLAG_draw_landmarks:
                painter = QPainter(scaled_pixmap)
                pen = QPen(QColor('red'))
                pen.setWidth(5)
                painter.setPen(pen)

                for lk in self.active_landmarks.values():
                    for p in lk:
                        DX, DY = p
                        painter.drawPoint(DX, DY)
                painter.end()

            self.setPixmap(scaled_pixmap)
        except Exception as e:
            print(f"<ERR> JpCameraScreen update screen: {e}, {frame}")
            print(traceback.format_exc())

    def update_landmarks(self, landmarks: Dict[str, Any]) -> None:
        """
            Scale normalized landmark coordinates to widget dimensions.

            :param landmarks: Dictionary mapping hand side to landmark coordinate objects.
        """
        try:
            sw = self.width()
            sh = self.height()

            for st, lk in landmarks.items():
                if lk is None:
                    self.active_landmarks[st] = []
                    continue
                else:
                    self.active_landmarks[st] = [
                        (
                            int(sw * p.x),
                            int(sh * p.y),
                        )
                        for p in lk
                    ]

        except Exception as e:
            print(f"<ERR> JpCameraScreen update landmarks: {e}, {landmarks}")

