"""
    MediapipeRecognizer thread module.
    Responsible for hand landmark detection on incoming video frames
    and emitting the keypoints to the GUI and UIC modules.
"""

import time
import traceback
from typing import Any, Dict, Tuple, Optional
import numpy as np
from numpy.typing import NDArray

import mediapipe as mp
from mediapipe.tasks import python as mp_python

from PyQt5.QtCore import QThread, pyqtSignal

from src.application.utils.structure import CircularBuffer
from src.utils.Logs import Logs

from src.Config import HAND_LANDMARK_PATH

class MediapipeRecognizer(QThread):
    """
    MediapipeRecognizer(QThread) class:
    Detects hand landmarks from video frame stream using MediaPipe HandLandmarker.
    """

    SIGNAL_A002_2GUI = pyqtSignal(int, object)  # Landmark signal to GUI
    SIGNAL_A003_2UIC = pyqtSignal(int, object)  # Landmark signal to UIC

    def SIGNAL_A001_4CAM(self, timestamp_ms: int, frame_rgb: np.ndarray) -> None:
        """
            Slot receiving frame data from the camera thread and placing it into the circular buffer.
        """
        try:
            if frame_rgb is not None:
                self.data_frame_2_recognition.put((timestamp_ms, frame_rgb))
        except Exception as e:
            Logs.print(f"<ERR> SIGNAL_A001_4CAM failed: {e}")

    def __init__(self) -> None:
        super().__init__()
        Logs.print("MPR: [INIT] Initializing thread")

        # Define MediaPipe HandLandmarker options
        self.options = mp_python.vision.HandLandmarkerOptions(
            base_options=mp_python.BaseOptions(
                model_asset_path=HAND_LANDMARK_PATH,
                delegate=mp_python.BaseOptions.Delegate.GPU,
            ),
            num_hands=2,
            running_mode=mp.tasks.vision.RunningMode.VIDEO,
            min_hand_presence_confidence=0.5,
            min_hand_detection_confidence=0.5,
            min_tracking_confidence=0.7,
        )

        self.data_frame_2_recognition: CircularBuffer = CircularBuffer(60)

    def run(self) -> None:
        Logs.print("MPR: [PROC] Activating MediapipeRecognizer process")

        try:
            with mp_python.vision.HandLandmarker.create_from_options(self.options) as recognizer:
                Logs.print("MPR: [INFO] Model hand_landmarker.task opened successfully!")

                last_video_timestamp_ms: int = -1

                while not self.isInterruptionRequested():
                    if len(self.data_frame_2_recognition) == 0:
                        time.sleep(0.005)
                        continue

                    start_time = time.time()
                    ts, frame_rgb = self.data_frame_2_recognition.throw()

                    # Convert NumPy array frame to MediaPipe Image format
                    mp_image = mp.Image(
                        image_format=mp.ImageFormat.SRGB, data=frame_rgb
                    )

                    # Ensure strictly monotonically increasing timestamp for MediaPipe Video Mode
                    current_timestamp_ms = int(time.time() * 1000)
                    if current_timestamp_ms <= last_video_timestamp_ms:
                        current_timestamp_ms = last_video_timestamp_ms + 1
                    last_video_timestamp_ms = current_timestamp_ms

                    # Perform hand landmark detection
                    result = recognizer.detect_for_video(mp_image, current_timestamp_ms)

                    # Map landmarks to specific hand sides ("Right" / "Left")
                    data_landmarks: Dict[str, Any] = {
                        "Right": None,
                        "Left": None,
                    }

                    if result.hand_landmarks and result.handedness:
                        for lk, hd in zip(result.hand_landmarks, result.handedness):
                            side = hd[0].category_name
                            data_landmarks[side] = lk
                            <>brak rozruzniania strony

                    proc_time_ms = int(abs(time.time() - start_time) * 1000)
                    output_timestamp = max(0, ts - proc_time_ms)

                    # Emit detected landmarks
                    self.SIGNAL_A002_2GUI.emit(output_timestamp, data_landmarks.copy())
                    self.SIGNAL_A003_2UIC.emit(output_timestamp, data_landmarks.copy())

                    # Frame dropping logic: keep processing latency low when buffer backs up
                    if len(self.data_frame_2_recognition) >= 3:
                        self.data_frame_2_recognition.throw()
                        self.data_frame_2_recognition.throw()

        except Exception as e:
            Logs.print(f"<ERR> MediapipeRecognizer thread failed: {e}")
            Logs.print(traceback.format_exc())

        Logs.print("\n[THREAD] Deactivating MediapipeRecognizer")
        self.quit()