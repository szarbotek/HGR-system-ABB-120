from src.core.camera.BaseCamera import BaseCamera
import cv2
from typing import Tuple, Optional
from numpy.typing import NDArray
import time

class SimulatedCamera(BaseCamera):
    """
    Symulowana kamera (FakeCamera/VideoStream), która wczytuje plik wideo
    i odtwarza go w pętli, symulując strumień na żywo z fizycznej kamery.
    """

    def __init__(self, video_path: str = "sample_video.mp4"):
        super().__init__()
        self.video_path = video_path
        self.cap = cv2.VideoCapture(self.video_path)

        if not self.cap.isOpened():
            raise Exception(f"<ERR:SIMULATED_CAM> Cannot open video file: {self.video_path}")

        # Odczytanie natywnej liczby klatek na sekundę z pliku wideo
        fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.frame_delay = 1.0 / fps if fps > 0 else 1.0 / 30.0
        self.last_frame_time = time.time()

    def get_image(self) -> Tuple[Optional[NDArray], Optional[int]]:
        """
        Zwraca klatkę z pliku wideo w formacie RGB.
        Automatycznie zapętla wideo po osiągnięciu końca pliku.
        """
        # Kontrola tempa odtwarzania wideo (zachowanie natywnego FPS filmu)
        elapsed = time.time() - self.last_frame_time
        if elapsed < self.frame_delay:
            time.sleep(self.frame_delay - elapsed)
        self.last_frame_time = time.time()

        ret, frame_bgr = self.cap.read()

        # Jeśli osiągnięto koniec filmu (lub błąd odczytu) -> zapętlenie
        if not ret or frame_bgr is None:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame_bgr = self.cap.read()
            if not ret or frame_bgr is None:
                return None, None

        timestamp_ms = int(time.time() * 1000)
        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        return frame_rgb, timestamp_ms

    def swap_objective(self, site: str) -> None:
        pass

    def close(self) -> None:
        if self.cap and self.cap.isOpened():
            self.cap.release()