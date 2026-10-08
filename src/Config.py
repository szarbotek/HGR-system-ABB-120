from pathlib import Path
import os
from src.numeric.T_Typing import T_noneLabel

PROJECT_PATH = Path(__file__).resolve().parent.parent
ASSETS_PATH = os.path.join(PROJECT_PATH, "assets")

HAND_LANDMARK_PATH = PROJECT_PATH / "data" / "hand_landmarker.task"

RECOGNITION_ACCELERATION = {True: "GPU", False: "CPU"}
RECOGNITION_MODE = True

REFRESH_TIME_MS = 33
CAMERA_MODE = "simulated"
SIMULATED_CAMERA_VIDEO_PATH = PROJECT_PATH / "assets" / "video" / "videoplayback_003.mp4"

CLASSIFIER_MODEL_PATH = PROJECT_PATH / "data" / "gesture_classifier.keras"
CLASSIFIER_LABEL_CLASSES_ID_PATH = PROJECT_PATH / "data" / "classes.npy"

NONE_LABEL: T_noneLabel = "None"

PROJECT_ACCESSIBLE_CLASSES = [
    "EMPTY-NOT-USE-STATE-ONLY-CALLULALAR-AUTOMATA"
    "grip",
    "one",
    "rock",
    "three3",
    "thumb_index",
    "fist",
    "dislike",
    "stop",
    "peace",
    "three",
    "call",
    "little_finger",
    "like",
    NONE_LABEL,
]


