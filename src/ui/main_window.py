"""Main application window: sidebar + stacked pages + system tray."""
from __future__ import annotations

import threading
from datetime import datetime, timedelta

from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject
from PyQt6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
                              QLabel, QFrame, QStackedWidget, QSystemTrayIcon,
                              QMenu, QApplication, QPushButton)
from PyQt6.QtGui import QAction

from . import theme as th
from .widgets import NavButton, make_app_icon
from .pages.dashboard import DashboardPage
from .pages.qibla_page import QiblaPage
from .pages.settings_page import SettingsPage
from .pages.dzikir_page import DzikirPage
from .pages.quran_page import QuranPage
from ..data.settings_manager import Settings, save as save_settings
from ..core.notification_manager import NotificationManager, PrayerAlertDialog
from ..core import prayer_calculator as pc
from .. import APP_NAME, VERSION
from ..i18n import t, prayer_name as i18n_prayer_name

# (icon, i18n_key, page_key)  — labels translated at _build() time
_MENU_DEF = [
    ("🕌", "nav_dashboard",  "Dashboard"),
    ("🧭", "nav_qibla",      "Qibla"),
    ("📿", "nav_dzikir",     "Dzikir"),
    ("📖", "nav_quran",      "Quran"),
    ("⚙️", "nav_settings",   "Settings"),
]


class _UpdateSignal(QObject):
    found = pyqtSignal(str, str)   # (version, url)


class MainWindow(QMainWindow):
    def __init__(self, settings: Settings):
        super().__init__()
        self.settings = settings
        self.icon = make_app_icon(64)

        self.setWindowTitle(APP_NAME)
        self.setWindowIcon(self.icon)
        self.resize(1100, 720)
        self.setMinimumSize(900, 600)

        # Apply font size from saved settings
        th.apply_font_size(settings.font_size)
        QApplication.instance().setStyleSheet(th.STYLESHEET)

        # Notification manager
        self._notif = NotificationManager(self)
        self._notif.sound_enabled       = settings.sound_enabled
        self._notif.custom_sound_path   = settings.custom_sound_path
        self._notif.prayer_sounds       = dict(settings.prayer_sounds)
        self._notif.toast_enabled       = settings.toast_enabled

        # Latest update info (populated by background check, shown in Settings)
        self._latest_version: str = ""
        self._latest_url:     str = ""

        # Track which prayers already triggered today
        self._triggered: set[str] = set()
        self._remind_timers: list[QTimer] = []

        # System tray
        self._tray: QSystemTrayIcon | None = None
        self._setup_tray()

        self._build()

        # Start prayer check timer (every 30 s)
        self._check_timer = QTimer(self)
        self._check_timer.timeout.connect(self._check_prayers)
        self._check_timer.start(30_000)
        self._check_prayers()

        # Check for update in background (delay 3s so UI loads first)
        QTimer.singleShot(3000, self._start_update_check)

    # ─── tray ────────────────────────────────────────────────────────────────

    def _setup_tray(self):
        if not QSystemTrayIcon.isSystemTrayAvailable():
            return
        self._tray = QSystemTrayIcon(self.icon, self)
        self._tray.setToolTip(APP_NAME)

        menu = QMenu()
        act_show = QAction(t("tray_show"), self)
        act_show.triggered.connect(self._show_from_tray)
        act_quit = QAction(t("tray_quit"), self)
        act_quit.triggered.connect(QApplication.quit)
        menu.addAction(act_show)
        menu.addSeparator()
        menu.addAction(act_quit)
        self._tray.setContextMenu(menu)
        self._tray.activated.connect(self._on_tray_activated)
        self._tray.show()

    def _show_from_tray(self):
        self.showNormal()
        self.raise_()
        self.activateWindow()

    def _on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self._show_from_tray()

    def closeEvent(self, event):
        if self.settings.minimize_to_tray and self._tray is not None:
            event.ignore()
            self.hide()
            self._tray.showMessage(APP_NAME, t("tray_bg_msg"),
                                   self.icon, 2000)
        else:
            event.accept()

    # ─── layout ──────────────────────────────────────────────────────────────

    def _build(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Sidebar
        side = QFrame()
        side.setObjectName("Sidebar")
        side.setFixedWidth(220)
        sl = QVBoxLayout(side)
        sl.setContentsMargins(12, 0, 12, 0)
        sl.setSpacing(0)

        # Brand block
        brand = QWidget()
        brand.setStyleSheet("background: transparent;")
        bl = QHBoxLayout(brand)
        bl.setContentsMargins(8, 20, 8, 18)
        bl.setSpacing(10)

        moon_lbl = QLabel("☪")
        moon_lbl.setStyleSheet(f"font-size: 28px; color: {th.ACCENT}; background: transparent;")
        bl.addWidget(moon_lbl)

        title_box = QVBoxLayout()
        title_box.setSpacing(0)
        n1 = QLabel("Muslim")
        n1.setStyleSheet(f"font-size: 18px; font-weight: 800; color: {th.ACCENT}; background: transparent;")
        n2 = QLabel("Desk")
        n2.setStyleSheet(f"font-size: 18px; font-weight: 800; color: {th.HEADING}; background: transparent;")
        title_box.addWidget(n1)
        title_box.addWidget(n2)
        bl.addLayout(title_box)
        bl.addStretch()
        sl.addWidget(brand)

        # Nav buttons
        self._nav_buttons: list[NavButton] = []
        for icon_char, label_key, page_key in _MENU_DEF:
            btn = NavButton(icon_char, t(label_key))
            btn.clicked.connect(lambda _, k=page_key: self._on_nav(k))
            self._nav_buttons.append(btn)
            sl.addWidget(btn)

        sl.addStretch()

        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background: {th.BORDER};")
        sl.addWidget(sep)

        ver = QLabel(f"v{VERSION}")
        ver.setStyleSheet(f"color: {th.MUTED}; padding: 12px 4px; background: transparent; font-size: 11px;")
        ver.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sl.addWidget(ver)

        root.addWidget(side)

        # ── Right column: stacked pages
        right_col = QVBoxLayout()
        right_col.setContentsMargins(0, 0, 0, 0)
        right_col.setSpacing(0)

        self.stack = QStackedWidget()
        right_col.addWidget(self.stack, 1)

        root.addLayout(right_col, 1)

        self._pages: dict[str, QWidget] = {}
        self._dash           = DashboardPage(self)
        self._qibla          = QiblaPage(self)
        self._settings_page  = SettingsPage(self)
        self._dzikir_page    = DzikirPage(self)
        self._quran_page     = QuranPage(self)

        for key, page in (
            ("Dashboard", self._dash),
            ("Qibla",     self._qibla),
            ("Dzikir",    self._dzikir_page),
            ("Quran",     self._quran_page),
            ("Settings",  self._settings_page),
        ):
            self._pages[key] = page
            self.stack.addWidget(page)

        self._on_nav("Dashboard")

    # ─── auto-update ─────────────────────────────────────────────────────────

    def _start_update_check(self):
        self._update_sig = _UpdateSignal()
        self._update_sig.found.connect(self._on_update_found)
        threading.Thread(target=self._update_thread, daemon=True).start()

    def _update_thread(self):
        from ..core.updater import check_for_update
        result = check_for_update(VERSION)
        if result:
            version, url = result
            self._update_sig.found.emit(version, url)

    def _on_update_found(self, version: str, url: str):
        self._latest_version = version
        self._latest_url = url
        if hasattr(self, "_settings_page"):
            self._settings_page.show_update_available(version, url)

    # ─── navigation ──────────────────────────────────────────────────────────

    def _on_nav(self, key: str):
        for i, (_, _, k) in enumerate(_MENU_DEF):
            self._nav_buttons[i].setChecked(k == key)
        page = self._pages.get(key)
        if page is None:
            return
        if hasattr(page, "refresh"):
            page.refresh()
        self.stack.setCurrentWidget(page)

    def navigate(self, key: str):
        self._on_nav(key)

    # ─── shared API used by pages ─────────────────────────────────────────

    def on_settings_changed(self):
        """Called by SettingsPage after user saves."""
        save_settings(self.settings)
        self._notif.sound_enabled     = self.settings.sound_enabled
        self._notif.custom_sound_path = self.settings.custom_sound_path
        self._notif.prayer_sounds     = dict(self.settings.prayer_sounds)
        self._notif.toast_enabled     = self.settings.toast_enabled
        if hasattr(self._dash, "refresh"):
            self._dash.refresh()
        if hasattr(self._qibla, "refresh"):
            self._qibla.refresh()

    def apply_theme_live(self, theme_name: str):
        actual = theme_name
        if theme_name == "system":
            actual = th.resolve_system_theme()
        th.apply_theme(actual, font_size=self.settings.font_size)
        QApplication.instance().setStyleSheet(th.STYLESHEET)
        self._rebuild_ui()

    def _rebuild_ui(self):
        current = next((k for i, (_, _, k) in enumerate(_MENU_DEF)
                        if self._nav_buttons[i].isChecked()), "Dashboard")
        self._build()
        self._on_nav(current)

    # ─── prayer time checker ─────────────────────────────────────────────────

    def _check_prayers(self):
        if not self.settings.notification_enabled:
            return
        from ..core.location_service import app_now
        now = app_now(self.settings.timezone)
        today = now.date()

        try:
            times = pc.times_as_datetime(
                today,
                self.settings.latitude,
                self.settings.longitude,
                self.settings.timezone,
                self.settings.method,
                self.settings.asr_method,
                self.settings.altitude,
            )
        except Exception:
            return

        for name, dt in times.items():
            if not self.settings.prayer_alarms.get(name, True):
                continue
            key = f"{today}_{name}"
            if key in self._triggered:
                continue
            delta = abs((dt - now).total_seconds())
            if delta <= 60:
                self._triggered.add(key)
                self._fire_prayer_alert(name, dt.strftime("%H:%M"))

        if now.hour == 0 and now.minute == 0:
            self._triggered = {k for k in self._triggered if str(today) in k}

    def _fire_prayer_alert(self, prayer_en: str, time_str: str):
        name_id = i18n_prayer_name(prayer_en) or pc.PRAYER_NAMES_ID.get(prayer_en, prayer_en)

        dlg = PrayerAlertDialog(name_id, prayer_en, time_str, self)
        dlg.remind_requested.connect(lambda m, n=prayer_en, ts=time_str: self._schedule_reminder(n, ts, m))

        def _on_sound_done():
            try:
                if dlg and not dlg.isHidden():
                    dlg.accept()
            except RuntimeError:
                pass

        self._notif.sound_finished.connect(_on_sound_done)

        def _on_dialog_closed():
            self._notif.stop_sound()
            try:
                self._notif.sound_finished.disconnect(_on_sound_done)
            except Exception:
                pass

        dlg.finished.connect(_on_dialog_closed)

        self._notif.play_adzan(prayer_en)

        # Windows Toast notification
        self._notif.show_toast(
            f"{t('tray_prayer_time')} {name_id}",
            t("toast_msg", name_id, time_str),
        )

        if self._tray and not self.isActiveWindow():
            self._tray.showMessage(
                f"{t('tray_prayer_time')} {name_id}",
                f"{t('tray_at')} {time_str}",
                self.icon, 8000,
            )
        dlg.show()

    def _schedule_reminder(self, prayer_en: str, time_str: str, minutes: int):
        tmr = QTimer(self)
        tmr.setSingleShot(True)
        tmr.timeout.connect(lambda: self._fire_prayer_alert(prayer_en, time_str))
        tmr.start(minutes * 60 * 1000)
        self._remind_timers.append(tmr)
