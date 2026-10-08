"""
    Custom log output widget built on top of QPlainTextEdit.
"""

from typing import Optional
from PyQt5.QtWidgets import QPlainTextEdit, QWidget

from src.utils.Logs import Logs


class LogsBox(QPlainTextEdit):
    """Read-only text console designed for displaying application logs.

    Provides automatic styling and efficient text appending while maintaining
    autoscroll functionality.

    :param parent: Parent widget, defaults to None.
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Initialize read-only state, font formatting, and component stylesheets."""
        super().__init__(parent=parent)

        self.setReadOnly(True)
        # # Ograniczenie bufora linii, aby konsola nie zjadła całej pamięci RAM
        self.setMaximumBlockCount(1000)

        # self.setStyleSheet("""
        #     QPlainTextEdit {
        #         background-color: white;
        #         color: black;
        #         font-family: Consolas, Monospace;
        #         font-size: 10pt;
        #     }
        # """)

        # Zapamiętujemy długość tekstu, który już wyświetliliśmy
        self._last_log_length: int = 0

    def refresh(self, timestamp_ms: Optional[int] = None) -> None:
        """Appends only new log content to the console efficiently.

        :param timestamp_ms: Optional timestamp parameter for sync.
        """
        full_text = Logs.stream_text

        # Jeśli tekst jest krótszy niż wcześniej (np. wyczyszczono logi), czyścimy konsolę
        if len(full_text) < self._last_log_length:
            self.clear()
            self._last_log_length = 0

        # Pobieramy tylko NOWY fragment tekstu
        new_content = full_text[self._last_log_length:]

        if new_content:
            self._last_log_length = len(full_text)

            # Sprawdzamy, czy użytkownik jest na samym dole paska przewijania
            scrollbar = self.verticalScrollBar()
            at_bottom = scrollbar.value() >= scrollbar.maximum() - 10

            # Dopisaną treść wstawiamy na koniec (bez usuwania starej)
            self.appendPlainText(new_content.strip())

            # Autoscroll: przewijamy na dół tylko jeśli użytkownik sam nie przewija w górę
            if at_bottom:
                scrollbar.setValue(scrollbar.maximum())