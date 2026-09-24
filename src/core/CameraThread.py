"""
    The camera thread is responsible for capturing images from the camera
    and streaming them to the GUI and MPR modules.
    This module supports both native device cameras (OpenCV) and the ZED camera (pyzed.sl).
"""

import time

from PyQt5.QtCore import QThread, pyqtSignal
from src.utils.Logs import Logs

from src.core.camera import *

class CameraThread(QThread):
    """
        CameraThread(QThread) class:
        Responsible for broadcasting frames to the GUI and MPR modules.
    """
    SIGNAL_A000_2GUI: pyqtSignal = pyqtSignal(int, object)  # Frame signal to GUI
    SIGNAL_A001_2MPR: pyqtSignal = pyqtSignal(int, object)  # Frame signal to MPR

    def __Unconnected_SIGNAL_Axxx_4GUI(self, *args):
        """Receive camera lens change flag."""
        if self.mode == "zed":
            self.swap_zed_camera(*args)

    def swap_zed_camera(self, site: str):
        """Forwards the lens switch request to the camera object."""
        self.camera_object.swap_objective(site)

    def __init__(self, mode: str = "native", video_path: str = "sample_video.mp4"):
        """
        :param mode:"native", "simulated", "zed"
        :param video_path: Path to source video file for simulate camera
        """

        super().__init__()
        Logs.print(f"CAM: [INIT] Initializing thread")

        self.mode = mode

        # Wybór odpowiedniej kamery
        if mode == "native":
            self.camera_object: BaseCamera = NativeCamera()
            Logs.print(f"CAM: [INFO] Created NativeCamera instance")
        elif mode == "zed":
            self.camera_object: BaseCamera = ZED()
            Logs.print(f"CAM: [INFO] Created ZED instance")
        elif mode == "simulated":
            self.camera_object: BaseCamera = SimulatedCamera(video_path=video_path)
            Logs.print(f"CAM: [INFO] Created SimulatedCamera instance ({video_path})")
        else:
            raise TypeError("Invalid mode")

    def run(self):
        Logs.print(f"CAM: [PROC] Activating image frame grabbing process")

        try:
            while not self.isInterruptionRequested():
                start_time = time.time()

                frame_rgb, img_timestamp = self.camera_object.get_image()

                # Skip iteration if no frame is available
                if frame_rgb is None:
                    time.sleep(0.005)
                    continue

                # Calculate frame processing time
                timestamp_ms = int(abs((start_time - time.time()) * 1000))

                # Emit frames via signals
                self.SIGNAL_A000_2GUI.emit(
                    timestamp_ms, frame_rgb.copy()
                )
                self.SIGNAL_A001_2MPR.emit(
                    timestamp_ms, frame_rgb.copy()
                )

        except Exception as e:
            Logs.print(f"<ERR> Thread execution failed: {e}")
            self.quit()

        Logs.print(f"\n[ENDPROC] Deactivating image grabbing process")
        self.camera_object.close()