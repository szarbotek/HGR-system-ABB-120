import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QTextEdit, QFrame
)
from PyQt5.QtCore import Qt, QTime
from PyQt5.QtGui import QFont, QColor


class TestAppWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.counter = 0
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("PyQt5 Environment Test")
        self.resize(500, 450)
        self.setMinimumSize(400, 350)

        # Global Application Styling (Dark Modern Theme)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e2e;
            }
            QLabel {
                color: #cdd6f4;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QPushButton {
                background-color: #89b4fa;
                color: #11111b;
                font-weight: bold;
                border-radius: 8px;
                padding: 10px 16px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #b4befe;
            }
            QPushButton:pressed {
                background-color: #74c7ec;
            }
            QLineEdit {
                background-color: #313244;
                color: #cdd6f4;
                border: 1px solid #45475a;
                border-radius: 6px;
                padding: 8px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 1px solid #89b4fa;
            }
            QTextEdit {
                background-color: #181825;
                color: #a6adc8;
                border: 1px solid #313244;
                border-radius: 6px;
                font-family: 'Consolas', monospace;
                font-size: 12px;
            }
        """)

        # Main Central Widget and Layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(16)

        # Header Label
        self.title_label = QLabel("🚀 PyQt5 System Active")
        self.title_label.setFont(QFont("Segoe UI", 18, QFont.Bold))
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("color: #a6e3a1;")
        main_layout.addWidget(self.title_label)

        # Subtitle / Status
        self.subtitle_label = QLabel("Qt Platform Plugin (XCB / Wayland) initialized successfully.")
        self.subtitle_label.setFont(QFont("Segoe UI", 10))
        self.subtitle_label.setAlignment(Qt.AlignCenter)
        self.subtitle_label.setStyleSheet("color: #bac2de;")
        main_layout.addWidget(self.subtitle_label)

        # Divider
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("color: #45475a;")
        main_layout.addWidget(line)

        # Counter Row
        counter_layout = QHBoxLayout()
        self.counter_label = QLabel("Counter: 0")
        self.counter_label.setFont(QFont("Segoe UI", 12, QFont.Bold))

        self.btn_increment = QPushButton("Click Me (+1)")
        self.btn_increment.setCursor(Qt.PointingHandCursor)
        self.btn_increment.clicked.connect(self.handle_click)

        counter_layout.addWidget(self.counter_label)
        counter_layout.addStretch()
        counter_layout.addWidget(self.btn_increment)
        main_layout.addLayout(counter_layout)

        # Custom Message Row
        input_layout = QHBoxLayout()
        self.msg_input = QLineEdit()
        self.msg_input.setPlaceholderText("Enter custom log message...")
        self.msg_input.returnPressed.connect(self.log_custom_message)

        self.btn_send = QPushButton("Log")
        self.btn_send.setCursor(Qt.PointingHandCursor)
        self.btn_send.setStyleSheet("""
            background-color: #a6e3a1; 
            color: #11111b; 
            font-weight: bold;
            border-radius: 8px;
            padding: 8px 16px;
        """)
        self.btn_send.clicked.connect(self.log_custom_message)

        input_layout.addWidget(self.msg_input)
        input_layout.addWidget(self.btn_send)
        main_layout.addLayout(input_layout)

        # Event Console Output
        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        main_layout.addWidget(self.log_box)

        # Log initial event
        self.add_log("System initialized and ready.")

    def add_log(self, text: str):
        timestamp = QTime.currentTime().toString("hh:mm:ss")
        self.log_box.append(f"[{timestamp}] {text}")

    def handle_click(self):
        self.counter += 1
        self.counter_label.setText(f"Counter: {self.counter}")
        self.add_log(f"Button pressed. Total clicks: {self.counter}")

    def log_custom_message(self):
        text = self.msg_input.text().strip()
        if text:
            self.add_log(f"User: {text}")
            self.msg_input.clear()


def main():
    app = QApplication(sys.argv)
    window = TestAppWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()