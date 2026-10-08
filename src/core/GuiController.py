from typing import TYPE_CHECKING
from src.numeric.T_Typing import T_label, T_timestamp_ms, T_NormalizedLandmark63, T_labelBatch

from PyQt5.QtCore import Qt, QTimer, QMetaObject, Q_ARG, pyqtSlot

from src.core.CameraThread import CameraThread
from src.core.MediaPipeThread import MediaPipeThread
from src.core.CentralUnitThread import CentralUnitThread

import src.Config as Config

if TYPE_CHECKING:
    from src.ui.components.MainWindow import MainWindow


class GuiController:

    def SIGNAL_A000_4CAM(self, *args):
        ts: T_timestamp_ms  = args[0]
        frame = args[1]
        cameraScreen = self.main_window.cameraScreen
        cameraScreen.new_frame(ts, frame)

    def SIGNAL_A002_4MPR(self, *args):

        ts: T_timestamp_ms = args[0]
        landmarks: T_NormalizedLandmark63 = args[1]
        cameraScreen = self.main_window.cameraScreen
        cameraScreen.new_landmarks(ts, landmarks)

    def SIGNAL_A004_4CTU(self, *args):
        hr_stream: T_labelBatch = args[0]
        hl_stream: T_labelBatch = args[1]
        self.main_window.panel_flow_strem_hand_right.add_samples(hr_stream)
        self.main_window.panel_flow_strem_hand_left.add_samples(hl_stream)

    def SIGNAL_A005_4CTU(self, *args):
        queue: list = args[0]
        self.main_window.ask_queue.new_data(queue)

    def __init__(self, main_window: 'MainWindow'):
        super().__init__()
        self.main_window = main_window

        self.camera_thread: CameraThread
        self.mediapipe_thread: MediaPipeThread

        self.refresh_time_ms = Config.REFRESH_TIME_MS

        self.timerRefresh = QTimer()
        self.timerRefresh.timeout.connect( self.refresh )
        self.timerRefresh.start( self.refresh_time_ms )


    def start_thread(self):
        ### ------------------ Init ------------------------------------
        self.camera_thread = CameraThread(Config.CAMERA_MODE, Config.SIMULATED_CAMERA_VIDEO_PATH)
        self.mediapipe_thread = MediaPipeThread()
        self.central_unit_thread = CentralUnitThread()
        ### ------------------ Signals ---------------------------------
        self.camera_thread.SIGNAL_A000_2GUI.connect(self.SIGNAL_A000_4CAM)
        self.camera_thread.SIGNAL_A001_2MPR.connect(self.mediapipe_thread.SIGNAL_A001_4CAM)

        self.mediapipe_thread.SIGNAL_A002_2GUI.connect(self.SIGNAL_A002_4MPR)
        self.mediapipe_thread.SIGNAL_A003_2CTU.connect(self.central_unit_thread.SIGNAL_A003_4MPR)

        self.central_unit_thread.SIGNAL_A004_2GUI.connect(self.SIGNAL_A004_4CTU)
        self.central_unit_thread.SIGNAL_A005_2GUI.connect(self.SIGNAL_A005_4CTU)

        ### ------------------ Start -----------------------------------
        self.camera_thread.start()
        self.mediapipe_thread.start()
        self.central_unit_thread.start()

    def refresh(self):
        self.main_window.cameraScreen.refresh( self.refresh_time_ms )
        self.main_window.panel_flow_strem_hand_right.refresh(self.refresh_time_ms)
        self.main_window.panel_flow_strem_hand_left.refresh(self.refresh_time_ms)
        self.main_window.logsBox.refresh( self.refresh_time_ms )
        ## self.main_window.ask_queue.refresh( self.refresh_time_ms ) // undefined

