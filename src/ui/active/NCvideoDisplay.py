import traceback
from typing import Dict, Any, List, Tuple, Optional

import cv2
import numpy as np
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QImage, QPainter, QPen, QColor
from PyQt5.QtWidgets import QWidget

from src.numeric.CircularBuffer import CircularBuffer
from src.ui.active.NavigationCursor import NavigationCursor
from src.ui.Styles import Styles
import src.Config as Config
from src.utils.Logs import Logs

class NCvideoDisplay(QWidget, NavigationCursor):
    """
        PyQt5 component for rendering video frames and hand landmarks.
        Combines QPainter rendering performance with JpCameraScreen buffering and synchronization mechanisms.
    """

    RESOLUTIONS = {
        "720p": 720,
        "480p": 480,
        "360p": 360,
    }

    def __init__(
        self,
        navigation_parent: Optional[QWidget],
        resolution: str = "780p",
        scale_factor: float = 1.0,
        buffer_size: int = 60,
    ) -> None:
        """
        Initialize the camera display screen.
        """
        # Base classes initialization
        QWidget.__init__(self, parent=navigation_parent)
        NavigationCursor.__init__(self, navigation_parent=navigation_parent)

        self.setStyleSheet("background-color: black;")

        # Scaling and resolution settings
        self.target_height: Optional[int] = self.RESOLUTIONS.get(resolution, None)
        self.scale_factor: float = max(0.1, min(scale_factor, 1.0))

        # Circular buffers for frames and landmarks (from JpCameraScreen)
        self.frame_data: CircularBuffer = CircularBuffer(buffer_size)
        self.landmarks_data: CircularBuffer = CircularBuffer(buffer_size)

        # Time synchronization counters
        self.time_next_frame: int = 0
        self.time_next_landmarks: int = 0

        # Image and active landmarks scaled to pixel coordinates
        self._qimage: Optional[QImage] = None
        self.last_timestamp: int = 0

        self.active_landmarks: Dict[str, List[Tuple[int, int]]] = {
            "Right": [],
            "Left": [],
        }

        self.FLAG_draw_landmarks: bool = True

    # --- Interface and Geometry Settings ---

    def set_resolution(self, resolution: str) -> None:
        """Set target resolution ("720p", "480p", "360p", or "native")."""
        self.target_height = self.RESOLUTIONS.get(resolution, None)

    def set_scale_factor(self, scale_factor: float) -> None:
        """Set scaling factor for the rendered image."""
        self.scale_factor = max(0.1, min(scale_factor, 1.0))
        self.update()

    def padding(self, value: int) -> None:
        """Apply inner geometry margin by adjusting widget position and dimensions."""
        pos = self.pos()
        self.setGeometry(pos.x() + value, pos.y() + value, self.width() - 2 * value, self.height() - 2 * value)

    # --- Buffer Ingestion ---
    def new_frame(self, timestamp_ms: int, frame: np.ndarray) -> None:
        """Push a new video frame into the circular buffer."""
        self.frame_data.put((timestamp_ms, frame))

    def new_landmarks(self, timestamp_ms: int, landmarks: Dict[str, Any]) -> None:
        """Push new landmarks into the circular buffer."""
        self.landmarks_data.put((timestamp_ms, landmarks))

    # --- Internal Data Processing ---
    def update_frame(self, frame_rgb: np.ndarray) -> None:
        """
        Direct frame submission bypassing the buffer (backward compatibility for VideoDisplay).
        """
        self._process_and_set_frame( frame_rgb)

    def _process_and_set_frame(self, frame_rgb: np.ndarray) -> None:
        """Process a NumPy array into a QImage format ready for rendering."""
        try:
            if frame_rgb is None:
                return

            # Optional frame resolution scaling
            if self.target_height is not None and frame_rgb.shape[0] != self.target_height:
                h, w = frame_rgb.shape[:2]
                aspect_ratio = w / h
                new_w = int(self.target_height * aspect_ratio)
                frame_rgb = cv2.resize(
                    frame_rgb, (new_w, self.target_height), interpolation=cv2.INTER_NEAREST
                )

            height, width, channels = frame_rgb.shape

            # Create QImage directly from memory buffer
            self._qimage = QImage(
                frame_rgb.data,
                width,
                height,
                width * channels,
                QImage.Format_RGB888,
            )
        except Exception as e:
            Logs.print(f"<ERR> VideoDisplay refresh error: {e}")
            Logs.print(traceback.format_exc())

    def update_landmarks(self, landmarks: Dict[str, Any]) -> None:
        """
        Scale normalized landmark coordinates to widget dimensions.
        """
        try:
            sw = self.width()
            sh = self.height()

            for st, lk in landmarks.items():
                if (lk is None) or (lk == Config.NONE_LABEL):
                    self.active_landmarks[st] = []
                else:
                    self.active_landmarks[st] = [
                        ( p.x,p.y ) for p in lk
                    ]
        except Exception as e:
            Logs.print(f"<ERR> VideoDisplay update_landmarks error: {e}, {landmarks}")

    LANDMARKS_RESYNC_THRESHOLD_MS = 200
    FRAME_RESYNC_THRESHOLD_MS = 200

    def refresh(self, time_interval_ms: int) -> None:
        """
            Update time counters and retrieve ready frames and landmarks from buffers for rendering.
        """
        try:
            self.time_next_frame += time_interval_ms
            self.time_next_landmarks += time_interval_ms

            # --- Landmarks: wypuszczaj gotowe, resync gdy zbyt duże opóźnienie ---
            while len(self.landmarks_data) > 0:
                timestamp, _ = self.landmarks_data.last  # najstarszy w buforze
                if self.time_next_landmarks >= timestamp:
                    _, landmarks = self.landmarks_data.throw()
                    self.update_landmarks(landmarks)
                else:
                    break

            if len(self.landmarks_data) > 0:
                newest_ts, _ = self.landmarks_data.first  # najnowszy w buforze
                if newest_ts - self.time_next_landmarks > self.LANDMARKS_RESYNC_THRESHOLD_MS:
                    self.landmarks_data.clear()
                    self.time_next_landmarks = newest_ts

            # --- Frames: analogicznie ---
            while len(self.frame_data) > 0:
                timestamp, _ = self.frame_data.last
                if self.time_next_frame >= timestamp:
                    _, frame = self.frame_data.throw()
                    self.update_frame(frame)
                else:
                    break

            if len(self.frame_data) > 0:
                newest_ts, _ = self.frame_data.first
                if newest_ts - self.time_next_frame > self.FRAME_RESYNC_THRESHOLD_MS:
                    self.frame_data.clear()
                    self.time_next_frame = newest_ts

            self.update()
        except Exception as e:
            Logs.print(f"<ERR> VideoDisplay refresh error: {e}")
            Logs.print(traceback.format_exc())

    # --- Refreshing and Time Loop ---
    # def refresh(self, time_interval_ms: int) -> None:
    #     """
    #         Update time counters and retrieve ready frames and landmarks from buffers for rendering.
    #     """
    #     try:
    #         self.time_next_frame += time_interval_ms
    #         self.time_next_landmarks += time_interval_ms
    #
    #         ts1, frame = self.frame_data.throw()
    #         ts2, landmarks = self.landmarks_data.throw()
    #
    #         print(" <> frames", self.time_next_frame, self.time_next_landmarks, ts1, ts2)
    #
    #         # self.update_landmarks(landmarks)
    #         # self.update_frame( frame )
    #
    #         while len(self.landmarks_data) > 0:
    #             timestamp, _ = self.landmarks_data.last
    #             if self.time_next_landmarks >= timestamp:
    #                 _, landmarks = self.landmarks_data.throw()
    #                 self.update_landmarks(landmarks)
    #             else:
    #                 self.time_next_landmarks += 200
    #                 break
    #
    #         while len(self.frame_data) > 0:
    #             timestamp, _ = self.frame_data.last
    #             if self.time_next_frame >= timestamp:
    #                 _, frame = self.frame_data.throw()
    #                 self.update_frame(frame)
    #             else:
    #                 self.time_next_frame  += 200
    #                 break
    #         self.update()
    #
    #     except Exception as e:
    #         Logs.print(f"<ERR> VideoDisplay refresh error: {e}")
    #         Logs.print(traceback.format_exc())



    # --- Low-level Rendering (paintEvent) ---
    def paintEvent(self, event) -> None:
        """
        Render video frame and overlay hand landmarks in a single QPainter pass.
        """
        if self._qimage is None:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)

        widget_rect = self.rect()
        img_w = self._qimage.width()
        img_h = self._qimage.height()

        if img_w == 0 or img_h == 0:
            return

        scale = min(widget_rect.width() / img_w, widget_rect.height() / img_h) * self.scale_factor

        target_w = int(img_w * scale)
        target_h = int(img_h * scale)

        offset_x = (widget_rect.width() - target_w) // 2
        offset_y = (widget_rect.height() - target_h) // 2

        render_rect = QRect(offset_x, offset_y, target_w, target_h)

        # #  Calculate rendering rect considering scale_factor
        # widget_rect = self.rect()
        # if self.scale_factor < 1.0:
        #     target_w = int(widget_rect.width() * self.scale_factor)
        #     target_h = int(widget_rect.height() * self.scale_factor)
        #
        #     offset_x = (widget_rect.width() - target_w) // 2
        #     offset_y = (widget_rect.height() - target_h) // 2
        #
        #     render_rect = QRect(offset_x, offset_y, target_w, target_h)
        # else:
        #     render_rect = widget_rect

        # Draw image frame
        painter.drawImage(render_rect, self._qimage)

        # Overlay landmarks onto frame (if enabled)
        if self.FLAG_draw_landmarks:
            pen = QPen(QColor("red"))
            pen.setWidth(5)
            painter.setPen(pen)

            for lk in self.active_landmarks.values():
                for norm_x, norm_y in lk:
                    px = offset_x + int(norm_x * target_w)
                    py = offset_y + int(norm_y * target_h)

                    painter.drawPoint(px, py)

        painter.end()