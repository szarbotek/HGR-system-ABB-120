from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.ui.components.MainWindow import MainWindow


class GuiController:

    def SIGNAL_A000_4CAM(self, *args):
        ts = args[0]
        frame = args[1]

        self.main_window.cameraScreen.update_frame(ts, frame)


    def __init__(self, main_window: 'MainWindow'):
        super().__init__()
        self.main_window = main_window

