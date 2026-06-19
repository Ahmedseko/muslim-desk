"""Dashboard page: prayer times, countdown, Hijri date, location."""
from __future__ import annotations

import calendar
import threading
from datetime import datetime, timedelta, date

from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                              QLabel, QFrame, QPushButton, QScrollArea,
                              QSizePolicy, QProgressBar)
from PyQt6.QtGui import QFont

from ..widgets import PrayerCard, NextPrayerBanner, ClockWidget, DateHeader, SectionCard, CitySearchDialog
from .. import theme as th
from ...core import prayer_calculator as pc
from ...core.location_service import detect_location, app_now, local_timezone_offset, tz_label
from ...core.qibla_calculator import qibla_bearing, distance_to_mecca_km
from ...i18n import t, day_name as _day_name, month_name as _month_name, prayer_name as _prayer_name, get_language


_PRAYER_ORDER = ["Imsak", "Fajr", "Sunrise", "Dhuhr", "Asr", "Maghrib", "Isha"]
_MAIN_PRAYERS = ["Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"]  # without Sunrise for cards row


def _fmt_time(hhmm: str, fmt: str) -> str:
    """Convert 'HH:MM' string to 12h or 24h display format."""
    if not hhmm or hhmm in ("--:--", "—", ""):
        return hhmm
    try:
        h, m = map(int, hhmm.split(":"))
        if fmt == "12h":
            period = "AM" if h < 12 else "PM"
            return f"{h % 12 or 12}:{m:02d} {period}"
        return hhmm
    except Exception:
        return hhmm


class DashboardPage(QWidget):
    _location_detected = pyqtSignal(object)   # LocationInfo

    def __init__(self, main_win):
        super().__init__()
        self._win = main_win
        self._prayer_cards: dict[str, PrayerCard] = {}
        self._today_times: dict[str, str] = {}
        self._today_times_date: date | None = None
        self._next_prayer: str = ""
        self._schedule_mode = "7days"  # "7days" | "15days" | "month"
        self._build()

        self._location_detected.connect(self._on_location_detected)

        self._tick_timer = QTimer(self)
        self._tick_timer.timeout.connect(self._tick)
        self._tick_timer.start(1000)

        self.refresh()

    # ─── build ──────────────────────────────────────────────────────────────

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 20, 28, 20)
        root.setSpacing(16)

        # ── Top header row
        header_row = QHBoxLayout()
        header_row.setSpacing(12)

        title_col = QVBoxLayout()
        title_col.setSpacing(2)
        lbl_title = QLabel("Dashboard")
        lbl_title.setObjectName("H1")
        title_col.addWidget(lbl_title)

        self._date_header = DateHeader()
        title_col.addWidget(self._date_header)
        header_row.addLayout(title_col)

        # Ramadan badge (hidden unless Ramadan)
        self._ramadan_badge = QLabel("")
        self._ramadan_badge.setStyleSheet(
            f"color: #f59e0b; font-size: 13px; font-weight: 700; "
            f"background: rgba(245,158,11,0.12); border: 1px solid rgba(245,158,11,0.4); "
            f"border-radius: 8px; padding: 4px 12px;"
        )
        self._ramadan_badge.hide()
        header_row.addWidget(self._ramadan_badge)

        header_row.addStretch()

        # Location info + refresh button
        loc_col = QVBoxLayout()
        loc_col.setAlignment(Qt.AlignmentFlag.AlignRight)
        loc_col.setSpacing(4)

        self._loc_label = QLabel(t("loading_loc"))
        self._loc_label.setStyleSheet(f"color: {th.MUTED}; font-size: 13px; background: transparent;")
        self._loc_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        loc_col.addWidget(self._loc_label)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(6)
        self._btn_search_city = QPushButton(t("search_city_btn"))
        self._btn_search_city.setFixedHeight(32)
        self._btn_search_city.clicked.connect(self._open_city_search)
        self._btn_refresh_loc = QPushButton(t("auto_location_btn"))
        self._btn_refresh_loc.setObjectName("Primary")
        self._btn_refresh_loc.setFixedHeight(32)
        self._btn_refresh_loc.clicked.connect(self._update_location)
        btn_row.addWidget(self._btn_search_city)
        btn_row.addWidget(self._btn_refresh_loc)
        loc_col.addLayout(btn_row)
        header_row.addLayout(loc_col)

        root.addLayout(header_row)

        # ── Timezone mismatch warning bar
        self._tz_bar = QFrame()
        self._tz_bar.setStyleSheet(
            "QFrame { background: rgba(245,158,11,0.13); "
            "border: 1px solid rgba(245,158,11,0.45); "
            "border-left: 4px solid #f59e0b; border-radius: 10px; }"
        )
        tz_lay = QHBoxLayout(self._tz_bar)
        tz_lay.setContentsMargins(14, 8, 14, 8)
        tz_lay.setSpacing(10)

        tz_icon = QLabel("⚠️")
        tz_icon.setStyleSheet("font-size: 15px; background: transparent;")
        tz_lay.addWidget(tz_icon)

        self._tz_bar_lbl = QLabel("")
        self._tz_bar_lbl.setStyleSheet(
            f"color: {th.TEXT}; font-size: 12px; font-weight: 400; background: transparent;"
        )
        self._tz_bar_lbl.setWordWrap(True)
        tz_lay.addWidget(self._tz_bar_lbl, 1)

        _btn_style = (
            f"QPushButton {{ background: rgba(245,158,11,0.18); border: 1px solid rgba(245,158,11,0.55); "
            f"border-radius: 6px; padding: 4px 12px; color: #f59e0b; font-size: 12px; font-weight: 600; }}"
            f"QPushButton:hover {{ background: rgba(245,158,11,0.32); }}"
        )
        self._btn_use_sys_tz = QPushButton(t("tz_use_system"))
        self._btn_use_sys_tz.setFixedHeight(30)
        self._btn_use_sys_tz.setStyleSheet(_btn_style)
        self._btn_use_sys_tz.clicked.connect(self._apply_system_timezone)
        tz_lay.addWidget(self._btn_use_sys_tz)

        btn_tz_dismiss = QPushButton(t("tz_dismiss"))
        btn_tz_dismiss.setFixedHeight(30)
        btn_tz_dismiss.setStyleSheet(_btn_style)
        btn_tz_dismiss.clicked.connect(lambda: self._tz_bar.setVisible(False))
        tz_lay.addWidget(btn_tz_dismiss)

        self._tz_bar.setVisible(False)
        root.addWidget(self._tz_bar)

        # ── Clock + Next Prayer Banner
        top_row = QHBoxLayout()
        top_row.setSpacing(16)

        clock_card = QFrame()
        clock_card.setObjectName("Card")
        clock_layout = QVBoxLayout(clock_card)
        clock_layout.setContentsMargins(20, 16, 20, 16)
        clock_layout.setSpacing(4)
        lbl_now = QLabel(t("current_time"))
        lbl_now.setStyleSheet(f"font-size: 12px; color: {th.MUTED}; font-weight: 500; background: transparent;")
        self._clock = ClockWidget()
        clock_layout.addWidget(lbl_now)
        clock_layout.addWidget(self._clock)
        top_row.addWidget(clock_card, 1)

        self._banner = NextPrayerBanner()
        top_row.addWidget(self._banner, 2)

        root.addLayout(top_row)

        # ── Prayer progress bar
        prog_card = QFrame()
        prog_card.setObjectName("Card")
        prog_layout = QVBoxLayout(prog_card)
        prog_layout.setContentsMargins(16, 10, 16, 10)
        prog_layout.setSpacing(6)

        prog_top = QHBoxLayout()
        lbl_prog = QLabel(t("progress_lbl"))
        lbl_prog.setStyleSheet(f"font-size: 11px; color: {th.MUTED}; background: transparent;")
        self._progress_pct = QLabel("0%")
        self._progress_pct.setStyleSheet(
            f"font-size: 11px; font-weight: 700; color: {th.ACCENT}; background: transparent;"
        )
        prog_top.addWidget(lbl_prog)
        prog_top.addStretch()
        prog_top.addWidget(self._progress_pct)

        self._progress = QProgressBar()
        self._progress.setRange(0, 1000)
        self._progress.setValue(0)
        self._progress.setTextVisible(False)
        self._progress.setFixedHeight(14)
        self._progress.setStyleSheet(
            f"QProgressBar {{ background: {th.SURFACE_2}; border: 1px solid {th.BORDER}; "
            f"border-radius: 7px; }}"
            f"QProgressBar::chunk {{ background: {th.ACCENT_DK}; border-radius: 6px; }}"
        )
        prog_layout.addLayout(prog_top)
        prog_layout.addWidget(self._progress)
        root.addWidget(prog_card)

        # ── 5 Prayer Cards
        cards_row = QHBoxLayout()
        cards_row.setSpacing(10)

        for name in _MAIN_PRAYERS:
            color = th.PRAYER_COLORS[name]
            name_id = _prayer_name(name) or pc.PRAYER_NAMES_ID[name]
            card = PrayerCard(name, name_id, color)
            card.alarm_toggled.connect(self._on_alarm_toggled)
            self._prayer_cards[name] = card
            cards_row.addWidget(card)

        root.addLayout(cards_row)

        # ── Prayer log
        root.addWidget(self._build_log_card())

        # ── Bottom two-panel section
        bottom = QHBoxLayout()
        bottom.setSpacing(12)
        bottom.addWidget(self._build_weekly_card(), 55)
        bottom.addWidget(self._build_hijri_card(),  45)
        root.addLayout(bottom, 1)

        # Status bar
        self._status = QLabel("")
        self._status.setStyleSheet(f"font-size: 11px; color: {th.MUTED}; background: transparent;")
        self._status.setAlignment(Qt.AlignmentFlag.AlignRight)
        root.addWidget(self._status)

    # ─── prayer log card ─────────────────────────────────────────────────────

    def _build_log_card(self) -> QFrame:
        from ...core import prayer_log as pl
        from ...i18n import t as _t, prayer_name as _pn
        import src.core.prayer_calculator as _pc

        card = QFrame()
        card.setObjectName("Card")
        lay = QVBoxLayout(card)
        lay.setContentsMargins(16, 10, 16, 12)
        lay.setSpacing(8)

        # Header row
        hdr = QHBoxLayout()
        title = QLabel(_t("log_title"))
        title.setStyleSheet(
            f"font-size: 12px; font-weight: 700; color: {th.MUTED}; background: transparent;"
        )
        hdr.addWidget(title)
        hdr.addStretch()
        self._streak_lbl = QLabel("")
        self._streak_lbl.setStyleSheet(
            f"font-size: 12px; font-weight: 700; color: {th.ACCENT}; background: transparent;"
        )
        hdr.addWidget(self._streak_lbl)
        lay.addLayout(hdr)

        # Buttons row
        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)

        self._log_data = pl.load_today()
        self._log_btns: dict[str, QPushButton] = {}

        for name in pl.MAIN_PRAYERS:
            label = _pn(name) or _pc.PRAYER_NAMES_ID.get(name, name)
            btn = QPushButton()
            btn.setFixedHeight(40)
            btn.setMinimumWidth(90)
            btn.setCheckable(True)
            btn.setChecked(self._log_data.get(name, False))
            self._log_btns[name] = btn
            self._apply_log_btn_style(btn, name, btn.isChecked(), label)
            btn.clicked.connect(lambda checked, n=name, lbl=label: self._on_log_toggle(n, checked, lbl))
            btn_row.addWidget(btn, 1)

        lay.addLayout(btn_row)

        streak = pl.load_streak()
        if streak > 0:
            from ...i18n import t as _t2
            self._streak_lbl.setText(_t2("log_streak", streak))

        return card

    def _apply_log_btn_style(self, btn: QPushButton, prayer: str, done: bool, label: str = ""):
        color = th.PRAYER_COLORS[prayer]
        if not label:
            label = btn.text().lstrip("✓ ").lstrip("○ ")
        if done:
            btn.setText(f"✓  {label}")
            btn.setStyleSheet(
                f"QPushButton {{"
                f"  background: {color};"
                f"  border: none;"
                f"  border-radius: 8px;"
                f"  color: #ffffff;"
                f"  font-size: 12px;"
                f"  font-weight: 700;"
                f"  padding: 0 8px;"
                f"}}"
                f"QPushButton:hover {{"
                f"  background: {color}cc;"
                f"}}"
            )
        else:
            btn.setText(f"○  {label}")
            btn.setStyleSheet(
                f"QPushButton {{"
                f"  background: {th.SURFACE_2};"
                f"  border: 1px solid {th.BORDER};"
                f"  border-radius: 8px;"
                f"  color: {th.MUTED};"
                f"  font-size: 12px;"
                f"  font-weight: 500;"
                f"  padding: 0 8px;"
                f"}}"
                f"QPushButton:hover {{"
                f"  border-color: {color};"
                f"  color: {color};"
                f"}}"
            )

    def _on_log_toggle(self, prayer: str, checked: bool, label: str = ""):
        from ...core import prayer_log as pl
        self._log_data[prayer] = checked
        pl.save_today(self._log_data)
        btn = self._log_btns[prayer]
        self._apply_log_btn_style(btn, prayer, checked, label)
        streak = pl.load_streak()
        if streak > 0:
            from ...i18n import t as _t
            self._streak_lbl.setText(_t("log_streak", streak))
        else:
            self._streak_lbl.setText("")

    # ─── refresh ─────────────────────────────────────────────────────────────

    def refresh(self):
        s = self._win.settings
        today = app_now(s.timezone).date()

        # Gregorian
        greg = (f"{_day_name(today.weekday())}, "
                f"{today.day} {_month_name(today.month)} {today.year}")
        # Hijri
        hy, hm, hd = pc.gregorian_to_hijri(today.year, today.month, today.day)
        hijri = pc.format_hijri(hy, hm, hd)
        self._date_header.update_dates(greg, hijri)

        # Ramadan badge
        if hm == 9:
            self._ramadan_badge.setText(f"{t('ramadan_badge')} {hy} H")
            self._ramadan_badge.show()
        else:
            self._ramadan_badge.hide()

        # Location label
        self._loc_label.setText(f"📍 {s.city}, {s.country}")

        # Calculate times (with Imsak if enabled)
        try:
            self._today_times = pc.calculate_times(
                today, s.latitude, s.longitude, s.timezone,
                s.method, s.asr_method, s.altitude,
                imsak_minutes=s.imsak_minutes,
            )
            self._today_times_date = today
        except Exception as e:
            self._status.setText(t("calc_failed") + str(e))
            return

        # Update cards
        tfmt = s.time_format
        self._clock.set_format(tfmt)
        for name, card in self._prayer_cards.items():
            raw = self._today_times.get(name, "--:--")
            card.set_time(_fmt_time(raw, tfmt))
            card.set_alarm(s.prayer_alarms.get(name, True))

        self._refresh_weekly_schedule()
        self._refresh_hijri_calendar()
        self._check_timezone_mismatch()
        self._tick()

    # ─── countdown tick ──────────────────────────────────────────────────────

    def _tick(self):
        now   = app_now(self._win.settings.timezone)
        today = now.date()

        if self._today_times_date != today:
            self.refresh()
            return

        if not self._today_times:
            return

        # Build prayer datetimes (skip Imsak for countdown purposes)
        order = [p for p in _PRAYER_ORDER if p != "Imsak"]
        dts: dict[str, datetime] = {}
        for name in order:
            tv = self._today_times.get(name)
            if tv:
                h, m = map(int, tv.split(":"))
                dts[name] = datetime(today.year, today.month, today.day, h, m)

        # Find next prayer (today)
        next_name: str | None = None
        next_dt:   datetime | None = None
        for name in order:
            dt = dts.get(name)
            if dt and dt > now:
                next_name = name
                next_dt   = dt
                break

        prev_name: str | None = None
        prev_dt:   datetime | None = None
        for name in reversed(order):
            dt = dts.get(name)
            if dt and dt <= now:
                prev_name = name
                prev_dt   = dt
                break

        # If all today's prayers passed → tomorrow's Fajr
        tomorrow_fajr = False
        if next_dt is None:
            tomorrow = today + timedelta(days=1)
            s = self._win.settings
            try:
                tmr_times = pc.calculate_times(
                    tomorrow, s.latitude, s.longitude, s.timezone,
                    s.method, s.asr_method, s.altitude,
                )
                fh, fm = map(int, tmr_times["Fajr"].split(":"))
                next_name = "Fajr"
                next_dt   = datetime(tomorrow.year, tomorrow.month, tomorrow.day, fh, fm)
                tomorrow_fajr = True
                if prev_dt is None and dts.get("Isha"):
                    prev_dt = dts["Isha"]
            except Exception:
                pass

        if prev_dt is None and next_name == "Fajr" and not tomorrow_fajr:
            yesterday = today - timedelta(days=1)
            s = self._win.settings
            try:
                ytd = pc.calculate_times(
                    yesterday, s.latitude, s.longitude, s.timezone,
                    s.method, s.asr_method, s.altitude,
                )
                ih, im = map(int, ytd["Isha"].split(":"))
                prev_dt = datetime(yesterday.year, yesterday.month, yesterday.day, ih, im)
            except Exception:
                pass

        # Update prayer cards
        for name, card in self._prayer_cards.items():
            is_next = (name == next_name and not tomorrow_fajr)
            card.set_active(is_next)
            if is_next and next_dt:
                remaining = next_dt - now
                secs = int(remaining.total_seconds())
                hh, rem = divmod(secs, 3600)
                mi, ss  = divmod(rem, 60)
                card.set_countdown(f"dalam {hh:02d}:{mi:02d}:{ss:02d}")
            else:
                card.set_countdown("")

        if next_name and next_dt:
            remaining = next_dt - now
            secs = int(remaining.total_seconds())
            hh, rem = divmod(secs, 3600)
            mi, ss  = divmod(rem, 60)
            countdown_str = f"{hh:02d}:{mi:02d}:{ss:02d}"
            color = th.PRAYER_COLORS.get(next_name, th.ACCENT)

            label_id = _prayer_name(next_name) or pc.PRAYER_NAMES_ID.get(next_name, next_name)
            if tomorrow_fajr:
                label_id += t("tomorrow_suffix")

            time_display = _fmt_time(next_dt.strftime("%H:%M"), self._win.settings.time_format)
            self._banner.update_next(label_id, time_display, countdown_str, color)
            self._next_prayer = next_name

            if prev_dt:
                total   = (next_dt - prev_dt).total_seconds()
                elapsed = (now    - prev_dt).total_seconds()
                frac    = max(0.0, min(1.0, elapsed / total)) if total > 0 else 0.0
                pct     = int(frac * 100)
                self._progress.setValue(int(frac * 1000))
                self._progress.setStyleSheet(
                    f"QProgressBar {{ background: {th.SURFACE_2}; border: 1px solid {th.BORDER}; "
                    f"border-radius: 7px; }}"
                    f"QProgressBar::chunk {{ background: {color}; border-radius: 6px; }}"
                )
                self._progress_pct.setText(f"{pct}%")
                self._progress_pct.setStyleSheet(
                    f"font-size: 11px; font-weight: 700; color: {color}; background: transparent;"
                )
            else:
                self._progress.setValue(0)
                self._progress_pct.setText("0%")
        else:
            self._banner.update_next("—", "—", "—", th.MUTED)
            self._progress.setValue(0)
            self._progress_pct.setText("0%")

    # ─── timezone mismatch ───────────────────────────────────────────────────

    def _check_timezone_mismatch(self):
        sys_tz  = local_timezone_offset()
        app_tz  = self._win.settings.timezone
        diff    = app_tz - sys_tz
        if abs(diff) >= 0.5:
            sys_name = tz_label(sys_tz)
            app_name = tz_label(app_tz)
            self._tz_bar_lbl.setText(
                f"Peringatan zona waktu — Laptop: {sys_name}  |  "
                f"Lokasi pilihan: {app_name}.  "
                f"Waktu sholat & countdown sudah dikoreksi ke {app_name}."
            )
            self._tz_bar.setVisible(True)
        else:
            self._tz_bar.setVisible(False)

    def _apply_system_timezone(self):
        sys_tz = local_timezone_offset()
        self._win.settings.timezone = sys_tz
        from ...data.settings_manager import save as save_s
        save_s(self._win.settings)
        self._tz_bar.setVisible(False)
        self.refresh()

    # ─── location update ─────────────────────────────────────────────────────

    def _open_city_search(self):
        dlg = CitySearchDialog(self)
        dlg.location_selected.connect(self._on_location_detected)
        dlg.exec()

    def _update_location(self):
        self._btn_refresh_loc.setText(t("detecting_loc"))
        self._btn_refresh_loc.setEnabled(False)
        self._status.setText(t("detecting_via_ip"))
        threading.Thread(target=self._detect_thread, daemon=True).start()

    def _detect_thread(self):
        loc = detect_location()
        self._location_detected.emit(loc)

    def _on_location_detected(self, loc):
        s = self._win.settings
        s.latitude      = loc.latitude
        s.longitude     = loc.longitude
        s.city          = loc.city
        s.country       = loc.country
        s.timezone      = loc.timezone
        s.timezone_name = loc.timezone_name
        if loc.country_code:
            from ...core.location_service import method_for_country
            s.method = method_for_country(loc.country_code)
        from ...data.settings_manager import save as save_s
        save_s(s)
        self._btn_refresh_loc.setText(t("refresh_location_btn"))
        self._btn_refresh_loc.setEnabled(True)
        self._status.setText(t("loc_updated") + loc.display_name())
        self.refresh()

    # ─── alarm toggles ───────────────────────────────────────────────────────

    def _on_alarm_toggled(self, prayer_en: str, enabled: bool):
        self._win.settings.prayer_alarms[prayer_en] = enabled
        from ...data.settings_manager import save as save_s
        save_s(self._win.settings)

    # ─── weekly / monthly schedule ───────────────────────────────────────────

    def _build_weekly_card(self) -> SectionCard:
        card = SectionCard(t("weekly_title"))

        # Toggle buttons row
        toggle_row = QHBoxLayout()
        toggle_row.setSpacing(6)
        toggle_row.addStretch()

        self._btn_7days = QPushButton(t("schedule_7days"))
        self._btn_7days.setFixedHeight(26)
        self._btn_7days.setStyleSheet(
            f"QPushButton {{ background: {th.ACCENT_DK}; border: none; border-radius: 6px; "
            f"color: #fff; font-size: 11px; padding: 2px 10px; font-weight: 700; }}"
        )
        self._btn_7days.clicked.connect(lambda: self._set_schedule_mode("7days"))

        self._btn_15days = QPushButton(t("schedule_15days"))
        self._btn_15days.setFixedHeight(26)
        self._btn_15days.setStyleSheet(
            f"QPushButton {{ background: {th.SURFACE_2}; border: 1px solid {th.BORDER}; "
            f"border-radius: 6px; color: {th.MUTED}; font-size: 11px; padding: 2px 10px; }}"
        )
        self._btn_15days.clicked.connect(lambda: self._set_schedule_mode("15days"))

        self._btn_month = QPushButton(t("schedule_month"))
        self._btn_month.setFixedHeight(26)
        self._btn_month.setStyleSheet(
            f"QPushButton {{ background: {th.SURFACE_2}; border: 1px solid {th.BORDER}; "
            f"border-radius: 6px; color: {th.MUTED}; font-size: 11px; padding: 2px 10px; }}"
        )
        self._btn_month.clicked.connect(lambda: self._set_schedule_mode("month"))

        toggle_row.addWidget(self._btn_7days)
        toggle_row.addWidget(self._btn_15days)
        toggle_row.addWidget(self._btn_month)
        card.body.addLayout(toggle_row)

        # Scroll area for the grid (needed for monthly)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setMinimumHeight(160)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        scroll.viewport().setStyleSheet("background: transparent;")

        self._schedule_container = QWidget()
        self._schedule_container.setStyleSheet("background: transparent;")
        self._schedule_grid_layout = QVBoxLayout(self._schedule_container)
        self._schedule_grid_layout.setContentsMargins(0, 0, 0, 0)
        self._schedule_grid_layout.setSpacing(0)

        scroll.setWidget(self._schedule_container)
        card.body.addWidget(scroll, 1)
        card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._schedule_scroll = scroll
        return card

    def _set_schedule_mode(self, mode: str):
        self._schedule_mode = mode
        active_style = (
            f"QPushButton {{ background: {th.ACCENT_DK}; border: none; border-radius: 6px; "
            f"color: #fff; font-size: 11px; padding: 2px 10px; font-weight: 700; }}"
        )
        inactive_style = (
            f"QPushButton {{ background: {th.SURFACE_2}; border: 1px solid {th.BORDER}; "
            f"border-radius: 6px; color: {th.MUTED}; font-size: 11px; padding: 2px 10px; }}"
        )
        self._btn_7days.setStyleSheet(active_style if mode == "7days"  else inactive_style)
        self._btn_15days.setStyleSheet(active_style if mode == "15days" else inactive_style)
        self._btn_month.setStyleSheet(active_style if mode == "month"  else inactive_style)
        self._refresh_weekly_schedule()

    @staticmethod
    def _calc_dhuha(times: dict) -> str:
        """Dhuha = Sunrise + (Dhuhr - Sunrise) / 4  (quarter-day formula)."""
        try:
            sr = times.get("Sunrise", "")
            dh = times.get("Dhuhr", "")
            if not sr or not dh:
                return "--:--"
            sr_h, sr_m = map(int, sr.split(":"))
            dh_h, dh_m = map(int, dh.split(":"))
            sr_mins = sr_h * 60 + sr_m
            dh_mins = dh_h * 60 + dh_m
            duha = sr_mins + (dh_mins - sr_mins) // 4
            return f"{duha // 60:02d}:{duha % 60:02d}"
        except Exception:
            return "--:--"

    def _refresh_weekly_schedule(self):
        if not hasattr(self, "_schedule_grid_layout"):
            return

        # Clear existing layout
        while self._schedule_grid_layout.count():
            item = self._schedule_grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())

        s = self._win.settings
        today = date.today()
        tfmt = s.time_format

        if self._schedule_mode == "7days":
            days = [today + timedelta(days=i) for i in range(7)]
        elif self._schedule_mode == "15days":
            days = [today + timedelta(days=i) for i in range(15)]
        else:
            year, month = today.year, today.month
            _, days_in_month = calendar.monthrange(year, month)
            days = [date(year, month, d) for d in range(1, days_in_month + 1)]

        # 6 prayer columns: Fajr, Dhuha, Dhuhr, Asr, Maghrib, Isha
        PKEY = ["Fajr", "Dhuha", "Dhuhr", "Asr", "Maghrib", "Isha"]
        PCOL = [
            th.PRAYER_COLORS["Fajr"],    th.PRAYER_COLORS["Dhuha"],
            th.PRAYER_COLORS["Dhuhr"],   th.PRAYER_COLORS["Asr"],
            th.PRAYER_COLORS["Maghrib"], th.PRAYER_COLORS["Isha"],
        ]

        grid_widget = QWidget()
        grid_widget.setStyleSheet("background: transparent;")
        grid = QGridLayout(grid_widget)
        grid.setVerticalSpacing(0)
        grid.setHorizontalSpacing(0)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setColumnStretch(0, 36)
        for c in range(1, 7):
            grid.setColumnStretch(c, 11)

        hdrs = [(t("weekly_col_date"), th.MUTED)] + [
            (_prayer_name(k), PCOL[i]) for i, k in enumerate(PKEY)
        ]
        for col, (h, c) in enumerate(hdrs):
            lbl = QLabel(h)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setStyleSheet(
                f"color: {c}; font-size: 11px; font-weight: 700; "
                f"background: transparent; padding: 0 0 4px 0;"
            )
            grid.addWidget(lbl, 0, col)

        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background: {th.BORDER};")
        grid.addWidget(sep, 1, 0, 1, 7)

        lang = get_language()
        for row_idx, d in enumerate(days):
            is_today  = (d == today)
            is_friday = (d.weekday() == 4)

            hy_d, hm_d, hd_d = pc.gregorian_to_hijri(d.year, d.month, d.day)
            is_ayyamul = hd_d in (13, 14, 15)
            is_event   = bool(pc.get_islamic_event(hm_d, hd_d, lang))

            # Date-cell styling mirrors calendar day cells; prayer-time cells stay transparent
            if is_today:
                date_bg = f"background: {th.ACCENT_DK}; border-radius: 4px;"
                dcol    = "#ffffff"
                dfw     = "700"
            elif is_ayyamul:
                date_bg = "background: rgba(245,158,11,0.20); border: 1px solid rgba(245,158,11,0.55); border-radius: 4px;"
                dcol    = "#f59e0b"
                dfw     = "600"
            elif is_event:
                date_bg = "background: rgba(167,139,250,0.18); border: 1px solid rgba(167,139,250,0.55); border-radius: 4px;"
                dcol    = "#a78bfa"
                dfw     = "600"
            else:
                date_bg = "background: transparent;"
                dcol    = "#38bdf8" if is_friday else th.MUTED
                dfw     = "500"

            tfw = "700" if is_today else "500"

            date_txt = f"{_day_name(d.weekday(), short=True)}, {d.day} {_month_name(d.month, short=True)}"
            dlbl = QLabel(date_txt)
            dlbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            dlbl.setStyleSheet(
                f"color: {dcol}; font-size: 11px; font-weight: {dfw}; padding: 4px 6px; {date_bg}"
            )
            grid.addWidget(dlbl, row_idx + 2, 0)

            try:
                times = pc.calculate_times(
                    d, s.latitude, s.longitude, s.timezone,
                    s.method, s.asr_method, s.altitude,
                )
                times["Dhuha"] = self._calc_dhuha(times)
                for col_idx, (key, color) in enumerate(zip(PKEY, PCOL)):
                    lbl = QLabel(_fmt_time(times.get(key, "--:--"), tfmt))
                    lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    lbl.setStyleSheet(
                        f"color: {color}; font-size: 11px; font-weight: {tfw}; "
                        f"padding: 4px 1px; background: transparent;"
                    )
                    grid.addWidget(lbl, row_idx + 2, col_idx + 1)
            except Exception:
                for col_idx in range(6):
                    lbl = QLabel("--")
                    lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    lbl.setStyleSheet(
                        f"color: {th.MUTED}; font-size: 11px; padding: 4px 1px; background: transparent;"
                    )
                    grid.addWidget(lbl, row_idx + 2, col_idx + 1)

        self._schedule_grid_layout.addWidget(grid_widget)
        self._schedule_grid_layout.addStretch()

    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    # ─── hijri calendar ──────────────────────────────────────────────────────

    def _build_hijri_card(self) -> SectionCard:
        card = SectionCard(t("hijri_title"))

        self._hijri_month_lbl = QLabel("—")
        self._hijri_month_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._hijri_month_lbl.setStyleSheet(
            f"color: {th.ACCENT}; font-size: 15px; font-weight: 700; "
            f"background: transparent; margin-bottom: 6px;"
        )
        card.body.addWidget(self._hijri_month_lbl)

        self._hijri_grid_widget = QFrame()
        self._hijri_grid_widget.setStyleSheet("background: transparent;")
        self._hijri_grid = QGridLayout(self._hijri_grid_widget)
        self._hijri_grid.setSpacing(4)
        self._hijri_grid.setContentsMargins(0, 0, 0, 0)
        card.body.addWidget(self._hijri_grid_widget)

        # Legend
        leg = QHBoxLayout()
        leg.setSpacing(10)
        for color, text in [
            (th.ACCENT_DK, "■ Hari ini"),
            ("#f59e0b",    "■ Ayyamul Bidh"),
            ("#38bdf8",    "■ Jum'at"),
            ("#a78bfa",    "■ Hari Istimewa"),
        ]:
            lbl = QLabel(text)
            lbl.setStyleSheet(f"color: {color}; font-size: 10px; background: transparent;")
            leg.addWidget(lbl)
        leg.addStretch()
        card.body.addLayout(leg)

        self._ayyamul_lbl = QLabel("")
        self._ayyamul_lbl.setStyleSheet(
            f"color: {th.TEXT}; font-size: 12px; "
            f"background: transparent; margin-top: 8px;"
        )
        self._ayyamul_lbl.setWordWrap(True)
        card.body.addWidget(self._ayyamul_lbl)

        self._event_lbl = QLabel("")
        self._event_lbl.setStyleSheet(
            f"color: #a78bfa; font-size: 12px; font-weight: 600; "
            f"background: transparent; margin-top: 2px;"
        )
        self._event_lbl.setWordWrap(True)
        card.body.addWidget(self._event_lbl)

        from PyQt6.QtWidgets import QSizePolicy
        card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        return card

    def _refresh_hijri_calendar(self):
        if not hasattr(self, "_hijri_grid"):
            return
        today = date.today()
        hy, hm, hd = pc.gregorian_to_hijri(today.year, today.month, today.day)
        lang = get_language()

        self._hijri_month_lbl.setText(f"{pc.HIJRI_MONTHS_ID[hm - 1]} {hy} H")

        first_greg = today - timedelta(days=hd - 1)
        month_days: list[tuple] = []
        for i in range(30):
            g = first_greg + timedelta(days=i)
            hy2, hm2, hd2 = pc.gregorian_to_hijri(g.year, g.month, g.day)
            if hm2 != hm or hy2 != hy:
                break
            month_days.append((g, hd2))

        # Clear grid
        while self._hijri_grid.count():
            item = self._hijri_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        DAY_HDR = [_day_name(i, short=True) for i in range(7)]
        for col, d in enumerate(DAY_HDR):
            c = "#38bdf8" if col == 4 else th.MUTED
            lbl = QLabel(d)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setStyleSheet(
                f"color: {c}; font-size: 12px; font-weight: 700; background: transparent;"
            )
            self._hijri_grid.addWidget(lbl, 0, col)

        start_col  = first_greg.weekday()
        ayyamul_info: list[str] = []
        today_event: str = ""

        for greg_d, hij_d in month_days:
            delta   = (greg_d - first_greg).days
            cal_pos = delta + start_col
            row     = cal_pos // 7 + 1
            col     = greg_d.weekday()

            is_today   = (greg_d == today)
            is_ayyamul = hij_d in (13, 14, 15)
            is_friday  = (col == 4)
            event_name = pc.get_islamic_event(hm, hij_d, lang)
            is_event   = bool(event_name)

            cell = QFrame()
            cell.setFixedSize(38, 32)

            if is_today:
                cell.setStyleSheet(f"background: {th.ACCENT_DK}; border-radius: 5px;")
                fg, fw = "#ffffff", "700"
            elif is_ayyamul:
                cell.setStyleSheet(
                    "background: rgba(245,158,11,0.20); border-radius: 5px; "
                    "border: 1px solid rgba(245,158,11,0.55);"
                )
                fg, fw = "#f59e0b", "700"
            elif is_event:
                cell.setStyleSheet(
                    "background: rgba(167,139,250,0.18); border-radius: 5px; "
                    "border: 1px solid rgba(167,139,250,0.55);"
                )
                fg, fw = "#a78bfa", "700"
            else:
                cell.setStyleSheet("background: transparent;")
                fg, fw = ("#38bdf8" if is_friday else th.TEXT), "400"

            if event_name:
                cell.setToolTip(event_name)
            if is_ayyamul:
                cell.setToolTip(("Ayyamul Bidh" if not event_name else event_name))

            cl = QVBoxLayout(cell)
            cl.setContentsMargins(0, 0, 0, 0)
            cl.setSpacing(0)
            n = QLabel(str(hij_d))
            n.setAlignment(Qt.AlignmentFlag.AlignCenter)
            n.setStyleSheet(
                f"color: {fg}; font-size: 13px; font-weight: {fw}; background: transparent;"
            )
            cl.addWidget(n)
            self._hijri_grid.addWidget(cell, row, col, Qt.AlignmentFlag.AlignCenter)

            if is_ayyamul:
                ayyamul_info.append(f"{_day_name(greg_d.weekday(), short=True)} {greg_d.day}/{greg_d.month}")
            if is_today and event_name:
                today_event = event_name

        if ayyamul_info:
            self._ayyamul_lbl.setText(
                f"{t('ayyamul_label')}{',  '.join(ayyamul_info)}"
            )
        else:
            self._ayyamul_lbl.setText("")

        if today_event:
            self._event_lbl.setText(f"🌟 {today_event}")
        else:
            self._event_lbl.setText("")
