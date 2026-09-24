"""
    Widget components for rendering single, dual, and multi-state image icons in PyQt5.
"""

from typing import Optional

from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QPixmap, QPaintEvent, QPen, QColor
from PyQt5.QtCore import Qt

from src.ui.active.NavigationCursor import NavigationCursor
from src.ui.Styles import Styles

class NCstaticIconImage(QWidget, NavigationCursor):
    """
        Widget displaying a single static icon.

        :param navigation_parent: Parent widget, defaults to None.
        :param path: File path to the image asset, defaults to "".
        :param size: Target bounding box size in pixels, defaults to 100.
    """

    def __init__(
        self, navigation_parent: Optional[QWidget],
        path: str = "", size: tuple[int, int] = (100,100),
    ) -> None:
        """
            Initialize static icon with given dimensions and image path.
        """
        super().__init__(parent=navigation_parent, navigation_parent=navigation_parent)

        self.FLAG_is_object_selected: bool = False

        self._pixmap: QPixmap = QPixmap(path)

        t0, t1 = size

        self.setFixedSize( t0, t1 )
        self.setAttribute(Qt.WA_TransparentForMouseEvents)

    def paintEvent(self, event: QPaintEvent) -> None:
        """
            Render centered pixmap.

            :param event: Qt paint event instance.
        """
        if self._pixmap.isNull():
            return

        border_color =  Styles.frame.getFrameColor( self.FLAG_is_object_selected )

        painter = QPainter(self)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)

        pixmap = self._pixmap.scaled(
            self.width(),
            self.height(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation,
        )

        x = (self.width() - pixmap.width()) // 2
        y = (self.height() - pixmap.height()) // 2

        painter.drawPixmap(x, y, pixmap)

        pen = QPen(border_color, 2*Styles.frame.thickness)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)

        painter.drawRect(0, 0, self.width() - 1, self.height() - 1)

# class DoubleIconImage(QWidget):
#     """
#         Dual-state icon widget toggling between enabled and disabled pixmaps.
#
#         :param parent: Parent widget, defaults to None.
#         :param pathAcc: Image path for active state, defaults to "".
#         :param pathDis: Image path for inactive state, defaults to "".
#         :param base_state: Initial state flag, defaults to False.
#         :param size: Max dimension size in pixels, defaults to 100.
#     """
#
#     def __init__(
#         self,
#         parent: Optional[QWidget] = None,
#         pathAcc: str = "",
#         pathDis: str = "",
#         base_state: bool = False,
#         size: int = 100,
#     ) -> None:
#         """
#             Initialize dual-state icon with aspect-ratio-adjusted bounds.
#         """
#         super().__init__(parent)
#
#         self._pixmapAcc: QPixmap = QPixmap(pathAcc)
#         self._pixmapDis: QPixmap = QPixmap(pathDis)
#         self.FLAG_state: bool = base_state
#
#         if not self._pixmapAcc.isNull():
#             ratio = self._pixmapAcc.width() / self._pixmapAcc.height()
#             if ratio > 1:
#                 self.setFixedSize(size, int(size / ratio))
#             else:
#                 self.setFixedSize(int(size * ratio), size)
#         else:
#             self.setFixedSize(size, size)
#
#         self.setAttribute(Qt.WA_TransparentForMouseEvents)
#
#     def set_state(self, flag_of_state: bool) -> None:
#         """
#             Update display state flag and schedule redraw.
#
#             :param flag_of_state: Target state (True for active, False for inactive).
#         """
#         self.FLAG_state = flag_of_state
#         self.update()
#
#     def paintEvent(self, event: QPaintEvent) -> None:
#         """
#             Render active or inactive pixmap based on state flag.
#
#             :param event: Qt paint event instance.
#         """
#         painter = QPainter(self)
#         painter.setRenderHint(QPainter.SmoothPixmapTransform, True)
#
#         ico = self._pixmapAcc if self.FLAG_state else self._pixmapDis
#
#         if ico.isNull():
#             return
#
#         pixmap = ico.scaled(
#             self.width(),
#             self.height(),
#             Qt.KeepAspectRatio,
#             Qt.SmoothTransformation,
#         )
#
#         x = (self.width() - pixmap.width()) // 2
#         y = (self.height() - pixmap.height()) // 2
#
#         painter.drawPixmap(x, y, pixmap)
#
# class MultiIconImage(QWidget):
#     """
#         Multi-state icon widget cycling through a sequence of image paths.
#
#         :param parent: Parent widget, defaults to None.
#         :param paths: List of image file paths, defaults to ["None"].
#         :param index: Initial active image index, defaults to 0.
#         :param size: Max dimension size in pixels, defaults to 100.
#     """
#
#     def __init__(
#         self,
#         parent: Optional[QWidget] = None,
#         paths: Optional[List[str]] = None,
#         index: int = 0,
#         size: int = 100,
#     ) -> None:
#         """
#             Initialize multi-state icon with image sequence list.
#         """
#         super().__init__(parent)
#
#         self.ico_paths: List[str] = paths if paths is not None else ["None"]
#         self.index: int = index
#         self._pixmapActive: QPixmap = QPixmap(self.ico_paths[self.index])
#
#         if not self._pixmapActive.isNull():
#             ratio = self._pixmapActive.width() / self._pixmapActive.height()
#             if ratio > 1:
#                 self.setFixedSize(size, int(size / ratio))
#             else:
#                 self.setFixedSize(int(size * ratio), size)
#         else:
#             self.setFixedSize(size, size)
#
#         self.setAttribute(Qt.WA_TransparentForMouseEvents)
#
#     def next(self) -> None:
#         """
#         Advance to the next image index and request repaint.
#         """
#         self.index = (self.index + 1) % len(self.ico_paths)
#         self.update()
#
#     def prev(self) -> None:
#         """Move to the previous image index and request repaint."""
#         self.index = (self.index - 1) % len(self.ico_paths)
#         self.update()
#
#     def paintEvent(self, event: QPaintEvent) -> None:
#         """
#         Render active pixmap at current list index.
#         :param event: Qt paint event instance.
#         """
#         try:
#             painter = QPainter(self)
#             painter.setRenderHint(QPainter.SmoothPixmapTransform, True)
#
#             self._pixmapActive = QPixmap(self.ico_paths[self.index])
#             ico = self._pixmapActive
#
#             if ico.isNull():
#                 return
#
#             pixmap = ico.scaled(
#                 self.width(),
#                 self.height(),
#                 Qt.KeepAspectRatio,
#                 Qt.SmoothTransformation,
#             )
#
#             x = (self.width() - pixmap.width()) // 2
#             y = (self.height() - pixmap.height()) // 2
#
#             painter.drawPixmap(x, y, pixmap)
#         except Exception as e:
#             print(f"Error rendering MultiIconImage: {e}")