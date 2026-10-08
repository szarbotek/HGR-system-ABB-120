from typing import TypedDict, Union, Optional, NewType,  NamedTuple
from mediapipe.tasks.python.components.containers import NormalizedLandmark
import numpy as np

T_NormalizedLandmark63 = list[NormalizedLandmark]
T_landmarkBatch63 = NewType("T_landmarkBatch63", np.ndarray)
T_noneLabel = NewType("T_noneLabel", str)
T_label = str | T_noneLabel
T_labelBatch = list[str]

class T_LandmarkRightLeft(TypedDict):
    """
    Type definition for Left/Right hand landmarks data.
    """
    Right:  Union[NormalizedLandmark, T_noneLabel]
    Left:   Union[NormalizedLandmark, T_noneLabel]

T_timestamp_ms = NewType("T_timestamp_ms", int)

class T_sample(NamedTuple):
    timestamp_ms: Optional[T_timestamp_ms]
    landmarks:    Optional[T_LandmarkRightLeft]