from src.core.camera.BaseCamera import BaseCamera
import cv2
from typing import Tuple, Optional
from numpy.typing import NDArray
# import pyzed.sl as sl

class sl:
    pass
    # download pyzed

class ZED(BaseCamera):
    """
        ZED Camera Instance configured with:
        30 FPS, no depth mode, HD720 resolution
    """

    def __init__(self):
        super().__init__()

        # ZED camera instance
        self.cam = sl.Camera()

        # Initialize camera parameters
        self.init_params = sl.InitParameters()
        self.init_params.camera_resolution = sl.RESOLUTION.HD720
        self.init_params.depth_mode = sl.DEPTH_MODE.NONE
        self.init_params.camera_fps = 30

        # Active reading side / lens
        self.choice_objective = {
            "Right": sl.VIEW.RIGHT,
            "Left": sl.VIEW.LEFT,
        }
        self.active_cam = "Right"

        # Memory buffer for image matrix
        self.image_array = sl.Mat()

        if self.cam.open(self.init_params) != sl.ERROR_CODE.SUCCESS:
            raise Exception("<ERR:ZED> ZED Camera cannot be opened.")

    def get_image(self) -> Tuple[Optional[NDArray], Optional[int]]:
        """
        Retrieves a frame in RGB format along with a timestamp in milliseconds.

        :return frame_rgb: RGB frame
        :return timestamp_ms: Timestamp in milliseconds
        """
        if self.cam.grab() == sl.ERROR_CODE.SUCCESS:
            # Retrieve image from the selected lens
            self.cam.retrieve_image(self.image_array, self.choice_objective[self.active_cam], sl.MEM.CPU)

            timestamp_ns = self.cam.get_timestamp(sl.TIME_REFERENCE.IMAGE).get_nanoseconds()
            timestamp_ms = int(timestamp_ns // 1_000_000)

            # Read buffer data
            frame_bgra: NDArray = self.image_array.get_data()
            frame_rgb = cv2.cvtColor(frame_bgra, cv2.COLOR_BGRA2RGB)

            return frame_rgb, timestamp_ms
        else:
            return None, None

    def swap_objective(self, site: str) -> None:
        """Switches the active ZED lens (Left / Right)."""
        if site in self.choice_objective:
            self.active_cam = site

    def close(self) -> None:
        """Closes the connection to the ZED camera."""
        if hasattr(self, 'cam') and self.cam.is_opened():
            self.cam.close()
