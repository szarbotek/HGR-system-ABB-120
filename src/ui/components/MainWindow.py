from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import QMainWindow, QGridLayout, QVBoxLayout, QWidget

from src.utils.Logs import Logs

from src.ui.Styles import Styles

from src.ui.active.NCwidget import NCwidget
from src.ui.active.NavigationCursor import NavigationCursor
from src.ui.active.NCicons import NCstaticIconImage
from src.ui.active.NCvideoDisplay import NCvideoDisplay

from src.ui.components.VideoDisplay import VideoDisplay
from src.ui.components.TextLabel import TextLabel

from src.ui.dynamic.LogsBox import LogsBox
from src.ui.dynamic.WordQueue import WordQueue
from src.ui.dynamic.RobotListWidget import RobotListWidget
from src.ui.dynamic.PanelFlowStream import PanelFlowStream
from src.ui.dynamic.TextEntry import TextEntry

from src.core.GuiController import GuiController


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        Logs.print("GUI: [__init__] Initializing MainWindow thread context")

        self.setFixedSize(1200, 700)
        self.setStyleSheet("background-color: #0d1117;")

        self.config_NC_keys()

        self.cameraScreen: NCvideoDisplay
        self.build_ui()

        self.gui_controller = GuiController(self)
        self.gui_controller.start_thread()

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
        grid_main.setContentsMargins(8, 8, 8, 8)
        grid_main.setSpacing(4)

        self.cameraScreen: VideoDisplay
        # ------------------ Section: Camera -----------------------
        def build_section_camera():
            section = NCwidget(win)
            grid_layout = QGridLayout( section )

            grid_layout.setContentsMargins(8,20,8,20)
            grid_layout.setSpacing(2)

            panel = NCwidget( section )
            panel.setFixedSize(324, 40)
            grid_layout.addWidget( panel, 0, 0)
            ## --- panel ---
            #
            # here
            #

            self.cameraScreen = NCvideoDisplay(self)
            grid_layout.addWidget(self.cameraScreen, 1, 0)

            return section

        # ------------------ Section: Help Box ---------------------
        def build_section_help_box():
            # section = NCwidget(win)
            #
            # grid_layout = QGridLayout(section)
            # grid_layout.setContentsMargins(4,4,4,4)
            # grid_layout.setSpacing(2)

            self.helpBoxScreen = NCstaticIconImage(
                win,
                path=Styles.Assets.HELPBOX_BASE,
                size=(260, 260)
            )

            # grid_layout.addWidget(self.helpBoxScreen, 0, 0)

            return self.helpBoxScreen #section

        # ------------------ Section: Samples ---------------------
        def build_section_samples():
            section = NCwidget(win)

            grid_layout = QGridLayout(section)
            grid_layout.setContentsMargins(20,20,20,20)
            grid_layout.setSpacing(2)

            self.panel_flow_strem_hand_left = PanelFlowStream()
            self.panel_flow_strem_hand_right = PanelFlowStream()

            left_hand_ico = NCstaticIconImage(
                section,
                path=Styles.Assets.HAND_L,
                size=(60, 60)
            )
            right_hand_ico = NCstaticIconImage(
                section,
                path=Styles.Assets.HAND_R,
                size=(60, 60)
            )

            grid_layout.addWidget(left_hand_ico, 0, 0)
            grid_layout.addWidget(right_hand_ico, 1, 0)
            grid_layout.addWidget(self.panel_flow_strem_hand_right, 0, 1)
            grid_layout.addWidget(self.panel_flow_strem_hand_left,  1, 1)

            return section

        # ------------------ Section: Logs ---------------------
        def build_section_logs():
            section = NCwidget(win)

            grid_layout = QGridLayout(section)
            grid_layout.setContentsMargins(2,2,2,2)
            grid_layout.setSpacing(4)

            self.logsBox = LogsBox()
            self.logsBox.setFixedHeight(12  * self.logsBox.fontMetrics().lineSpacing() )
            grid_layout.addWidget(self.logsBox, 0, 0)

            size = self.logsBox.size()
            section.setFixedSize( QSize(size) )

            return section

        # ------------------ Section: Ask ---------------------
        def build_section_queue_ask():
            section = NCwidget(win)

            grid_layout = QGridLayout(section)
            grid_layout.setContentsMargins(20,20,20,20)
            grid_layout.setSpacing(4)

            self.ask_queue = WordQueue(self, stick_to_side="Up")
            self.ask_queue.setFixedWidth(180)

            grid_layout.addWidget(self.ask_queue, 0, 0)

            return section

        # ------------------ Section: Robot Panel ---------------------
        def build_section_robot_panel():
            section = NCwidget(win)

            grid_layout = QGridLayout(section)
            grid_layout.setContentsMargins(2,2,2,2)
            grid_layout.setSpacing(4)

            return section

        # ------------------ Section: Robot Status ---------------------
        def build_section_robot_status():
            section = NCwidget(win)

            grid_layout = QGridLayout(section)
            grid_layout.setContentsMargins(2, 2, 2, 2)
            grid_layout.setSpacing(4)

            return section

        # ------------------ Section: Connection Panel ---------------------
        def build_section_connection_panel():
            section = NCwidget(win)

            # Main grid layout configuration
            grid_layout = QGridLayout(section)
            grid_layout.setContentsMargins(20, 20, 20, 20)
            grid_layout.setSpacing(4)

            # Labels creation
            tl_title = TextLabel("Connection Panel", font_size=20)
            tl_conn = TextLabel("status", text_color="#ff0000", alignment="right")

            address = TextLabel("Server address:",  alignment="left")
            port = TextLabel("Server port:",  alignment="left")
            address_val = TextEntry( text =  "192.168.0.27")
            port_val = TextEntry(text = "8686")

            unit = TextLabel("Accessible unit", font_size=14)

            # Sub-layout for the robot list widget
            robot = QVBoxLayout()
            self.robotConnection = RobotListWidget()
            # self.robotConnection.setFixedWidth(300)
            robot.addWidget(self.robotConnection)

            # Populate grid layout
            grid_layout.addWidget(tl_title, 0, 0, 1, 2)
            grid_layout.addWidget(tl_conn, 1, 0, 1, 2)

            grid_layout.addWidget(address, 2, 0)
            grid_layout.addWidget(address_val, 2, 1)
            grid_layout.addWidget(port, 3, 0)
            grid_layout.addWidget(port_val, 3, 1)

            grid_layout.addWidget(unit, 4, 0, 1, 2)

            # Add nested sub-layout using addLayout instead of addWidget
            grid_layout.addLayout(robot, 5, 0, 1, 2)

            return section

        # ------------------ End section layout --------------------
        sectionCamera = build_section_camera()
        sectionHelpBox = build_section_help_box()
        sectionSamples = build_section_samples()
        sectionLogs = build_section_logs()
        sectionQueueAsk = build_section_queue_ask()
        sectionConnection = build_section_connection_panel()
        sectionRobotPanel = build_section_robot_panel()
        sectionRobotStatus = build_section_robot_status()

        Logs.print("GUI: [BUILD] Generate grid layout")

        grid_main.addWidget( sectionCamera,     0, 0)
        grid_main.addWidget( sectionHelpBox,    0, 1)
        grid_main.addWidget( sectionSamples,    1, 0, 1, 2)
        grid_main.addWidget( sectionLogs,       2, 0, 1, 2)

        grid_main.addWidget(sectionConnection,  0, 2, 1, 2)
        grid_main.addWidget(sectionRobotStatus, 0, 4, )

        grid_main.addWidget( sectionQueueAsk,   1, 2, 2, 1)
        grid_main.addWidget( sectionRobotPanel, 1, 3, 2, 2)

        self.show()
        NavigationCursor.generate_connection()
        NavigationCursor.set_cursor(win)

        Logs.print("GUI: [BUILD] End building UI components ")

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

