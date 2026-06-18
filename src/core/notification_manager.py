"""Windows prayer-time notification & alarm manager."""
from __future__ import annotations

import os
import threading
import winsound
from pathlib import Path

from PyQt6.QtCore import QObject, pyqtSignal, QTimer
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                              QPushButton, QFrame)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt


_SOUNDS_DIR = Path(__file__).parent.parent.parent / "assets" / "sounds"


class NotificationManager(QObject):
    prayer_arrived = pyqtSignal(str, str)   # english_name, time_str
    sound_finished = pyqtSignal()           # emitted when adzan sound ends

    def __init__(self, parent=None):
        super().__init__(parent)
        self.sound_enabled: bool = True
        self.custom_sound_path: str = ""
        self.prayer_sounds: dict[str, str] = {}
        self._playing = False

    def play_adzan(self, prayer_name: str = ""):
        if not self.sound_enabled:
            # no sound — emit immediately so dialog can start its fallback timer
            self.sound_finished.emit()
            return
        threading.Thread(target=self._play_sound, args=(prayer_name,), daemon=True).start()

    def _play_sound(self, prayer_name: str = ""):
        self._playing = True
        try:
            # 1. Per-prayer sound
            per_prayer = self.prayer_sounds.get(prayer_name, "")
            if per_prayer and Path(per_prayer).exists():
                winsound.PlaySound(per_prayer, winsound.SND_FILENAME)
                return
            # 2. Global custom sound
            if self.custom_sound_path and Path(self.custom_sound_path).exists():
                winsound.PlaySound(self.custom_sound_path, winsound.SND_FILENAME)
                return
            # 3. Default sounds in assets/sounds/
            for name in ("adzan.wav", "notification.wav"):
                p = _SOUNDS_DIR / name
                if p.exists():
                    winsound.PlaySound(str(p), winsound.SND_FILENAME)
                    return
            # 4. Built-in Windows beep fallback
            winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
        except Exception:
            pass
        finally:
            self._playing = False
            self.sound_finished.emit()  # queued to main thread via AutoConnection

    def stop_sound(self):
        try:
            winsound.PlaySound(None, winsound.SND_PURGE)
        except Exception:
            pass


class PrayerAlertDialog(QDialog):
    """Popup dialog shown when a prayer time arrives."""

    remind_requested = pyqtSignal(int)   # minutes

    def __init__(self, prayer_name_id: str, prayer_name_en: str,
                 time_str: str, parent=None):
        super().__init__(parent)
        self.prayer_name_en = prayer_name_en
        from src.i18n import t as _t
        self.setWindowTitle(_t("notif_title"))
        self.setWindowFlags(
            Qt.WindowType.Dialog
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.FramelessWindowHint
        )
        self.setModal(False)
        self.setMinimumWidth(360)
        self._build(prayer_name_id, time_str)

    def _build(self, name_id: str, time_str: str):
        from src.ui import theme as th
        from src.i18n import t as _t
        self.setStyleSheet(f"""
            QDialog {{
                background: {th.SURFACE};
                border: 2px solid {th.ACCENT_DK};
                border-radius: 16px;
            }}
            QLabel {{ background: transparent; color: {th.TEXT}; }}
        """)

        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(14)

        # Icon + title row
        top = QHBoxLayout()
        top.setSpacing(12)
        moon = QLabel("🕌")
        moon.setStyleSheet("font-size: 32px; background: transparent;")
        top.addWidget(moon)
        title_box = QVBoxLayout()
        title_box.setSpacing(2)
        lbl_title = QLabel(_t("notif_its_time"))
        lbl_title.setStyleSheet(f"font-size: 13px; font-weight: 600;"
                                 f"color: {th.MUTED}; background: transparent;")
        lbl_name = QLabel(name_id)
        lbl_name.setStyleSheet(f"font-size: 28px; font-weight: 800;"
                                f"color: {th.ACCENT}; background: transparent;")
        title_box.addWidget(lbl_title)
        title_box.addWidget(lbl_name)
        top.addLayout(title_box)
        top.addStretch()
        root.addLayout(top)

        # Time
        lbl_time = QLabel(time_str)
        lbl_time.setStyleSheet(f"font-size: 20px; font-weight: 700;"
                                f"color: {th.HEADING}; background: transparent;")
        lbl_time.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(lbl_time)

        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background: {th.BORDER};")
        root.addWidget(sep)

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)

        for mins in (5, 10, 15):
            b = QPushButton(_t("notif_remind", mins))
            b.setStyleSheet(f"""
                QPushButton {{
                    background: {th.SURFACE_2}; border: 1px solid {th.BORDER};
                    border-radius: 8px; padding: 8px 10px; font-size: 12px;
                    color: {th.TEXT};
                }}
                QPushButton:hover {{ background: {th.BTN_HOVER}; border-color: {th.ACCENT_DK}; }}
            """)
            b.clicked.connect(lambda _, m=mins: self._remind(m))
            btn_row.addWidget(b)

        root.addLayout(btn_row)

        btn_dismiss = QPushButton(_t("notif_close"))
        btn_dismiss.setObjectName("Primary")
        btn_dismiss.setStyleSheet(f"""
            QPushButton {{
                background: {th.ACCENT_DK}; border: none; border-radius: 8px;
                padding: 10px; color: #ffffff; font-size: 14px; font-weight: 600;
            }}
            QPushButton:hover {{ background: {th.ACCENT}; }}
        """)
        btn_dismiss.clicked.connect(self.accept)
        root.addWidget(btn_dismiss)

    def _remind(self, minutes: int):
        self.remind_requested.emit(minutes)
        self.accept()

    def showEvent(self, event):
        super().showEvent(event)
        # Position bottom-right near taskbar
        from PyQt6.QtWidgets import QApplication
        screen = QApplication.primaryScreen().availableGeometry()
        self.move(screen.right() - self.width() - 24,
                  screen.bottom() - self.height() - 24)
        # Fallback: auto-close after 15 minutes if sound signal never arrives
        self._fallback = QTimer(self)
        self._fallback.setSingleShot(True)
        self._fallback.timeout.connect(self.accept)
        self._fallback.start(15 * 60 * 1000)
