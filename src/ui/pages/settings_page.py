"""Settings page."""
from __future__ import annotations

import sys
from pathlib import Path

from PyQt6.QtCore import Qt, QUrl, pyqtSignal
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QFrame, QPushButton, QComboBox,
                              QCheckBox, QLineEdit, QFileDialog,
                              QScrollArea, QSizePolicy, QInputDialog,
                              QMessageBox, QListWidget, QListWidgetItem)

from ..widgets import SectionCard
from .. import theme as th


class _ModernSpin(QFrame):
    """Modern −/+ number input — replaces QSpinBox/QDoubleSpinBox."""

    valueChanged = pyqtSignal(float)

    def __init__(self, min_val: float, max_val: float,
                 step: float = 1.0, decimals: int = 0,
                 special_zero: str = "", parent=None):
        super().__init__(parent)
        self._min = float(min_val)
        self._max = float(max_val)
        self._step = float(step)
        self._decimals = decimals
        self._special_zero = special_zero
        self._val = 0.0
        self._build()

    def _build(self):
        self.setFixedHeight(38)
        self.setStyleSheet(
            f"QFrame {{ background: {th.SURFACE_2}; "
            f"border: 1px solid {th.BORDER}; border-radius: 8px; }}"
        )
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        btn_style = (
            f"QPushButton {{ background: transparent; border: none; "
            f"color: {th.MUTED}; font-size: 17px; font-weight: 600; "
            f"min-width: 34px; border-radius: 8px; }}"
            f"QPushButton:hover {{ background: {th.BTN_HOVER}; color: {th.ACCENT}; }}"
            f"QPushButton:pressed {{ background: {th.BTN_PRESSED}; }}"
            f"QPushButton:disabled {{ color: {th.BORDER}; }}"
        )

        self._btn_minus = QPushButton("−")
        self._btn_minus.setFixedWidth(34)
        self._btn_minus.setStyleSheet(btn_style)
        self._btn_minus.clicked.connect(self._decrement)
        lay.addWidget(self._btn_minus)

        sep_l = QFrame()
        sep_l.setFixedWidth(1)
        sep_l.setStyleSheet(f"background: {th.BORDER};")
        lay.addWidget(sep_l)

        self._edit = QLineEdit()
        self._edit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._edit.setStyleSheet(
            "QLineEdit { background: transparent; border: none; padding: 0 4px; }"
            "QLineEdit:disabled { color: #555; }"
        )
        self._edit.editingFinished.connect(self._on_edited)
        lay.addWidget(self._edit, 1)

        sep_r = QFrame()
        sep_r.setFixedWidth(1)
        sep_r.setStyleSheet(f"background: {th.BORDER};")
        lay.addWidget(sep_r)

        self._btn_plus = QPushButton("+")
        self._btn_plus.setFixedWidth(34)
        self._btn_plus.setStyleSheet(btn_style)
        self._btn_plus.clicked.connect(self._increment)
        lay.addWidget(self._btn_plus)

        self._refresh_text()

    def _refresh_text(self):
        if self._special_zero and self._val == 0.0:
            self._edit.setText(self._special_zero)
        elif self._decimals == 0:
            self._edit.setText(str(int(round(self._val))))
        else:
            self._edit.setText(f"{self._val:.{self._decimals}f}")

    def _clamp(self, v: float) -> float:
        return max(self._min, min(self._max, round(v, max(self._decimals, 6))))

    def _increment(self):
        self._val = self._clamp(self._val + self._step)
        self._refresh_text()
        self.valueChanged.emit(self._val)

    def _decrement(self):
        self._val = self._clamp(self._val - self._step)
        self._refresh_text()
        self.valueChanged.emit(self._val)

    def _on_edited(self):
        txt = self._edit.text().strip().replace(",", ".")
        if self._special_zero and txt.lower() in (self._special_zero.lower(), "0", ""):
            self._val = 0.0
        else:
            try:
                self._val = self._clamp(float(txt))
            except ValueError:
                pass
        self._refresh_text()
        self.valueChanged.emit(self._val)

    def value(self) -> float:
        return self._val

    def setValue(self, v: float):
        self._val = self._clamp(float(v))
        self._refresh_text()

    def setEnabled(self, enabled: bool):
        super().setEnabled(enabled)
        for w in (self._btn_minus, self._btn_plus, self._edit):
            w.setEnabled(enabled)
        alpha = "1px solid " + th.BORDER if enabled else "1px solid " + th.SURFACE_2
        self.setStyleSheet(
            f"QFrame {{ background: {th.SURFACE_2 if enabled else th.SURFACE}; "
            f"border: {alpha}; border-radius: 8px; }}"
        )
from ...core import prayer_calculator as pc
from ...i18n import t, set_language, get_language, SUPPORTED as I18N_SUPPORTED
from ...i18n import prayer_name as _pname
from ... import VERSION


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

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        outer.addWidget(scroll)

        container = QWidget()
        scroll.setWidget(container)
        root = QVBoxLayout(container)
        root.setContentsMargins(28, 16, 28, 8)
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
        self._font_size_combo = self._add_combo(
            app_card, t("lbl_font_size"),
            ["12", "13", "15", "17"],
            [t("font_size_small"), t("font_size_med"), t("font_size_large"), t("font_size_xl")],
        )
        self._font_size_combo.currentIndexChanged.connect(self._apply_font_size_live)

        self._time_fmt_combo = self._add_combo(
            app_card, t("lbl_time_format"),
            ["24h", "12h"],
            [t("fmt_24h"), t("fmt_12h")],
        )
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

        # Imsak setting
        imsak_row = QHBoxLayout()
        lbl_imsak = QLabel(t("lbl_imsak_min"))
        lbl_imsak.setStyleSheet(f"color: {th.MUTED}; min-width: 180px; background: transparent;")
        self._imsak_spin = _ModernSpin(0, 30, step=1, decimals=0, special_zero=t("imsak_off"))
        imsak_row.addWidget(lbl_imsak)
        imsak_row.addWidget(self._imsak_spin, 1)
        calc_card.body.addLayout(imsak_row)
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

        # ── Location Profiles
        prof_card = SectionCard(t("sec_profiles"))

        # Profiles list
        self._profile_list = QListWidget()
        self._profile_list.setMaximumHeight(120)
        self._profile_list.setStyleSheet(
            f"QListWidget {{ background: {th.SURFACE_2}; border: 1px solid {th.BORDER}; "
            f"border-radius: 8px; }}"
            f"QListWidget::item {{ padding: 6px 10px; }}"
            f"QListWidget::item:selected {{ background: {th.ACCENT_DK}; color: #fff; }}"
        )
        prof_card.body.addWidget(self._profile_list)

        prof_btns = QHBoxLayout()
        prof_btns.setSpacing(6)
        self._btn_save_profile = QPushButton(t("profile_save_btn"))
        self._btn_save_profile.clicked.connect(self._save_profile)
        self._btn_use_profile = QPushButton(t("profile_use"))
        self._btn_use_profile.clicked.connect(self._use_profile)
        self._btn_del_profile = QPushButton(t("profile_delete"))
        self._btn_del_profile.setObjectName("Danger")
        self._btn_del_profile.clicked.connect(self._delete_profile)
        prof_btns.addWidget(self._btn_save_profile, 2)
        prof_btns.addWidget(self._btn_use_profile, 1)
        prof_btns.addWidget(self._btn_del_profile, 1)
        prof_card.body.addLayout(prof_btns)

        self._profile_status = QLabel("")
        self._profile_status.setStyleSheet(f"color: {th.GOOD}; font-size: 12px; background: transparent;")
        prof_card.body.addWidget(self._profile_status)
        root.addWidget(prof_card)

        # ── Notification
        notif_card = SectionCard(t("sec_notif"))
        self._notif_cb = QCheckBox(t("notif_cb"))
        self._notif_cb.setStyleSheet("background: transparent;")
        notif_card.body.addWidget(self._notif_cb)

        self._sound_cb = QCheckBox(t("sound_cb"))
        self._sound_cb.setStyleSheet("background: transparent;")
        notif_card.body.addWidget(self._sound_cb)

        self._toast_cb = QCheckBox(t("lbl_toast"))
        self._toast_cb.setStyleSheet("background: transparent;")
        notif_card.body.addWidget(self._toast_cb)

        # Custom sound path (supports MP3 and WAV now)
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

        # Per-prayer alarm & sound
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
        for en in ("Fajr", "Dhuhr", "Asr", "Maghrib", "Isha", "Sunrise"):
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

        # Preview button
        btn_preview = QPushButton(t("btn_preview_notif"))
        btn_preview.setFixedHeight(36)
        btn_preview.setStyleSheet(
            f"QPushButton {{ background: {th.SURFACE_2}; border: 1px solid {th.ACCENT_DK}; "
            f"border-radius: 8px; color: {th.ACCENT}; font-weight: 600; font-size: 13px; }}"
            f"QPushButton:hover {{ background: {th.BTN_HOVER}; }}"
        )
        btn_preview.clicked.connect(self._preview_notification)
        notif_card.body.addWidget(btn_preview)

        root.addWidget(notif_card)

        # ── Window behavior
        win_card = SectionCard(t("sec_window"))

        if sys.platform == "win32":
            self._startup_cb = QCheckBox(t("startup_cb"))
            self._startup_cb.setStyleSheet("background: transparent;")
            self._startup_cb.stateChanged.connect(self._on_startup_changed)
            win_card.body.addWidget(self._startup_cb)
        else:
            self._startup_cb = None

        self._start_min_cb = QCheckBox(t("start_min_cb"))
        self._start_min_cb.setStyleSheet("background: transparent;")
        win_card.body.addWidget(self._start_min_cb)

        self._tray_cb = QCheckBox(t("tray_cb"))
        self._tray_cb.setStyleSheet("background: transparent;")
        win_card.body.addWidget(self._tray_cb)
        root.addWidget(win_card)

        # ── About
        about_card = SectionCard(t("sec_about"))

        ver_row = QHBoxLayout()
        lbl_name = QLabel(f"Muslim Desk  v{VERSION}")
        lbl_name.setStyleSheet(
            f"font-size: 16px; font-weight: 800; color: {th.ACCENT}; background: transparent;"
        )
        ver_row.addWidget(lbl_name)

        # Update available badge (hidden by default)
        self._update_frame = QFrame()
        self._update_frame.setStyleSheet(
            f"QFrame {{ background: rgba(16,185,129,0.12); border: 1px solid rgba(16,185,129,0.45); "
            f"border-radius: 8px; padding: 2px 0; }}"
        )
        update_inner = QHBoxLayout(self._update_frame)
        update_inner.setContentsMargins(10, 6, 10, 6)
        update_inner.setSpacing(10)
        self._update_avail_lbl = QLabel("")
        self._update_avail_lbl.setStyleSheet(
            f"color: #10b981; font-size: 12px; font-weight: 600; background: transparent; border: none;"
        )
        update_inner.addWidget(self._update_avail_lbl)
        self._btn_update_dl = QPushButton(t("update_download"))
        self._btn_update_dl.setObjectName("Primary")
        self._btn_update_dl.setFixedHeight(26)
        self._btn_update_dl.clicked.connect(self._open_update_url)
        update_inner.addWidget(self._btn_update_dl)
        self._update_frame.setVisible(False)
        self._update_url = ""

        ver_row.addStretch()
        ver_row.addWidget(self._update_frame)
        about_card.body.addLayout(ver_row)

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
            f"min-width: 160px; background: transparent;"
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
            (t("about_algo"),        "PrayTimes.org",         ""),
            (t("about_hijri"),       "Umm al-Qura / Tabular", ""),
            (t("about_geo"),         "ip-api.com",            ""),
            (t("about_fw"),          "PyQt6 (Python)",        ""),
            (t("about_quran_data"),  "alquran.cloud API",     ""),
            (t("about_audio_fajr"),  "Adzan Subuh - Mishary Rashid",
             "https://www.youtube.com/watch?v=qhp3gy2rDUU"),
            (t("about_audio_other"), "Adzan - Umar Al Faruq",
             "https://www.youtube.com/watch?v=18r6pTlgFKs"),
            (t("about_audio_edit"),  "Audacity",              ""),
        ]
        _key_style = (
            f"color: {th.MUTED}; font-size: 12px; font-weight: 600; "
            f"min-width: 160px; background: transparent;"
        )
        for key, val, url in _info:
            row = QHBoxLayout()
            row.setSpacing(12)
            k = QLabel(key)
            k.setStyleSheet(_key_style)
            if url:
                v = QLabel(f'<a href="{url}" style="color:{th.ACCENT};">{val}</a>')
                v.setOpenExternalLinks(True)
            else:
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
        self._status.setVisible(False)
        root.addWidget(self._status)

    def show_update_available(self, version: str, url: str):
        self._update_url = url
        self._update_avail_lbl.setText(t("update_available", version))
        self._update_frame.setVisible(True)

    def _open_update_url(self):
        if self._update_url:
            QDesktopServices.openUrl(QUrl(self._update_url))

    def _restart_app(self):
        import sys
        from PyQt6.QtCore import QProcess
        from PyQt6.QtWidgets import QApplication
        QProcess.startDetached(sys.executable, [])
        QApplication.quit()

    def _on_startup_changed(self, state: int):
        if sys.platform == "win32":
            from ...data.settings_manager import set_startup_enabled
            enabled = (state == 2)
            set_startup_enabled(enabled)

    def _apply_time_format_live(self, index: int):
        fmt_keys = ["24h", "12h"]
        if index < 0 or index >= len(fmt_keys):
            return
        self._win.settings.time_format = fmt_keys[index]
        if hasattr(self._win._dash, "refresh"):
            self._win._dash.refresh()

    def _apply_font_size_live(self, index: int):
        sizes = [12, 13, 15, 17]
        if index < 0 or index >= len(sizes):
            return
        size = sizes[index]
        self._win.settings.font_size = size
        th.apply_font_size(size)
        from PyQt6.QtWidgets import QApplication
        QApplication.instance().setStyleSheet(th.STYLESHEET)

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
        method_msg = ""
        if loc.country_code:
            from ...core.location_service import method_for_country
            new_method = method_for_country(loc.country_code)
            _method_keys = list(pc.METHODS.keys())
            if new_method in _method_keys:
                self._method_combo.setCurrentIndex(_method_keys.index(new_method))
            method_msg = f"  ·  {t('method_auto_set', new_method)}"
        self._status.setText(f"{t('loc_set_to')}{loc.city}, {loc.country}{method_msg}")
        self._status.setVisible(True)

    # ─── profiles ────────────────────────────────────────────────────────────

    def _refresh_profile_list(self):
        self._profile_list.clear()
        profiles = self._win.settings.profiles
        if not profiles:
            self._profile_list.addItem(t("profile_none"))
            self._profile_list.item(0).setFlags(Qt.ItemFlag.NoItemFlags)
            return
        for p in profiles:
            item = QListWidgetItem(f"📌  {p.get('name', '?')}  —  {p.get('city', '')}, {p.get('country', '')}")
            self._profile_list.addItem(item)

    def _save_profile(self):
        name, ok = QInputDialog.getText(
            self, t("profile_name_lbl"), t("profile_name_lbl"),
            text=t("profile_name_ph"),
        )
        if not ok or not name.strip():
            return
        name = name.strip()
        s = self._win.settings
        profile = {
            "name":          name,
            "latitude":      self._lat_spin.value(),
            "longitude":     self._lon_spin.value(),
            "timezone":      self._tz_spin.value(),
            "altitude":      self._alt_spin.value(),
            "city":          self._city_edit.text().strip(),
            "country":       self._country_edit.text().strip(),
            "method":        list(pc.METHODS.keys())[self._method_combo.currentIndex()],
        }
        # Replace if same name exists
        s.profiles = [p for p in s.profiles if p.get("name") != name]
        s.profiles.append(profile)
        from ...data.settings_manager import save as save_s
        save_s(s)
        self._refresh_profile_list()
        self._profile_status.setText(t("profile_saved", name))

    def _use_profile(self):
        row = self._profile_list.currentRow()
        profiles = self._win.settings.profiles
        if row < 0 or row >= len(profiles):
            return
        p = profiles[row]
        self._lat_spin.setValue(p.get("latitude", self._win.settings.latitude))
        self._lon_spin.setValue(p.get("longitude", self._win.settings.longitude))
        self._tz_spin.setValue(p.get("timezone", self._win.settings.timezone))
        self._alt_spin.setValue(p.get("altitude", 0.0))
        self._city_edit.setText(p.get("city", ""))
        self._country_edit.setText(p.get("country", ""))
        self._auto_loc_cb.setChecked(False)
        self._on_auto_loc_changed(0)
        method = p.get("method", "MWL")
        _keys = list(pc.METHODS.keys())
        if method in _keys:
            self._method_combo.setCurrentIndex(_keys.index(method))
        self._profile_status.setText(t("profile_applied", p.get("name", "?")))

    def _delete_profile(self):
        row = self._profile_list.currentRow()
        profiles = self._win.settings.profiles
        if row < 0 or row >= len(profiles):
            return
        name = profiles[row].get("name", "?")
        self._win.settings.profiles.pop(row)
        from ...data.settings_manager import save as save_s
        save_s(self._win.settings)
        self._refresh_profile_list()
        self._profile_status.setText(f"🗑 '{name}' dihapus.")

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
                         min_val: float, max_val: float, decimals: int) -> "_ModernSpin":
        row = QHBoxLayout()
        lbl = QLabel(label)
        lbl.setStyleSheet(f"color: {th.MUTED}; min-width: 180px; background: transparent;")
        step = 0.1 if decimals > 0 else 1.0
        spin = _ModernSpin(min_val, max_val, step=step, decimals=decimals)
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

    def _preview_notification(self):
        from datetime import datetime
        from ...core.notification_manager import PrayerAlertDialog
        now = datetime.now().strftime("%H:%M")
        dlg = PrayerAlertDialog("Dzuhur", "Dhuhr", now, None)
        dlg.remind_requested.connect(lambda _: dlg.accept())

        def _stop_sound():
            self._win._notif.stop_sound()

        dlg.finished.connect(_stop_sound)
        self._win._notif.play_adzan("Dhuhr")
        dlg.show()

    def _browse_sound(self):
        path, _ = QFileDialog.getOpenFileName(
            self, t("lbl_sound_file"), "",
            "Audio Files (*.mp3 *.wav *.ogg);;All Files (*.*)"
        )
        if path:
            self._sound_path.setText(path)

    def _browse_prayer_sound(self, edit: QLineEdit, prayer_name: str):
        path, _ = QFileDialog.getOpenFileName(
            self, f"{t('lbl_sound_file')} — {prayer_name}", "",
            "Audio Files (*.mp3 *.wav *.ogg);;All Files (*.*)"
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

        # Font size
        size_keys = [12, 13, 15, 17]
        fidx = size_keys.index(s.font_size) if s.font_size in size_keys else 1
        self._font_size_combo.blockSignals(True)
        self._font_size_combo.setCurrentIndex(fidx)
        self._font_size_combo.blockSignals(False)

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

        # Imsak
        self._imsak_spin.setValue(s.imsak_minutes)

        # Location
        self._auto_loc_cb.setChecked(s.auto_location)
        self._lat_spin.setValue(s.latitude)
        self._lon_spin.setValue(s.longitude)
        self._tz_spin.setValue(s.timezone)
        self._alt_spin.setValue(s.altitude)
        self._city_edit.setText(s.city)
        self._country_edit.setText(s.country)
        self._on_auto_loc_changed(2 if s.auto_location else 0)

        # Profiles
        self._refresh_profile_list()
        self._profile_status.setText("")

        # Notification
        self._notif_cb.setChecked(s.notification_enabled)
        self._sound_cb.setChecked(s.sound_enabled)
        self._toast_cb.setChecked(s.toast_enabled)
        self._sound_path.setText(s.custom_sound_path)

        reminder_keys = ["0", "5", "10", "15"]
        ridx = reminder_keys.index(str(s.reminder_minutes)) if str(s.reminder_minutes) in reminder_keys else 1
        self._reminder_combo.setCurrentIndex(ridx)

        for en, edit in self._prayer_sound_edits.items():
            edit.setText(s.prayer_sounds.get(en, ""))

        for en, cb in self._prayer_alarm_checks.items():
            default_on = (en != "Sunrise")
            cb.setChecked(s.prayer_alarms.get(en, default_on))

        # Window
        if self._startup_cb is not None and sys.platform == "win32":
            from ...data.settings_manager import is_startup_enabled
            self._startup_cb.blockSignals(True)
            self._startup_cb.setChecked(is_startup_enabled())
            self._startup_cb.blockSignals(False)
        self._start_min_cb.setChecked(s.start_minimized)
        self._tray_cb.setChecked(s.minimize_to_tray)

        self._status.setText("")
        self._status.setVisible(False)

        # Restore update badge if update was already found
        if getattr(self._win, "_latest_version", ""):
            self.show_update_available(self._win._latest_version, self._win._latest_url)

    def _save(self):
        s = self._win.settings
        old_theme = s.theme
        old_lang  = s.language

        _theme_keys = ["dark", "light", "system"]
        _ti = self._theme_combo.currentIndex()
        s.theme = _theme_keys[_ti] if 0 <= _ti < len(_theme_keys) else "dark"

        # Font size
        _size_keys = [12, 13, 15, 17]
        _fsi = self._font_size_combo.currentIndex()
        s.font_size = _size_keys[_fsi] if 0 <= _fsi < len(_size_keys) else 13

        _fmt_keys = ["24h", "12h"]
        _fi = self._time_fmt_combo.currentIndex()
        s.time_format = _fmt_keys[_fi] if 0 <= _fi < len(_fmt_keys) else "24h"

        _lang_keys = list(I18N_SUPPORTED)
        _li = self._lang_combo.currentIndex()
        s.language = _lang_keys[_li] if 0 <= _li < len(_lang_keys) else "id"

        _method_keys = list(pc.METHODS.keys())
        _mi = self._method_combo.currentIndex()
        s.method = _method_keys[_mi] if 0 <= _mi < len(_method_keys) else "Kemenag"
        s.asr_method = self._asr_combo.currentIndex() + 1
        s.imsak_minutes = self._imsak_spin.value()

        s.auto_location = self._auto_loc_cb.isChecked()
        s.latitude      = self._lat_spin.value()
        s.longitude     = self._lon_spin.value()
        s.timezone      = self._tz_spin.value()
        s.altitude      = self._alt_spin.value()
        s.city          = self._city_edit.text().strip()
        s.country       = self._country_edit.text().strip()

        s.notification_enabled = self._notif_cb.isChecked()
        s.sound_enabled        = self._sound_cb.isChecked()
        s.toast_enabled        = self._toast_cb.isChecked()
        s.custom_sound_path    = self._sound_path.text().strip()

        _reminder_keys = ["0", "5", "10", "15"]
        _ri = self._reminder_combo.currentIndex()
        s.reminder_minutes = int(_reminder_keys[_ri] if 0 <= _ri < len(_reminder_keys) else "5")

        for en, edit in self._prayer_sound_edits.items():
            s.prayer_sounds[en] = edit.text().strip()

        for en, cb in self._prayer_alarm_checks.items():
            s.prayer_alarms[en] = cb.isChecked()

        s.start_minimized  = self._start_min_cb.isChecked()
        s.minimize_to_tray = self._tray_cb.isChecked()

        self._win.on_settings_changed()
        set_language(s.language)

        if s.theme != old_theme:
            self._win.apply_theme_live(s.theme)
        elif s.language != old_lang:
            self._restart_app()
            return
        else:
            if hasattr(self._win, "_dash") and hasattr(self._win._dash, "refresh"):
                self._win._dash.refresh()

        self._status.setText(t("saved_ok"))
        self._status.setVisible(True)
