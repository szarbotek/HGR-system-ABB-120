"""
    MediapipeRecognizer thread module.
    Responsible for hand landmark detection on incoming video frames
    and emitting the keypoints to the GUI and UIC modules.
"""

import time
import traceback

from typing import Any, Dict, Tuple, Optional
from src.numeric.T_Typing import T_LandmarkRightLeft, T_timestamp_ms

import numpy as np
from numpy.typing import NDArray

import mediapipe as mp
from mediapipe.tasks import python as mp_python

from PyQt5.QtCore import QThread, pyqtSignal

from src.numeric.CircularBuffer import CircularBuffer

from src.utils.Logs import Logs
import src.Config as Config



class MediaPipeThread(QThread):
    """
        MediapipeRecognizer(QThread) class:
        Detects hand landmarks from frame stream using MediaPipe HandLandmarker.
    """

    SIGNAL_A002_2GUI = pyqtSignal(int, object)  # Landmark signal to GUI
    SIGNAL_A003_2CTU = pyqtSignal(int, object)  # Landmark signal to CMT

    def SIGNAL_A001_4CAM(self, timestamp_ms: T_timestamp_ms, frame_rgb: np.ndarray) -> None:
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

        delegate_option = {
            "GPU": mp_python.BaseOptions.Delegate.GPU,
            "CPU": mp_python.BaseOptions.Delegate.CPU,
        }.get(  # selector
            Config.RECOGNITION_ACCELERATION.get(
                Config.RECOGNITION_MODE, "CPU"
            )
        )

        # Define MediaPipe HandLandmarker options
        self.options = mp_python.vision.HandLandmarkerOptions(
            base_options=mp_python.BaseOptions(
                model_asset_path=str(Config.HAND_LANDMARK_PATH),
                delegate= delegate_option,
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
                    data_landmarks: T_LandmarkRightLeft = {
                        "Right": Config.NONE_LABEL,
                        "Left":  Config.NONE_LABEL,
                    }

                    if result.hand_landmarks and result.handedness:
                        for lk, hd in zip(result.hand_landmarks, result.handedness):
                            # read hand side
                            side = hd[0].category_name
                            # save data
                            data_landmarks[side] = lk


                    # proc_time_ms = int(abs(time.time() - start_time) * 1000)
                    output_timestamp = max(0, ts) #- proc_time_ms)

                    ## Logs.print(f"MPR: [INFO] Detecting hand landmarks {output_timestamp}")

                    # Emit detected landmarks
                    self.SIGNAL_A002_2GUI.emit(output_timestamp, data_landmarks.copy())
                    self.SIGNAL_A003_2CTU.emit(output_timestamp, data_landmarks.copy())

                    # Frame dropping logic: keep processing latency low when buffer backs up
                    if len(self.data_frame_2_recognition) >= 3:
                        self.data_frame_2_recognition.throw()
                        self.data_frame_2_recognition.throw()

        except Exception as e:
            Logs.print(f"<ERR> MediapipeRecognizer thread failed: {e}")
            Logs.print(traceback.format_exc())

        Logs.print("\n[THREAD] Deactivating MediapipeRecognizer")
        self.quit()