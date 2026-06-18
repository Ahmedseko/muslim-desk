"""Dashboard page: prayer times, countdown, Hijri date, location."""
from __future__ import annotations

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
from ...i18n import t, day_name as _day_name, month_name as _month_name, prayer_name as _prayer_name


_PRAYER_ORDER = ["Fajr", "Sunrise", "Dhuhr", "Asr", "Maghrib", "Isha"]
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
        self._today_times_date: date | None = None   # which date _today_times covers
        self._next_prayer: str = ""
        self._build()

        self._location_detected.connect(self._on_location_detected)

        # Refresh prayer times + countdown every second
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

        # Title + dates
        title_col = QVBoxLayout()
        title_col.setSpacing(2)
        lbl_title = QLabel("Dashboard")
        lbl_title.setObjectName("H1")
        title_col.addWidget(lbl_title)

        self._date_header = DateHeader()
        title_col.addWidget(self._date_header)
        header_row.addLayout(title_col)

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

        # ── Timezone mismatch warning bar (hidden by default)
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

        # Digital clock
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

        # Next prayer banner
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

        # ── Syuruk row (Sunrise)
        syuruk_card = QFrame()
        syuruk_card.setObjectName("Card")
        syuruk_layout = QHBoxLayout(syuruk_card)
        syuruk_layout.setContentsMargins(20, 12, 20, 12)
        syuruk_layout.setSpacing(12)

        sun_icon = QLabel("🌅")
        sun_icon.setStyleSheet("font-size: 18px; background: transparent;")
        lbl_syuruk = QLabel(t("sunrise_row"))
        lbl_syuruk.setStyleSheet(f"font-size: 13px; color: {th.MUTED}; background: transparent;")
        self._syuruk_time = QLabel("--:--")
        self._syuruk_time.setStyleSheet(f"font-size: 16px; font-weight: 700; "
                                         f"color: {th.PRAYER_COLORS['Sunrise']}; background: transparent;")

        syuruk_layout.addWidget(sun_icon)
        syuruk_layout.addWidget(lbl_syuruk)
        syuruk_layout.addStretch()
        syuruk_layout.addWidget(self._syuruk_time)

        # Alarm toggle for Sunrise
        self._syuruk_alarm_btn = QPushButton(t("alarm_inactive"))
        self._syuruk_alarm_btn.setObjectName("AlarmOff")
        self._syuruk_alarm_btn.setFixedHeight(26)
        self._syuruk_alarm_btn.clicked.connect(self._toggle_syuruk)
        syuruk_layout.addWidget(self._syuruk_alarm_btn)

        root.addWidget(syuruk_card)

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

    # ─── refresh ─────────────────────────────────────────────────────────────

    def refresh(self):
        s = self._win.settings
        today = app_now(s.timezone).date()   # use app timezone, not system date

        # Gregorian
        greg = (f"{_day_name(today.weekday())}, "
                f"{today.day} {_month_name(today.month)} {today.year}")
        # Hijri
        hy, hm, hd = pc.gregorian_to_hijri(today.year, today.month, today.day)
        hijri = pc.format_hijri(hy, hm, hd)
        self._date_header.update_dates(greg, hijri)

        # Location label
        self._loc_label.setText(f"📍 {s.city}, {s.country}")

        # Calculate times
        try:
            self._today_times = pc.calculate_times(
                today, s.latitude, s.longitude, s.timezone,
                s.method, s.asr_method, s.altitude,
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

        self._syuruk_time.setText(_fmt_time(self._today_times.get("Sunrise", "--:--"), tfmt))
        syuruk_on = s.prayer_alarms.get("Sunrise", False)
        self._syuruk_alarm_btn.setObjectName("AlarmOn" if syuruk_on else "AlarmOff")
        self._syuruk_alarm_btn.setText(t("alarm_active") if syuruk_on else t("alarm_inactive"))
        self._syuruk_alarm_btn.style().unpolish(self._syuruk_alarm_btn)
        self._syuruk_alarm_btn.style().polish(self._syuruk_alarm_btn)

        self._refresh_weekly_schedule()
        self._refresh_hijri_calendar()
        self._check_timezone_mismatch()
        self._tick()

    # ─── countdown tick ──────────────────────────────────────────────────────

    def _tick(self):
        now   = app_now(self._win.settings.timezone)
        today = now.date()

        # Auto-refresh prayer times when the date changes (midnight crossover)
        if self._today_times_date != today:
            self.refresh()
            return

        if not self._today_times:
            return

        # Build prayer datetimes for today
        order = _PRAYER_ORDER
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

        # Previous prayer (today) — for progress bar start point
        prev_name: str | None = None
        prev_dt:   datetime | None = None
        for name in reversed(order):
            dt = dts.get(name)
            if dt and dt <= now:
                prev_name = name
                prev_dt   = dt
                break

        # If all today's prayers passed → fall back to tomorrow's Fajr
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
                # prev = today's Isha
                if prev_dt is None and dts.get("Isha"):
                    prev_dt = dts["Isha"]
            except Exception:
                pass

        # Before Fajr (midnight → dawn): prev_dt is None because no prayer has
        # passed today yet. Use yesterday's Isha so the progress bar animates.
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

        # Banner + progress bar
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

            # Progress bar: fraction between [prev_dt, next_dt]
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
        """Ubah timezone app agar sesuai dengan clock sistem."""
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
        # Auto-set calculation method based on detected country
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

    def _toggle_syuruk(self):
        s = self._win.settings
        current = s.prayer_alarms.get("Sunrise", False)
        new_val = not current
        s.prayer_alarms["Sunrise"] = new_val
        self._syuruk_alarm_btn.setObjectName("AlarmOn" if new_val else "AlarmOff")
        self._syuruk_alarm_btn.setText(t("alarm_active") if new_val else t("alarm_inactive"))
        self._syuruk_alarm_btn.style().unpolish(self._syuruk_alarm_btn)
        self._syuruk_alarm_btn.style().polish(self._syuruk_alarm_btn)
        from ...data.settings_manager import save as save_s
        save_s(s)

    # ─── weekly schedule ─────────────────────────────────────────────────────

    def _build_weekly_card(self) -> SectionCard:
        card = SectionCard(t("weekly_title"))

        # Centered date-range subtitle (updated on refresh)
        self._weekly_range_lbl = QLabel("—")
        self._weekly_range_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._weekly_range_lbl.setStyleSheet(
            f"color: {th.ACCENT}; font-size: 13px; font-weight: 700; "
            f"background: transparent; margin-bottom: 8px;"
        )
        card.body.addWidget(self._weekly_range_lbl)

        # Table grid
        grid = QGridLayout()
        grid.setVerticalSpacing(0)
        grid.setHorizontalSpacing(4)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setColumnStretch(0, 42)
        for c in range(1, 6):
            grid.setColumnStretch(c, 12)

        _HDRS = [
            (t("weekly_col_date"),   th.MUTED),
            (_prayer_name("Fajr"),   th.PRAYER_COLORS["Fajr"]),
            (_prayer_name("Dhuhr"),  th.PRAYER_COLORS["Dhuhr"]),
            (_prayer_name("Asr"),    th.PRAYER_COLORS["Asr"]),
            (_prayer_name("Maghrib"),th.PRAYER_COLORS["Maghrib"]),
            (_prayer_name("Isha"),   th.PRAYER_COLORS["Isha"]),
        ]
        for col, (h, c) in enumerate(_HDRS):
            lbl = QLabel(h)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setStyleSheet(
                f"color: {c}; font-size: 11px; font-weight: 700; "
                f"background: transparent; padding: 0 0 6px 0;"
            )
            grid.addWidget(lbl, 0, col)

        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background: {th.BORDER};")
        grid.addWidget(sep, 1, 0, 1, 6)

        self._weekly_labels: list[dict] = []
        _KEYS = ["date", "Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"]
        for row in range(7):
            row_dict: dict = {}
            for col, key in enumerate(_KEYS):
                lbl = QLabel("--")
                lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
                lbl.setStyleSheet(
                    f"color: {th.TEXT}; font-size: 12px; "
                    f"background: transparent; padding: 5px 2px;"
                )
                grid.addWidget(lbl, row + 2, col)
                row_dict[key] = lbl
            self._weekly_labels.append(row_dict)

        card.body.addLayout(grid)
        card.body.addStretch()
        card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        return card

    def _refresh_weekly_schedule(self):
        if not hasattr(self, "_weekly_labels"):
            return
        s = self._win.settings
        today = date.today()
        end   = today + timedelta(days=6)
        self._weekly_range_lbl.setText(
            f"{today.day} {_month_name(today.month, short=True)} — "
            f"{end.day} {_month_name(end.month, short=True)} {end.year}"
        )
        PCOL  = [
            th.PRAYER_COLORS["Fajr"],
            th.PRAYER_COLORS["Dhuhr"],
            th.PRAYER_COLORS["Asr"],
            th.PRAYER_COLORS["Maghrib"],
            th.PRAYER_COLORS["Isha"],
        ]
        PKEY  = ["Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"]

        for i in range(7):
            d        = today + timedelta(days=i)
            row_dict = self._weekly_labels[i]
            is_today  = (i == 0)
            is_friday = (d.weekday() == 4)

            bg    = f"background: {th.SURFACE_2}; border-radius: 4px;" if is_today else "background: transparent;"
            dcol  = th.ACCENT if is_today else ("#38bdf8" if is_friday else th.MUTED)
            fw    = "700" if is_today else "500"
            fsize = "12px"

            row_dict["date"].setText(
                f"{_day_name(d.weekday())}, {d.day} {_month_name(d.month)} {d.year}"
            )
            row_dict["date"].setStyleSheet(
                f"color: {dcol}; font-size: {fsize}; font-weight: {fw}; padding: 4px 6px; {bg}"
            )
            try:
                times = pc.calculate_times(
                    d, s.latitude, s.longitude, s.timezone,
                    s.method, s.asr_method, s.altitude,
                )
                tfmt = s.time_format
                for key, color in zip(PKEY, PCOL):
                    row_dict[key].setText(_fmt_time(times.get(key, "--:--"), tfmt))
                    row_dict[key].setStyleSheet(
                        f"color: {color}; font-size: {fsize}; font-weight: {fw}; padding: 4px 2px; {bg}"
                    )
            except Exception:
                for key in PKEY:
                    row_dict[key].setText("--")

    # ─── hijri calendar ──────────────────────────────────────────────────────

    def _build_hijri_card(self) -> SectionCard:
        card = SectionCard(t("hijri_title"))

        self._hijri_month_lbl = QLabel("—")
        self._hijri_month_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._hijri_month_lbl.setStyleSheet(
            f"color: {th.ACCENT}; font-size: 13px; font-weight: 700; "
            f"background: transparent; margin-bottom: 4px;"
        )
        card.body.addWidget(self._hijri_month_lbl)

        self._hijri_grid_widget = QFrame()
        self._hijri_grid_widget.setStyleSheet("background: transparent;")
        self._hijri_grid = QGridLayout(self._hijri_grid_widget)
        self._hijri_grid.setSpacing(2)
        self._hijri_grid.setContentsMargins(0, 0, 0, 0)
        card.body.addWidget(self._hijri_grid_widget)

        leg = QHBoxLayout()
        leg.setSpacing(10)
        for color, text in [
            (th.ACCENT_DK, "■ Hari ini"),
            ("#f59e0b",    "■ Ayyamul Bidh"),
            ("#38bdf8",    "■ Jum'at"),
        ]:
            l = QLabel(text)
            l.setStyleSheet(f"color: {color}; font-size: 10px; background: transparent;")
            leg.addWidget(l)
        leg.addStretch()
        card.body.addLayout(leg)

        self._ayyamul_lbl = QLabel("")
        self._ayyamul_lbl.setStyleSheet(
            f"color: {th.TEXT}; font-size: 11px; "
            f"background: transparent; margin-top: 6px;"
        )
        self._ayyamul_lbl.setWordWrap(True)
        card.body.addWidget(self._ayyamul_lbl)

        card.body.addStretch()

        from PyQt6.QtWidgets import QSizePolicy
        card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        return card

    def _refresh_hijri_calendar(self):
        if not hasattr(self, "_hijri_grid"):
            return
        today = date.today()
        hy, hm, hd = pc.gregorian_to_hijri(today.year, today.month, today.day)

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
                f"color: {c}; font-size: 10px; font-weight: 700; background: transparent;"
            )
            self._hijri_grid.addWidget(lbl, 0, col)

        start_col  = first_greg.weekday()
        ayyamul_info: list[str] = []

        for greg_d, hij_d in month_days:
            delta   = (greg_d - first_greg).days
            cal_pos = delta + start_col
            row     = cal_pos // 7 + 1
            col     = greg_d.weekday()

            is_today   = (greg_d == today)
            is_ayyamul = hij_d in (13, 14, 15)
            is_friday  = (col == 4)

            cell = QFrame()
            cell.setFixedSize(30, 26)

            if is_today:
                cell.setStyleSheet(f"background: {th.ACCENT_DK}; border-radius: 5px;")
                fg, fw = "#ffffff", "700"
            elif is_ayyamul:
                cell.setStyleSheet(
                    "background: rgba(245,158,11,0.20); border-radius: 5px; "
                    "border: 1px solid rgba(245,158,11,0.55);"
                )
                fg, fw = "#f59e0b", "700"
            else:
                cell.setStyleSheet("background: transparent;")
                fg, fw = ("#38bdf8" if is_friday else th.TEXT), "400"

            cl = QVBoxLayout(cell)
            cl.setContentsMargins(0, 0, 0, 0)
            cl.setSpacing(0)
            n = QLabel(str(hij_d))
            n.setAlignment(Qt.AlignmentFlag.AlignCenter)
            n.setStyleSheet(
                f"color: {fg}; font-size: 11px; font-weight: {fw}; background: transparent;"
            )
            cl.addWidget(n)
            self._hijri_grid.addWidget(cell, row, col, Qt.AlignmentFlag.AlignCenter)

            if is_ayyamul:
                ayyamul_info.append(f"{_day_name(greg_d.weekday(), short=True)} {greg_d.day}/{greg_d.month}")

        if ayyamul_info:
            self._ayyamul_lbl.setText(
                f"{t('ayyamul_label')}{',  '.join(ayyamul_info)}"
            )
        else:
            self._ayyamul_lbl.setText("")
