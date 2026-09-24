from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import QMainWindow, QGridLayout

from src.utils.Logs import Logs

from src.ui.Styles import Styles

from src.ui.active.NCwidget import NCwidget
from src.ui.active.NavigationCursor import NavigationCursor
from src.ui.active.NCicons import NCstaticIconImage

from src.ui.components.VideoDisplay import VideoDisplay


from src.core.GuiController import GuiController
from src.core.CameraThread import CameraThread

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        Logs.print("GUI: [__init__] Initializing MainWindow thread context")

        self.setFixedSize(1500, 800)
        self.setStyleSheet("background-color: #0d1117;")

        self.config_NC_keys()
        self.build_ui()
        self.start_thread()

    def config_NC_keys(self):
        """
        base mapping:
            W: W,
            S: S,
            A: A,
            D: D,
            E: IN,
            Q: OUT,
        :return:
        """
        source_mapping = NavigationCursor.CONNECTION_PATTER.copy()
        keyboard_mapping = {
            1: "W",
            2: "S",
            3: "A",
            4: "D",
            5: "E",
            6: "Q",
        }
        self.NC_keys_mapping: dict[str, str] = {}

        #
        for (sb_key, sb_val), (sr_key, sr_val) in zip(  keyboard_mapping.items(), source_mapping.items() ):
            if sb_key == sr_key:
                self.NC_keys_mapping[sb_val] = sr_val

    def build_ui(self):
        Logs.print("GUI: [BUILD] Building UI layout components")

        # ------------------ Main widget --------------------
        #  Main window base panel
        # ---------------------------------------------------
        win = NCwidget(self)
        win.setFixedSize(self.width(), self.height())
        win.backgroundColor = Styles.colorPallet.BgMain

        grid_main = QGridLayout(win)
        grid_main.setContentsMargins(2, 2, 2, 2)
        grid_main.setSpacing(4)

        self.cameraScreen: VideoDisplay
        # ------------------ Section: Camera -----------------------
        def build_section_camera():
            section = NCwidget(win)
            grid_layout = QGridLayout( section )

            grid_layout.setContentsMargins(2,2,2,2)
            grid_layout.setSpacing(4)

            self.cameraScreen = VideoDisplay(self, scale_factor=1.0)
            grid_layout.addWidget(self.cameraScreen, 0, 0)

            return section

        # ------------------ Section: Help Box ---------------------
        def build_section_help_box():
            section = NCwidget(win)

            grid_layout = QGridLayout(section)
            grid_layout.setContentsMargins(2,2,2,2)
            grid_layout.setSpacing(4)

            self.helpBoxScreen = NCstaticIconImage(section, path=Styles.assets.helpBox_base, size=(300, 300))

            grid_layout.addWidget(self.helpBoxScreen, 0, 0)

            return section

        # ------------------ Section: Samples ---------------------
        def build_section_samples():
            section = NCwidget(win)

            grid_layout = QGridLayout(section)
            grid_layout.setContentsMargins(2,2,2,2)
            grid_layout.setSpacing(4)

            return section

        # ------------------ Section: Samples ---------------------
        def build_section_logs():
            section = NCwidget(win)

            grid_layout = QGridLayout(section)
            grid_layout.setContentsMargins(2,2,2,2)
            grid_layout.setSpacing(4)

            return section

        # ------------------ Section: Samples ---------------------
        def build_section_queue_ask():
            section = NCwidget(win)

            grid_layout = QGridLayout(section)
            grid_layout.setContentsMargins(2,2,2,2)
            grid_layout.setSpacing(4)

            return section

        # ------------------ Section: Robot Panel ---------------------
        def build_section_robot_panel():
            section = NCwidget(win)

            grid_layout = QGridLayout(section)
            grid_layout.setContentsMargins(2,2,2,2)
            grid_layout.setSpacing(4)

            return section

        # ------------------ End section layout --------------------
        sectionCamera = build_section_camera()
        sectionHelpBox = build_section_help_box()
        sectionSamples = build_section_samples()
        sectionLogs = build_section_logs()
        sectionQueueAsk = build_section_queue_ask()
        sectionRobotPanel = build_section_robot_panel()

        Logs.print("GUI: [BUILD] Generate grid layout")

        grid_main.addWidget( sectionCamera,     0, 0)
        grid_main.addWidget( sectionHelpBox,    0, 1, 1, 2)
        grid_main.addWidget( sectionSamples,    1, 0, 1, 2)
        grid_main.addWidget( sectionLogs,       2, 0, 1, 2)
        grid_main.addWidget( sectionQueueAsk,   1, 2, 2, 1)
        grid_main.addWidget( sectionRobotPanel, 0, 3, 3, 1)

        self.show()
        NavigationCursor.generate_connection()
        NavigationCursor.set_cursor(win)

        Logs.print("GUI: [BUILD] End building UI components ")

    def start_thread(self):
        self.GuiController = GuiController(self)
        self.CameraThread = CameraThread("simulated", "assets/video/videoplayback.mp4")

        # ------------------ Signals ---------------------------------
        self.CameraThread.SIGNAL_A000_2GUI.connect( self.GuiController.SIGNAL_A000_4CAM )
        # self.CAM.SIGNAL_A001_2MPR.connect(self.MPR.SIGNAL_A001_4CAM)

        # ------------------ Start -----------------------------------
        self.CameraThread.start()


    # ------------------ Section: Help Box ---------------------
    #  keyPressEvent
    # ----------------------------------------------------------
    def keyPressEvent(self, event) -> None:

        keys = {
            Qt.Key_Q: "Q",
            Qt.Key_W: "W",
            Qt.Key_E: "E",
            Qt.Key_A: "A",
            Qt.Key_S: "S",
            Qt.Key_D: "D",
        }
        key = keys.get(event.key())

        if key:
            Logs.print(f"Key pressed: {key}, {self.NC_keys_mapping.get(key, None)}")
            NavigationCursor.movement_cursor.move_cursor_to_next_positon( self.NC_keys_mapping.get(key, None) )
            return

        super().keyPressEvent(event)

        try:
            pass
        except Exception as e:
            print(e)

