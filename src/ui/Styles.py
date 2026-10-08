from PyQt5.QtGui import QColor
from src.Config import PROJECT_PATH


class Styles:

    # ------------------ Frames --------------------
    class frame:
        thickness = 2

        color_frame_state: dict[bool, QColor] = {
            False: QColor(255, 255, 255),
            True: QColor(255, 0, 0),
        }

        @classmethod
        def getFrameColor(cls, staus):
            return cls.color_frame_state.get(staus, QColor(0, 0, 0))

    # ------------------ Colors --------------------
    class colorPallet:
        BgMain = QColor("#242e3d")
        BgWidget = QColor("#344257")

    # class assets:
    #     helpBox_base = "assets/ui/helpbox/base.png"

    class Assets:
        ROOT = PROJECT_PATH / "assets" / "ui"

        ACCESS_OFF = ROOT / "access_off.png"
        ACCESS_ON = ROOT / "access_on.png"

        AUTO = ROOT / "auto.png"

        HAND_L = ROOT / "hand_L.png"
        HAND = ROOT / "hand_.png"
        HAND_R = ROOT / "hand_R.png"

        HELPBOX = ROOT / "helpbox"
        HELPBOX_BASE = HELPBOX / "base.png"
        HELPBOX_CONNECT = HELPBOX / "connect.png"
        HELPBOX_INTERACT = HELPBOX / "interact.png"
        HELPBOX_MOVE = HELPBOX / "move.png"
        HELPBOX_MOVSYS = HELPBOX / "movsys.png"
        HELPBOX_RUNSYS = HELPBOX / "runsys.png"

        HELP_BOX_CONSTRUCTION = ROOT / "help_box_construction.svg"

        HIDE_CAMERA = ROOT / "hide_camera.png"
        HIDE_SCREEN = ROOT / "hide_screen.png"

        MANUAL = ROOT / "manual.png"

        MOTOR_OFF = ROOT / "motor_off.png"
        MOTOR_ON = ROOT / "motor_on.png"

        MOV_HELP_INFO = ROOT / "mov_help_info.png"

        RESUME_OFF = ROOT / "resume_off.png"
        RESUME_ON = ROOT / "resume_on.png"

        RUN_OFF = ROOT / "run_off.png"
        RUN_ON = ROOT / "run_on.png"

        SHOW_LANDMARK = ROOT / "show_landmark.png"

        STOP_OFF = ROOT / "stop_off.png"
        STOP_ON = ROOT / "stop_on.png"

        SWAP_MAIN_HAND = ROOT / "swap_main_hand.png"

        WIFI_CONNECT = ROOT / "wifi_connect.png"
        WIFI_DISCONNECT = ROOT / "wifi_disconnect.png"