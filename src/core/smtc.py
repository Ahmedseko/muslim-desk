"""Windows 11 System Media Transport Controls integration.

Uses a muted WinRT MediaPlayer for SMTC registration only;
actual audio is handled by QMediaPlayer in quran_page.py.
"""
from __future__ import annotations
import asyncio
import threading

from PyQt6.QtCore import QObject, pyqtSignal

try:
    from winrt.windows.media.playback import MediaPlayer as _WinRTPlayer
    from winrt.windows.media import (
        MediaPlaybackStatus as _Status,
        MediaPlaybackType as _Type,
        SystemMediaTransportControlsButton as _Btn,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False


class SMTCManager(QObject):
    """Sync Windows 11 lock-screen media controls with Quran audio."""

    play_pause_toggled  = pyqtSignal()
    next_requested      = pyqtSignal()
    prev_requested      = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._smtc   = None
        self._loop: asyncio.AbstractEventLoop | None = None

        if not _AVAILABLE:
            return

        self._loop = asyncio.new_event_loop()
        threading.Thread(target=self._loop.run_forever, daemon=True).start()
        asyncio.run_coroutine_threadsafe(self._init_async(), self._loop)

    async def _init_async(self):
        try:
            player = _WinRTPlayer()
            player.volume = 0.0
            player.auto_play = False

            smtc = player.system_media_transport_controls
            smtc.is_enabled          = True
            smtc.is_play_enabled     = True
            smtc.is_pause_enabled    = True
            smtc.is_next_enabled     = True
            smtc.is_previous_enabled = True
            smtc.is_stop_enabled     = True
            smtc.add_button_pressed(self._on_button)
            self._smtc = smtc
        except Exception:
            pass

    def _on_button(self, _sender, args):
        btn = args.button
        if btn in (_Btn.PLAY, _Btn.PAUSE):
            self.play_pause_toggled.emit()
        elif btn == _Btn.NEXT:
            self.next_requested.emit()
        elif btn == _Btn.PREVIOUS:
            self.prev_requested.emit()

    # ── public API ────────────────────────────────────────────────────────────

    def update_playing(self, surah_name: str, ayah: int, reciter: str):
        self._dispatch(self._update_async(surah_name, ayah, reciter))

    def update_paused(self):
        self._dispatch(self._set_status_async(_Status.PAUSED if _AVAILABLE else None))

    def update_stopped(self):
        self._dispatch(self._stop_async())

    # ── internals ─────────────────────────────────────────────────────────────

    def _dispatch(self, coro):
        if self._loop:
            asyncio.run_coroutine_threadsafe(coro, self._loop)

    async def _update_async(self, surah_name: str, ayah: int, reciter: str):
        if self._smtc is None:
            return
        try:
            upd = self._smtc.display_updater
            upd.type = _Type.MUSIC
            upd.music_properties.title        = f"{surah_name}  —  Ayat {ayah}"
            upd.music_properties.artist       = reciter
            upd.music_properties.album_title  = "Al-Qur'an"
            upd.update()
            self._smtc.playback_status = _Status.PLAYING
        except Exception:
            pass

    async def _set_status_async(self, status):
        if self._smtc and status is not None:
            try:
                self._smtc.playback_status = status
            except Exception:
                pass

    async def _stop_async(self):
        if self._smtc is None:
            return
        try:
            self._smtc.playback_status = _Status.STOPPED
            self._smtc.display_updater.clear_all()
        except Exception:
            try:
                self._smtc.playback_status = _Status.STOPPED
            except Exception:
                pass
