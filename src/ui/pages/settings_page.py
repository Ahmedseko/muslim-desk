"""Settings page."""
from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QFrame, QPushButton, QComboBox, QSpinBox,
                              QCheckBox, QLineEdit, QFileDialog, QDoubleSpinBox,
                              QScrollArea, QGroupBox, QSlider, QSizePolicy)

from ..widgets import SectionCard
from .. import theme as th
from ...core import prayer_calculator as pc
from ...i18n import t, set_language, get_language, SUPPORTED as I18N_SUPPORTED
from ...i18n import prayer_name as _pname


class SettingsPage(QWidget):
    def __init__(self, main_win):
        super().__init__()
        self._win = main_win
        self._build()
        self.refresh()

    def _build(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # Scrollable area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        outer.addWidget(scroll)

        container = QWidget()
        scroll.setWidget(container)
        root = QVBoxLayout(container)
        root.setContentsMargins(28, 20, 28, 28)
        root.setSpacing(16)

        # Header
        header_row = QHBoxLayout()
        lbl = QLabel(t("settings_title"))
        lbl.setObjectName("H1")
        header_row.addWidget(lbl)
        header_row.addStretch()
        self._btn_save = QPushButton(t("btn_save"))
        self._btn_save.setObjectName("Primary")
        self._btn_save.setFixedHeight(36)
        self._btn_save.clicked.connect(self._save)
        header_row.addWidget(self._btn_save)
        root.addLayout(header_row)

        # ── Appearance
        app_card = SectionCard(t("sec_appearance"))
        self._theme_combo = self._add_combo(app_card, t("lbl_theme"),
                                            ["dark", "light", "system"],
                                            [t("theme_dark"), t("theme_light"), t("theme_system")])
        self._time_fmt_combo = self._add_combo(
            app_card, t("lbl_time_format"),
            ["24h", "12h"],
            [t("fmt_24h"), t("fmt_12h")],
        )
        # Apply time format live when changed (no need to click Save)
        self._time_fmt_combo.currentIndexChanged.connect(self._apply_time_format_live)

        self._lang_combo = self._add_combo(
            app_card, t("lbl_language"),
            ["id", "en"],
            ["Indonesia (ID)", "English (EN)"],
        )
        app_card.body.addLayout(self._make_hint(t("hint_theme_save")))
        root.addWidget(app_card)

        # ── Prayer calculation
        calc_card = SectionCard(t("sec_calc"))
        method_keys = list(pc.METHODS.keys())
        method_names = [f"{k} — {v['name']}" for k, v in pc.METHODS.items()]
        self._method_combo = self._add_combo(calc_card, t("lbl_method"), method_keys, method_names)

        self._asr_combo = self._add_combo(calc_card, t("lbl_asr"),
                                          ["1", "2"],
                                          [t("asr_shafii"), t("asr_hanafi")])
        root.addWidget(calc_card)

        # ── Location
        loc_card = SectionCard(t("sec_location"))

        self._auto_loc_cb = QCheckBox(t("auto_loc_cb"))
        self._auto_loc_cb.setStyleSheet("background: transparent;")
        self._auto_loc_cb.stateChanged.connect(self._on_auto_loc_changed)
        loc_card.body.addWidget(self._auto_loc_cb)

        self._lat_spin = self._add_double_spin(loc_card, t("lbl_lat"), -90, 90, 6)
        self._lon_spin = self._add_double_spin(loc_card, t("lbl_lon"), -180, 180, 6)
        self._tz_spin  = self._add_double_spin(loc_card, t("lbl_tz"), -12, 14, 1)
        self._alt_spin = self._add_double_spin(loc_card, t("lbl_alt"), 0, 9000, 0)

        self._city_edit = self._add_lineedit(loc_card, t("lbl_city"))
        self._country_edit = self._add_lineedit(loc_card, t("lbl_country"))

        # City search button
        city_search_row = QHBoxLayout()
        city_search_row.setSpacing(8)
        lbl_cs = QLabel(t("lbl_search_city"))
        lbl_cs.setStyleSheet(f"color: {th.MUTED}; min-width: 180px; background: transparent;")
        self._btn_city_search = QPushButton(t("btn_search_city"))
        self._btn_city_search.clicked.connect(self._open_city_search)
        city_search_row.addWidget(lbl_cs)
        city_search_row.addWidget(self._btn_city_search, 1)
        loc_card.body.addLayout(city_search_row)

        loc_card.body.addLayout(self._make_hint(t("hint_city")))
        root.addWidget(loc_card)

        # ── Notification
        notif_card = SectionCard(t("sec_notif"))
        self._notif_cb = QCheckBox(t("notif_cb"))
        self._notif_cb.setStyleSheet("background: transparent;")
        notif_card.body.addWidget(self._notif_cb)

        self._sound_cb = QCheckBox(t("sound_cb"))
        self._sound_cb.setStyleSheet("background: transparent;")
        notif_card.body.addWidget(self._sound_cb)

        # Custom sound path
        sound_row = QHBoxLayout()
        sound_row.setSpacing(8)
        lbl_sound = QLabel(t("lbl_sound_file"))
        lbl_sound.setStyleSheet(f"color: {th.MUTED}; min-width: 140px; background: transparent;")
        self._sound_path = QLineEdit()
        self._sound_path.setPlaceholderText(t("sound_placeholder"))
        self._sound_path.setReadOnly(True)
        btn_browse = QPushButton(t("btn_choose_file"))
        btn_browse.clicked.connect(self._browse_sound)
        btn_clear = QPushButton(t("btn_clear"))
        btn_clear.setFixedWidth(70)
        btn_clear.clicked.connect(lambda: self._sound_path.clear())
        sound_row.addWidget(lbl_sound)
        sound_row.addWidget(self._sound_path, 1)
        sound_row.addWidget(btn_browse)
        sound_row.addWidget(btn_clear)
        notif_card.body.addLayout(sound_row)

        self._reminder_combo = self._add_combo(
            notif_card, t("lbl_reminder"),
            ["0", "5", "10", "15"],
            [t("reminder_off"), t("reminder_5"), t("reminder_10"), t("reminder_15")],
        )

        # ── Per-prayer alarm & sound section
        sep2 = QFrame()
        sep2.setFixedHeight(1)
        sep2.setStyleSheet(f"background: {th.BORDER};")
        notif_card.body.addWidget(sep2)

        lbl_per = QLabel(t("alarm_section_lbl"))
        lbl_per.setStyleSheet(
            f"font-size: 12px; font-weight: 700; color: {th.MUTED}; "
            f"letter-spacing: 1px; background: transparent; margin-top: 4px;"
        )
        notif_card.body.addWidget(lbl_per)

        self._prayer_sound_edits: dict[str, QLineEdit] = {}
        self._prayer_alarm_checks: dict[str, QCheckBox] = {}
        for en in ("Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"):
            loc_name = _pname(en)
            row = QHBoxLayout()
            row.setSpacing(6)
            cb = QCheckBox()
            cb.setChecked(True)
            cb.setStyleSheet("background: transparent;")
            lbl_p = QLabel(loc_name)
            lbl_p.setStyleSheet(
                f"color: {th.TEXT}; font-size: 13px; min-width: 72px; background: transparent;"
            )
            edit = QLineEdit()
            edit.setPlaceholderText(t("sound_prayer_placeholder"))
            edit.setReadOnly(True)
            btn_br = QPushButton(t("btn_choose_file"))
            btn_br.clicked.connect(lambda _, e=edit, n=loc_name: self._browse_prayer_sound(e, n))
            btn_cl = QPushButton(t("btn_clear"))
            btn_cl.setFixedWidth(70)
            btn_cl.clicked.connect(lambda _, e=edit: e.clear())
            row.addWidget(cb)
            row.addWidget(lbl_p)
            row.addWidget(edit, 1)
            row.addWidget(btn_br)
            row.addWidget(btn_cl)
            notif_card.body.addLayout(row)
            self._prayer_sound_edits[en] = edit
            self._prayer_alarm_checks[en] = cb

        notif_card.body.addLayout(self._make_hint(t("hint_sound")))
        root.addWidget(notif_card)

        # ── Window behavior
        win_card = SectionCard(t("sec_window"))

        self._startup_cb = QCheckBox(t("startup_cb"))
        self._startup_cb.setStyleSheet("background: transparent;")
        self._startup_cb.stateChanged.connect(self._on_startup_changed)
        win_card.body.addWidget(self._startup_cb)

        self._start_min_cb = QCheckBox(t("start_min_cb"))
        self._start_min_cb.setStyleSheet("background: transparent;")
        win_card.body.addWidget(self._start_min_cb)

        self._tray_cb = QCheckBox(t("tray_cb"))
        self._tray_cb.setStyleSheet("background: transparent;")
        win_card.body.addWidget(self._tray_cb)
        root.addWidget(win_card)

        # ── About
        about_card = SectionCard(t("sec_about"))

        lbl_name = QLabel("Muslim Desk  v1.0.0")
        lbl_name.setStyleSheet(
            f"font-size: 16px; font-weight: 800; color: {th.ACCENT}; background: transparent;"
        )
        about_card.body.addWidget(lbl_name)

        lbl_desc = QLabel(t("about_desc"))
        lbl_desc.setStyleSheet(f"color: {th.MUTED}; font-size: 13px; background: transparent;")
        lbl_desc.setWordWrap(True)
        about_card.body.addWidget(lbl_desc)

        sep_about = QFrame()
        sep_about.setFixedHeight(1)
        sep_about.setStyleSheet(f"background: {th.BORDER}; margin: 8px 0;")
        about_card.body.addWidget(sep_about)

        dev_row = QHBoxLayout()
        dev_row.setSpacing(12)
        lbl_dev_key = QLabel(t("about_dev"))
        lbl_dev_key.setStyleSheet(
            f"color: {th.MUTED}; font-size: 12px; font-weight: 600; "
            f"min-width: 120px; background: transparent;"
        )
        lbl_dev_val = QLabel("Ahmed Seko")
        lbl_dev_val.setStyleSheet(
            f"color: {th.HEADING}; font-size: 13px; font-weight: 700; background: transparent;"
        )
        dev_row.addWidget(lbl_dev_key)
        dev_row.addWidget(lbl_dev_val)
        dev_row.addStretch()
        about_card.body.addLayout(dev_row)

        _info = [
            (t("about_algo"),  "PrayTimes.org"),
            (t("about_hijri"), "Umm al-Qura / Tabular"),
            (t("about_geo"),   "ip-api.com"),
            (t("about_fw"),    "PyQt6 (Python)"),
        ]
        for key, val in _info:
            row = QHBoxLayout()
            row.setSpacing(12)
            k = QLabel(key)
            k.setStyleSheet(
                f"color: {th.MUTED}; font-size: 12px; font-weight: 600; "
                f"min-width: 120px; background: transparent;"
            )
            v = QLabel(val)
            v.setStyleSheet(f"color: {th.TEXT}; font-size: 13px; background: transparent;")
            row.addWidget(k)
            row.addWidget(v)
            row.addStretch()
            about_card.body.addLayout(row)

        root.addWidget(about_card)
        root.addStretch()

        self._status = QLabel("")
        self._status.setStyleSheet(f"font-size: 12px; color: {th.GOOD}; background: transparent;")
        self._status.setAlignment(Qt.AlignmentFlag.AlignRight)
        root.addWidget(self._status)

    def _restart_app(self):
        """Save current settings then relaunch the executable."""
        import sys
        from PyQt6.QtCore import QProcess
        from PyQt6.QtWidgets import QApplication
        QProcess.startDetached(sys.executable, [])
        QApplication.quit()

    def _on_startup_changed(self, state: int):
        from ...data.settings_manager import set_startup_enabled
        enabled = (state == 2)  # Qt.CheckState.Checked
        set_startup_enabled(enabled)

    def _apply_time_format_live(self, index: int):
        """Apply time format immediately when combo changes — no Save needed."""
        fmt_keys = ["24h", "12h"]
        if index < 0 or index >= len(fmt_keys):
            return
        self._win.settings.time_format = fmt_keys[index]
        if hasattr(self._win._dash, "refresh"):
            self._win._dash.refresh()

    # ─── city search ─────────────────────────────────────────────────────────

    def _open_city_search(self):
        from ..widgets import CitySearchDialog
        dlg = CitySearchDialog(self)
        dlg.location_selected.connect(self._apply_city_location)
        dlg.exec()

    def _apply_city_location(self, loc):
        self._lat_spin.setValue(loc.latitude)
        self._lon_spin.setValue(loc.longitude)
        self._tz_spin.setValue(loc.timezone)
        self._city_edit.setText(loc.city)
        self._country_edit.setText(loc.country)
        self._auto_loc_cb.setChecked(False)
        self._on_auto_loc_changed(0)
        # Auto-set calculation method based on country
        method_msg = ""
        if loc.country_code:
            from ...core.location_service import method_for_country
            from ...core import prayer_calculator as pc
            new_method = method_for_country(loc.country_code)
            _method_keys = list(pc.METHODS.keys())
            if new_method in _method_keys:
                self._method_combo.setCurrentIndex(_method_keys.index(new_method))
            method_msg = f"  ·  {t('method_auto_set', new_method)}"
        self._status.setText(f"{t('loc_set_to')}{loc.city}, {loc.country}{method_msg}")

    # ─── helpers ─────────────────────────────────────────────────────────────

    def _add_combo(self, card: SectionCard, label: str,
                   keys: list[str], names: list[str]) -> QComboBox:
        row = QHBoxLayout()
        lbl = QLabel(label)
        lbl.setStyleSheet(f"color: {th.MUTED}; min-width: 180px; background: transparent;")
        combo = QComboBox()
        for name in names:
            combo.addItem(name)
        row.addWidget(lbl)
        row.addWidget(combo, 1)
        card.body.addLayout(row)
        combo._keys = keys
        return combo

    def _add_double_spin(self, card: SectionCard, label: str,
                         min_val: float, max_val: float, decimals: int) -> QDoubleSpinBox:
        row = QHBoxLayout()
        lbl = QLabel(label)
        lbl.setStyleSheet(f"color: {th.MUTED}; min-width: 180px; background: transparent;")
        spin = QDoubleSpinBox()
        spin.setRange(min_val, max_val)
        spin.setDecimals(decimals)
        spin.setSingleStep(0.1 if decimals > 0 else 1.0)
        row.addWidget(lbl)
        row.addWidget(spin, 1)
        card.body.addLayout(row)
        return spin

    def _add_lineedit(self, card: SectionCard, label: str) -> QLineEdit:
        row = QHBoxLayout()
        lbl = QLabel(label)
        lbl.setStyleSheet(f"color: {th.MUTED}; min-width: 180px; background: transparent;")
        edit = QLineEdit()
        row.addWidget(lbl)
        row.addWidget(edit, 1)
        card.body.addLayout(row)
        return edit

    def _make_hint(self, text: str) -> QHBoxLayout:
        row = QHBoxLayout()
        lbl = QLabel(f"ℹ️  {text}")
        lbl.setStyleSheet(f"color: {th.MUTED}; font-size: 12px; background: transparent;")
        lbl.setWordWrap(True)
        row.addWidget(lbl)
        return row

    def _on_auto_loc_changed(self, state):
        manual = (state == 0)
        for w in (self._lat_spin, self._lon_spin, self._tz_spin,
                  self._alt_spin, self._city_edit, self._country_edit):
            w.setEnabled(manual)

    def _browse_sound(self):
        path, _ = QFileDialog.getOpenFileName(
            self, t("lbl_sound_file"), "",
            "Audio WAV (*.wav);;All Files (*.*)"
        )
        if path:
            self._sound_path.setText(path)

    def _browse_prayer_sound(self, edit: QLineEdit, prayer_name: str):
        path, _ = QFileDialog.getOpenFileName(
            self, f"{t('lbl_sound_file')} — {prayer_name}", "",
            "Audio WAV (*.wav);;All Files (*.*)"
        )
        if path:
            edit.setText(path)

    # ─── load / save ─────────────────────────────────────────────────────────

    def refresh(self):
        s = self._win.settings

        # Theme
        theme_keys = ["dark", "light", "system"]
        idx = theme_keys.index(s.theme) if s.theme in theme_keys else 0
        self._theme_combo.setCurrentIndex(idx)

        # Time format
        fmt_keys = ["24h", "12h"]
        self._time_fmt_combo.setCurrentIndex(fmt_keys.index(s.time_format) if s.time_format in fmt_keys else 0)

        # Language
        lang_keys = list(I18N_SUPPORTED)
        _li = lang_keys.index(s.language) if s.language in lang_keys else 0
        self._lang_combo.setCurrentIndex(_li)

        # Method
        method_keys = list(pc.METHODS.keys())
        midx = method_keys.index(s.method) if s.method in method_keys else 0
        self._method_combo.setCurrentIndex(midx)

        # Asr
        self._asr_combo.setCurrentIndex(max(0, s.asr_method - 1))

        # Location
        self._auto_loc_cb.setChecked(s.auto_location)
        self._lat_spin.setValue(s.latitude)
        self._lon_spin.setValue(s.longitude)
        self._tz_spin.setValue(s.timezone)
        self._alt_spin.setValue(s.altitude)
        self._city_edit.setText(s.city)
        self._country_edit.setText(s.country)
        self._on_auto_loc_changed(2 if s.auto_location else 0)

        # Notification
        self._notif_cb.setChecked(s.notification_enabled)
        self._sound_cb.setChecked(s.sound_enabled)
        self._sound_path.setText(s.custom_sound_path)

        reminder_keys = ["0", "5", "10", "15"]
        ridx = reminder_keys.index(str(s.reminder_minutes)) if str(s.reminder_minutes) in reminder_keys else 1
        self._reminder_combo.setCurrentIndex(ridx)

        for en, edit in self._prayer_sound_edits.items():
            edit.setText(s.prayer_sounds.get(en, ""))

        for en, cb in self._prayer_alarm_checks.items():
            cb.setChecked(s.prayer_alarms.get(en, True))

        # Window
        from ...data.settings_manager import is_startup_enabled
        self._startup_cb.blockSignals(True)
        self._startup_cb.setChecked(is_startup_enabled())
        self._startup_cb.blockSignals(False)
        self._start_min_cb.setChecked(s.start_minimized)
        self._tray_cb.setChecked(s.minimize_to_tray)

        self._status.setText("")

    def _save(self):
        s = self._win.settings
        old_theme = s.theme
        old_lang  = s.language

        # Theme (hardcoded keys)
        _theme_keys = ["dark", "light", "system"]
        _ti = self._theme_combo.currentIndex()
        s.theme = _theme_keys[_ti] if 0 <= _ti < len(_theme_keys) else "dark"

        # Time format (hardcoded keys)
        _fmt_keys = ["24h", "12h"]
        _fi = self._time_fmt_combo.currentIndex()
        s.time_format = _fmt_keys[_fi] if 0 <= _fi < len(_fmt_keys) else "24h"

        # Language
        _lang_keys = list(I18N_SUPPORTED)
        _li = self._lang_combo.currentIndex()
        s.language = _lang_keys[_li] if 0 <= _li < len(_lang_keys) else "id"

        # Method (hardcoded keys)
        _method_keys = list(pc.METHODS.keys())
        _mi = self._method_combo.currentIndex()
        s.method = _method_keys[_mi] if 0 <= _mi < len(_method_keys) else "Kemenag"
        s.asr_method = self._asr_combo.currentIndex() + 1

        # Location
        s.auto_location = self._auto_loc_cb.isChecked()
        s.latitude      = self._lat_spin.value()
        s.longitude     = self._lon_spin.value()
        s.timezone      = self._tz_spin.value()
        s.altitude      = self._alt_spin.value()
        s.city          = self._city_edit.text().strip()
        s.country       = self._country_edit.text().strip()

        # Notification
        s.notification_enabled = self._notif_cb.isChecked()
        s.sound_enabled        = self._sound_cb.isChecked()
        s.custom_sound_path    = self._sound_path.text().strip()

        _reminder_keys = ["0", "5", "10", "15"]
        _ri = self._reminder_combo.currentIndex()
        s.reminder_minutes = int(_reminder_keys[_ri] if 0 <= _ri < len(_reminder_keys) else "5")

        for en, edit in self._prayer_sound_edits.items():
            s.prayer_sounds[en] = edit.text().strip()

        for en, cb in self._prayer_alarm_checks.items():
            s.prayer_alarms[en] = cb.isChecked()

        # Window
        s.start_minimized  = self._start_min_cb.isChecked()
        s.minimize_to_tray = self._tray_cb.isChecked()

        self._win.on_settings_changed()

        # Always sync language module (may have changed)
        set_language(s.language)

        if s.theme != old_theme:
            self._win.apply_theme_live(s.theme)
        elif s.language != old_lang:
            # Language changed → restart app so all labels rebuild cleanly
            self._restart_app()
            return
        else:
            if hasattr(self._win, "_dash") and hasattr(self._win._dash, "refresh"):
                self._win._dash.refresh()

        self._status.setText(t("saved_ok"))
