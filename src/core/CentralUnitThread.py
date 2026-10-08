"""
    User Interface Controller.

    Thread responsible for control and decision-making logic.
    Based on hand_landmarks, it classifies gestures (after normalization)
    using a trained ML gesture. Gestures are collected in task buffers (Task)
    separately for the right and left hands. When a command sequence is recognized,
    the corresponding control signals are emitted.
"""

import time
import traceback
from typing import List, Tuple, Dict, Any, Optional, Union, cast

from control import Compiler
from src.numeric.T_Typing import (
    T_LandmarkRightLeft, T_timestamp_ms, T_sample, T_landmarkBatch63, T_label, T_NormalizedLandmark63, T_noneLabel
)
from src.numeric.T_numeric import _T_landmark63

import numpy as np
from PyQt5.QtCore import QThread, pyqtSignal, QTimer, pyqtSlot

from src.core.gesture.ClassifierModel import ClassifierModel
from src.core.gesture.GestureLabelEncoder import GestureLabelEncoder

from src.utils.Logs import Logs
import src.Config as Config

from src.numeric.CircularBuffer import CircularBuffer
from src.numeric.TaskBuffer import TaskBuffer

from src.core.control.WordCoder import WordCoder
from src.core.control.SignalUnit import SignalUnit

import src.numeric.Normalization as Normalization


from src.core.gesture.CellularAutomata import CellularAutomata

# from src.application.utils.HandGastureControlSystem import Task, WordCoder
# from src.application.utils.ComunicationProtocol import T_TagCommand, T_DictionaryMessage, CommunicationTags


class CentralUnitThread(QThread):
    # --- Outgoing signals to GUI and communication modules ---
    SIGNAL_A004_2GUI = pyqtSignal(list, list)    # Detected samples (right, left)
    SIGNAL_A005_2GUI = pyqtSignal(list)                 # WordCoder queue state

    # SIGNAL_A005_2GUI = pyqtSignal(list, list)         # Labels from Task buffer
    # SIGNAL_A006_2GUI = pyqtSignal(list, list)         # Label duration times from Task buffer
    # SIGNAL_A007_2GUI = pyqtSignal(list)                 # WordCoder queue state
    # SIGNAL_A008_2GUI = pyqtSignal(object)               # MOV movement query
    # SIGNAL_A009_2CMT = pyqtSignal(bool)                 # Connection activation/deactivation
    # SIGNAL_A011_2CMT = pyqtSignal(str)                  # Control messages
    # SIGNAL_A012_2GUI = pyqtSignal(object)               # Communication responses

    @pyqtSlot(int, object)
    def SIGNAL_A003_4MPR(self, timestamp_ms: T_timestamp_ms, landmark: T_LandmarkRightLeft):

        hr: Optional[T_landmarkBatch63] = landmark.get("Right", None)
        hl: Optional[T_landmarkBatch63] = landmark.get("Left", None)

        self.raw_samples_stream_hand_right.put( (timestamp_ms, hr) )
        self.raw_samples_stream_hand_left.put(  (timestamp_ms, hl) )

    # @pyqtSlot(tuple)
    # def SIGNAL_A010_4CMT(self, info):
    #     """ Slot receiving statuses from the communication module. """
        # try:
        #     tag, msg = info
        #     self.SIGNAL_A012_2GUI.emit((tag, msg))
        #
        #     if tag == CommunicationTags.TAG.MESSAGE:
        #         self.data_unit = msg.get(CommunicationTags.MessageDictKeys.dataUnit)
        #
        #     elif tag == CommunicationTags.TAG.CONTROL:
        #         self.control = msg
        #         programs: Dict[str, str] = msg.get(CommunicationTags.MessageDictKeys.programs, {})
        #         self.word_coder.literal_programs.setup(0, list(programs.keys()))
        #
        #     elif tag == CommunicationTags.TAG.CONFIGURATE:
        #         self.configurate = msg
        #         controllers: Dict[str, Any] = msg.get(CommunicationTags.MessageDictKeys.controllers, {})
        #         self.word_coder.numerator_connect.setup(0, len(controllers))
        #
        # except Exception as e:
        #     LOG.print(f"<ERR> UIC SIGNAL_A010_4CMT: {e}")
        #     LOG.print(traceback.format_exc())

    # --- Detection parameters ---

    gesture_per_second: int = 10
    min_sample_time_ms: int = int(1.0 / gesture_per_second * 1000)  # 100 ms

    max_sample_analyze_time_s: int = 5
    max_sample_analyze_time_ms: int = 1000 * max_sample_analyze_time_s
    max_sample_amount: int = max_sample_analyze_time_s * gesture_per_second # 60 samples

    def __init__(self):
        super().__init__()
        Logs.print("CTU: [INIT] Initializing CentralUnitThread")

        # Flags and timers
        self.timer_detect: Optional[QTimer] = None

        # Load gesture detection gesture
        self.model = ClassifierModel( Config.CLASSIFIER_MODEL_PATH )
        self.encoder = GestureLabelEncoder( Config.CLASSIFIER_LABEL_CLASSES_ID_PATH )

        self.raw_samples_stream_hand_right: CircularBuffer[T_sample] = CircularBuffer( self.max_sample_amount )
        self.raw_samples_stream_hand_left:  CircularBuffer[T_sample] = CircularBuffer( self.max_sample_amount )

        self.predict_samples_stream_hand_right: CircularBuffer[str] = CircularBuffer(self.max_sample_amount)
        self.predict_samples_stream_hand_left:  CircularBuffer[str] = CircularBuffer(self.max_sample_amount)

        self.stable_samples_stream_hand_right: CircularBuffer[str] = CircularBuffer(self.max_sample_amount)
        self.stable_samples_stream_hand_left:  CircularBuffer[str] = CircularBuffer(self.max_sample_amount)

        self.word_coder = WordCoder(
            min_sample_time_ms=self.min_sample_time_ms,
            max_sample_amount=self.max_sample_amount
        )

        # # Configuration info and controller states
        # self.configurate: Optional[Dict] = None
        # self.control: Optional[Dict] = None
        # self.data_unit: Optional[Any] = None

    def label_predict(self):
        """ Fetches latest landmark data, performs normalization, and runs classifier inference. """
        try:
            # Default to fallback label for both hands
            label_right: T_label = Config.NONE_LABEL
            label_left: T_label = Config.NONE_LABEL

            landmark_hr: Union[T_NormalizedLandmark63, T_noneLabel]
            landmark_hl: Union[T_NormalizedLandmark63, T_noneLabel]

            if len(self.raw_samples_stream_hand_right) == 0 or (len(self.raw_samples_stream_hand_left) == 0):
                self.predict_samples_stream_hand_right.put(str(label_right))
                self.predict_samples_stream_hand_left.put(str(label_left))
                return

            # Pop the oldest sample from circular buffers
            tsr0, landmark_hr = self.raw_samples_stream_hand_right.throw()
            tsl0, landmark_hl = self.raw_samples_stream_hand_left.throw()

            tr_sum = 0
            tl_sum = 0

            # eliminate overflow buffor in sample time block
            while len(self.raw_samples_stream_hand_right):
                tsr, landmark_hr = self.raw_samples_stream_hand_right.throw()
                tr_sum += tsr - tsr0
                if tr_sum > self.min_sample_time_ms-16:
                    break
            while len(self.raw_samples_stream_hand_left):
                tsl, landmark_hl = self.raw_samples_stream_hand_left.throw()
                tl_sum += tsl - tsl0
                if tl_sum > self.min_sample_time_ms-16:
                    break
            # self.raw_samples_stream_hand_right.clear()
            # self.raw_samples_stream_hand_left.clear()

            if (
                    landmark_hr is None              or landmark_hl is None               ) or (
                    landmark_hr == Config.NONE_LABEL or landmark_hl == Config.NONE_LABEL
            ):
                # Skip inference if either hand is missing or unclassified
                pass
            else:
                landmark_hr_valid = cast(T_NormalizedLandmark63, landmark_hr)
                landmark_hl_valid = cast(T_NormalizedLandmark63, landmark_hl)

                # Both hands detected; proceed with batch processing
                conv_landmark_hr: _T_landmark63 = Normalization.convert_NormalizedLandmark_2_array(landmark_hr_valid)
                conv_landmark_hl: _T_landmark63 = Normalization.convert_NormalizedLandmark_2_array(landmark_hl_valid)

                # Normalize 3D landmark coordinates
                norm_landmark_hr = Normalization.normalization_landmark63( conv_landmark_hr, True,True,True,True,)
                norm_landmark_hl = Normalization.normalization_landmark63( conv_landmark_hl, True, True, True, True, )

                # Combine normalized arrays into a single batch for inference
                landmark_batch: list[np.ndarray] = [
                    norm_landmark_hr,
                    norm_landmark_hl,
                ]

                # Run model inference and decode class IDs into labels
                id_batch = self.model.predict_batch_class_ids(landmark_batch)
                label_batch: list[str] = self.encoder.decode(id_batch)

                label_right, label_left = label_batch[0], label_batch[1]

            # Push predicted gesture labels to output streams
            self.predict_samples_stream_hand_right.put( str(label_right) )
            self.predict_samples_stream_hand_left.put( str(label_left) )

        except Exception as e:
            Logs.print(f"<ERR:CTU> Problem in CentralUnitThread.label_predict: {e}")
            Logs.print(traceback.format_exc())

    def stabilization(self):
        """
            Filters out gesture recognition noise using a cellular automaton.
        :return:
        """
        try:
            def repet_to_stable(data_stream):

                _conv_ID_2_LABEL: dict[int,str] = { index:label for index,label  in enumerate( Config.PROJECT_ACCESSIBLE_CLASSES ) }
                _conv_LABEl_2_ID: dict[str,int]  = { label:index for index,label  in enumerate( Config.PROJECT_ACCESSIBLE_CLASSES ) }

                generation = [ _conv_LABEl_2_ID.get(d, 0) for d in data_stream]

                # 20 steps maximum
                for i in range(10):
                    last_generation = generation.copy()
                    generation = CellularAutomata.next_generation( generation.copy() )
                    # print( "%%%", last_generation, '\n', generation)
                    if last_generation == generation:
                        # print("STABILIZING")
                        break

                stable_data_stream = [_conv_ID_2_LABEL.get(g, Config.NONE_LABEL) for g in generation]

                return stable_data_stream

            if (len(self.predict_samples_stream_hand_right) <= 3) or (
                    len(self.predict_samples_stream_hand_left) <= 3 ): return

            window7cells_r = self.predict_samples_stream_hand_right[:7]
            window7cells_l = self.predict_samples_stream_hand_left[:7]

            # rest_r = self.predict_samples_stream_hand_right[7:]
            # rest_l = self.predict_samples_stream_hand_left[7:]

            stab7cells_r = repet_to_stable( window7cells_r )
            stab7cells_l = repet_to_stable( window7cells_l )

            self.stable_samples_stream_hand_right.put( stab7cells_r[3] )
            self.stable_samples_stream_hand_left.put(  stab7cells_l[3] )
            ## update gesture in time status
            self.word_coder.put_task_main_command( stab7cells_l[3], stab7cells_r[3] )

        except Exception as e:
            Logs.print(f"<ERR:CTU> Stabilization error: {e}")
            Logs.print(traceback.format_exc())

    def _processing_cycle(self):
        """ Processing cycle invoked periodically by QTimer within the execution thread. """
        try:
            ## 1. Gesture classification
            self.label_predict()

            ## 2. Filtering and result stabilization
            self.stabilization()

            self.SIGNAL_A004_2GUI.emit(
                self.stable_samples_stream_hand_left.get_list(),
                self.stable_samples_stream_hand_right.get_list(),
            )

            ## 3.  Update command logic
            self.word_coder.update_status()

            ## 4. Emit results to Graphic User Interface (GUI)
            self.SIGNAL_A005_2GUI.emit( self.word_coder.queue )#self.word_coder.get())
            # self.SIGNAL_A006_2GUI.emit()

            ## 5. Emit results to Communication Thread (CMT)
            # self.SIGNAL_A007_2CMT.emit()
            # self.SIGNAL_A008_2CMT.emit()
            # self.SIGNAL_A009_2CMT.emit()

            ## 6. Signal Resets
            SignalUnit.refresh_signal()

            # buf_data = self.gestures.get_buffer()
            # self.SIGNAL_A004_2GUI.emit([t[1] for t in buf_data], [t[2] for t in buf_data])
            #
            # self.SIGNAL_A005_2GUI.emit(self.task_right.get_label(), self.task_left.get_label())
            # self.SIGNAL_A006_2GUI.emit(self.task_right.get_value(), self.task_left.get_value())
            # self.SIGNAL_A007_2GUI.emit(self.word_coder.get())
            #
            # # 5. Emit network and control events
            # if self.word_coder.FLAG_emit_SIGNAL_A008:
            #     self.SIGNAL_A008_2GUI.emit(self.word_coder.DATA_emit_SIGNAL_A008)
            #
            # if self.word_coder.FLAG_emit_SIGNAL_A009:
            #     self.SIGNAL_A009_2CMT.emit(self.word_coder.DATA_emit_SIGNAL_A009)
            #
            # if self.word_coder.FLAG_emit_SIGNAL_A011:
            #     self.SIGNAL_A011_2CMT.emit(self.word_coder.DATA_emit_SIGNAL_A011)


        except Exception as e:
            Logs.print(f"<ERR:CTU> CentralUnitThread cycle error: {e}")
            Logs.print(traceback.format_exc())

    def run(self):
        """ Main thread method. Initializes the QTimer inside this thread's scope. """
        Logs.print("CTU: [PROC] Activating CentralUnitThread run loop")

        # Create QTimer INSIDE the execution thread
        self.timer_detect = QTimer()
        self.timer_detect.setInterval(self.min_sample_time_ms)
        self.timer_detect.timeout.connect(self._processing_cycle)
        self.timer_detect.start()

        # Run Qt event loop
        self.exec_()

        # Cleanup after event loop exits
        self.timer_detect.stop()