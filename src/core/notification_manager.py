"""Prayer-time notification & alarm manager — QMediaPlayer (MP3+WAV) + winotify toast."""
from __future__ import annotations

import sys
import threading
from pathlib import Path

from PyQt6.QtCore import QObject, pyqtSignal, QTimer, QUrl
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                              QPushButton, QFrame)
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
        self.toast_enabled: bool = True

        # Qt multimedia player (runs on main thread, async)
        self._player = QMediaPlayer(self)
        self._audio_out = QAudioOutput(self)
        self._player.setAudioOutput(self._audio_out)
        self._player.playbackStateChanged.connect(self._on_playback_state)
        self._expect_finish = False

    def _on_playback_state(self, state: QMediaPlayer.PlaybackState):
        if state == QMediaPlayer.PlaybackState.StoppedState and self._expect_finish:
            self._expect_finish = False
            self.sound_finished.emit()

    def play_adzan(self, prayer_name: str = ""):
        if not self.sound_enabled:
            self.sound_finished.emit()
            return
        path = self._get_sound_path(prayer_name)
        if path:
            self._expect_finish = True
            self._player.setSource(QUrl.fromLocalFile(path))
            self._player.play()
        else:
            # No file found: system beep then done
            self._system_beep()
            self.sound_finished.emit()

    def _get_sound_path(self, prayer_name: str) -> str | None:
        per = self.prayer_sounds.get(prayer_name, "")
        if per and Path(per).exists():
            return per
        if self.custom_sound_path and Path(self.custom_sound_path).exists():
            return self.custom_sound_path
        for name in ("adzan.mp3", "adzan.wav", "notification.mp3", "notification.wav"):
            p = _SOUNDS_DIR / name
            if p.exists():
                return str(p)
        return None

    def _system_beep(self):
        if sys.platform == "win32":
            try:
                import winsound
                winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
            except Exception:
                pass

    def stop_sound(self):
        self._expect_finish = False
        self._player.stop()

    def show_toast(self, title: str, message: str):
        """Show a Windows 10/11 toast notification (non-blocking background thread)."""
        if not self.toast_enabled:
            return
        threading.Thread(target=self._toast_thread, args=(title, message), daemon=True).start()

    def _toast_thread(self, title: str, message: str):
        try:
            from winotify import Notification, audio
            toast = Notification(
                app_id="Muslim Desk",
                title=title,
                msg=message,
                duration="short",
            )
            toast.set_audio(audio.Default, loop=False)
            toast.show()
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

        lbl_time = QLabel(time_str)
        lbl_time.setStyleSheet(f"font-size: 20px; font-weight: 700;"
                                f"color: {th.HEADING}; background: transparent;")
        lbl_time.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(lbl_time)

        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background: {th.BORDER};")
        root.addWidget(sep)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)
        for mins in (5, 10, 15):
            b = QPushButton(_t("notif_remind", mins))
            b.setStyleSheet(f"""
                QPushButton {{
                    background: {th.SURFACE_2}; border: 1px solid {th.BORDER};
                    border-radius: 8px; padding: 8px 10px; font-size: 12px; color: {th.TEXT};
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
        from PyQt6.QtWidgets import QApplication
        screen = QApplication.primaryScreen().availableGeometry()
        self.move(screen.right() - self.width() - 24,
                  screen.bottom() - self.height() - 24)
        self._fallback = QTimer(self)
        self._fallback.setSingleShot(True)
        self._fallback.timeout.connect(self.accept)
        self._fallback.start(15 * 60 * 1000)
