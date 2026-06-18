"""Muslim Desk — Jadwal Sholat 5 Waktu untuk Windows 11."""
import sys
import os

# Ensure the project root is on sys.path so `src` is importable
sys.path.insert(0, os.path.dirname(__file__))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from src.data import settings_manager as sm
from src.ui import theme as th
from src.ui.main_window import MainWindow


def main():
    # High-DPI support
    os.environ.setdefault("QT_AUTO_SCREEN_SCALE_FACTOR", "1")

    app = QApplication(sys.argv)
    app.setApplicationName("Muslim Desk")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("muslim-desk")

    settings = sm.load()
    sm.save(settings)   # persist any safety-net corrections (e.g. prayer_alarms) immediately

    # Initialise language
    from src.i18n import set_language
    set_language(settings.language)

    # Resolve theme (system → detect from Windows registry)
    display_theme = settings.theme
    if display_theme == "system":
        display_theme = th.resolve_system_theme()

    th.apply_theme(display_theme)
    app.setStyleSheet(th.STYLESHEET)

    window = MainWindow(settings)
    if settings.start_minimized:
        window.showMinimized()
    else:
        window.showMaximized()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
