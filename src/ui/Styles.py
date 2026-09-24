from PyQt5.QtGui import QColor

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

    class assets:
        helpBox_base = "assets/ui/helpbox/base.png"
