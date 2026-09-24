import cv2
import numpy as np
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QImage, QPainter
from PyQt5.QtWidgets import QWidget

class VideoDisplay(QWidget):
    """
        PyQt5 class for rendering video frames.
        Accepts an RGB matrix (NumPy) and a timestamp, then refreshes the window.
    """

    # Resolution target heights mapping
    RESOLUTIONS = {
        "720p": 720,
        "480p": 480,
        "360p": 360,
    }

    def set_resolution(self, resolution: str) -> None:
        """
        Sets target resolution preset ("720p", "480p", "360p" or "native").
        """
        self.target_height = self.RESOLUTIONS.get(resolution, None)

    def set_scale_factor(self, scale_factor: float) -> None:
        """
        Sets active drawing scale factor (e.g. 0.5 shrinks target rendered image to 50%).
        """
        self.scale_factor = max(0.1, min(scale_factor, 1.0))
        self.update()

    def __init__(self, parent=None, resolution: str = "720p", scale_factor: float = 1.0):
        super().__init__(parent)
        self._qimage = None
        self.last_timestamp = 0

        # Dynamic resolution and display scaling settings
        self.target_height = self.RESOLUTIONS.get(resolution, None)
        self.scale_factor = max(0.1, min(scale_factor, 1.0))  # Clamped between 0.1 and 1.0

        # Force black background
        self.setStyleSheet("background-color: black;")

    def update_frame(self, timestamp_ms: int, frame_rgb: np.ndarray) -> None:
        """
        Main method that accepts a new frame and triggers a window repaint.
        """
        if frame_rgb is None:
            return

        self.last_timestamp = timestamp_ms

        if self.target_height is not None and frame_rgb.shape[0] != self.target_height:
            h, w = frame_rgb.shape[:2]
            aspect_ratio = w / h
            new_w = int(self.target_height * aspect_ratio)
            frame_rgb = cv2.resize(
                frame_rgb, (new_w, self.target_height), interpolation=cv2.INTER_NEAREST
            )

        height, width, channels = frame_rgb.shape

        # Create QImage directly from NumPy memory buffer (zero-copy)
        self._qimage = QImage(
            frame_rgb.data,
            width,
            height,
            width * channels,
            QImage.Format_RGB888,
        )

        # Trigger system repaint event (fastest trigger in Qt)
        self.update()

    def paintEvent(self, event) -> None:
        """
            Low-level image rendering directly onto the QWidget canvas buffer with scaling factor applied.
        """
        if self._qimage is None:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, False)

        # Calculate target bounding rectangle based on scale_factor
        widget_rect = self.rect()
        if self.scale_factor < 1.0:
            target_w = int(widget_rect.width() * self.scale_factor)
            target_h = int(widget_rect.height() * self.scale_factor)

            # Center scaled image inside widget
            offset_x = (widget_rect.width() - target_w) // 2
            offset_y = (widget_rect.height() - target_h) // 2

            render_rect = QRect(offset_x, offset_y, target_w, target_h)
        else:
            render_rect = widget_rect

        # Draw frame onto calculated canvas area
        painter.drawImage(render_rect, self._qimage)
        painter.end()