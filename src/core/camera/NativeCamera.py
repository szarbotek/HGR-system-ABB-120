from src.core.camera.BaseCamera import BaseCamera
import cv2
from typing import Tuple, Optional
from numpy.typing import NDArray
import time

class NativeCamera(BaseCamera):
    """
        Instance of a native device camera using OpenCV (cv2.VideoCapture).
        By default captures images at HD720 resolution (1280x720) at 30 FPS.
    """

    def __init__(self, camera_index: int = 0):
        super().__init__()
        self.camera_index = camera_index
        self.cap = cv2.VideoCapture(self.camera_index)

        # Set HD720 resolution and 30 FPS framerate
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        self.cap.set(cv2.CAP_PROP_FPS, 30)

        if not self.cap.isOpened():
            raise Exception(f"<ERR:NATIVE_CAM> Native camera (index {self.camera_index}) cannot be opened.")

    def get_image(self) -> Tuple[Optional[NDArray], Optional[int]]:
        """
        Retrieves a frame from the native camera and converts it to RGB format.

        :return frame_rgb: RGB format frame
        :return timestamp_ms: Frame capture timestamp in milliseconds
        """
        ret, frame_bgr = self.cap.read()
        if not ret or frame_bgr is None:
            return None, None

        timestamp_ms = int(time.time() * 1000)
        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        return frame_rgb, timestamp_ms

    def swap_objective(self, site: str) -> None:
        """Native camera has only a single lens - dummy method for interface consistency."""
        pass

    def close(self) -> None:
        """Releases native camera resources."""
        if self.cap and self.cap.isOpened():
            self.cap.release()

