"""
    Custom container widget with selection-aware rounded borders.
"""

from typing import Optional

from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QPen, QColor, QBrush, QPaintEvent
from PyQt5.QtCore import QRectF

from src.ui.active.NavigationCursor import NavigationCursor
from src.ui.Styles import Styles

class NCwidget(QWidget, NavigationCursor):
    """
        Container widget rendering a rounded box with dynamic selection borders.

        :param navigation_parent: Parent widget, defaults to None.
    """

    def __init__(self, navigation_parent: Optional[QWidget] ) -> None:
        """
            Initialize the custom widget and set default color attributes.
        """
        super().__init__(parent=navigation_parent, navigation_parent=navigation_parent)

        self.backgroundColor: QColor = Styles.colorPallet.BgWidget
        self.FLAG_is_object_selected: bool = False

    def setBgColor(self, color: QColor | str):
        if isinstance(color, str):
            self.backgroundColor= QColor(color)
        elif isinstance(color, QColor):
            self.backgroundColor = color
        else:
            raise TypeError

    def paintEvent(self, event: QPaintEvent) -> None:
        """
            Render background fill

            :param event: Qt paint event trigger.
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        color_border = Styles.frame.getFrameColor( self.FLAG_is_object_selected )
        thickness = Styles.frame.thickness

        half = float( thickness )
        rect = QRectF(self.rect()).adjusted(half, half, -half, -half)

        painter.setBrush(QBrush(self.backgroundColor))

        pen = QPen(color_border)
        pen.setWidth( int( thickness ) )
        painter.setPen(pen)
        painter.drawRect(rect)
        # painter.drawRoundedRect(rect, 10.0, 10.0)
