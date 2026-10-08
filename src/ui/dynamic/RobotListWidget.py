from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QPainter, QColor, QPen, QFont, QFontMetrics
from PyQt5.QtWidgets import (
    QStyledItemDelegate,
    QTableWidget,
    QTableWidgetItem,
    QAbstractItemView,
    QHeaderView
)


class SimpleListDelegate(QStyledItemDelegate):
    """Delegate for drawing single text cells with text eliding and custom highlight color."""

    def __init__(self, parent_widget):
        """
        Initialize the delegate.

        :param parent_widget: Parent widget associated with this delegate.
        """
        super().__init__(parent_widget)
        self.widget = parent_widget

    def paint(self, painter: QPainter, option, index):
        """
        Render a single item in the table.

        :param painter: Painter object used for drawing.
        :param option: Style option for the item.
        :param index: Model index of the item.
        """
        painter.save()
        painter.setRenderHint(QPainter.Antialiasing)

        row = index.row()
        rect = option.rect

        # Cell background: green highlight if it matches active index
        if row == self.widget.index:
            painter.fillRect(rect, self.widget.fill_active_color)
        else:
            painter.fillRect(rect, QColor("white"))

        # Text rendering with right side eliding (...)
        text = str(index.data(Qt.DisplayRole) or "")
        painter.setFont(self.widget.custom_font)
        painter.setPen(QPen(QColor("black")))

        # Internal text padding
        padding = 10
        text_rect = rect.adjusted(padding, 0, -padding, 0)

        metrics = QFontMetrics(self.widget.custom_font)
        elided_text = metrics.elidedText(text, Qt.ElideRight, text_rect.width())

        painter.drawText(text_rect, Qt.AlignLeft | Qt.AlignVCenter, elided_text)
        painter.restore()


class RobotListWidget(QTableWidget):
    """Custom table widget for displaying robot lists without stylesheets."""

    def __init__(self, parent=None, font_name="Consolas", font_size=10):
        """
        Initialize the robot list widget.

        :param parent: Parent widget, defaults to None.
        :param font_name: Name of the font family, defaults to "Consolas".
        :param font_size: Size of the font, defaults to 11.
        """
        super().__init__(parent)

        # Configuration and appearance parameters
        self.index = 0  # Default active item index
        self.fill_active_color = QColor("#2ECC71")  # Active highlight color

        self.cell_hight: int = 20  # Height of a single cell
        self.visual_actvie_cell: int = 4  # Number of visible rows

        # Global font setup
        self.custom_font = QFont(font_name, font_size)
        self.setFont(self.custom_font)

        # Table configuration
        self.setColumnCount(2)
        self.setHorizontalHeaderLabels(['robot', 'ip'])
        self.verticalHeader().setVisible(False)  # Hide row numbers

        # Disable grid lines and editing
        self.setShowGrid(False)
        self.setSelectionMode(QAbstractItemView.NoSelection)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # Header configuration and sizing
        header = self.horizontalHeader()
        header.setFont(self.custom_font)
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        # Scrollbar policies
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Set custom delegate
        self.setItemDelegate(SimpleListDelegate(self))

        # Apply sizing
        self.update_dimensions()

    def set_active_index(self, new_index: int):
        """
        Update the active item index and refresh the viewport.

        :param new_index: Target row index to highlight.
        """
        self.index = new_index
        self.viewport().update()

    def update_dimensions(self):
        """Update row height, header height, and total widget height."""
        # Row heights
        self.verticalHeader().setDefaultSectionSize(self.cell_hight)
        # Header height
        self.horizontalHeader().setFixedHeight(self.cell_hight)

        # Calculate widget height based on visible rows + header
        total_height = (self.cell_hight * self.visual_actvie_cell) + self.cell_hight
        self.setFixedHeight(total_height)

    def add_robot(self, robot_name: str, ip_address: str):
        """
        Add a new row with robot information.

        :param robot_name: Name of the robot.
        :param ip_address: IP address of the robot.
        """
        row_count = self.rowCount()
        self.insertRow(row_count)

        item_robot = QTableWidgetItem(robot_name)
        item_ip = QTableWidgetItem(ip_address)

        self.setItem(row_count, 0, item_robot)
        self.setItem(row_count, 1, item_ip)

    def paintEvent(self, event):
        """
        Paint event handler to draw standard content and custom borders.

        :param event: The paint event object.
        """
        super().paintEvent(event)

        painter = QPainter(self.viewport())
        painter.setRenderHint(QPainter.Antialiasing, False)
        rect = QRectF(0, 0, self.width(), self.height())
        painter.drawRect(rect)
        painter.end()