"""Custom reusable PyQt6 widgets for Muslim Desk."""
from __future__ import annotations

import math
import sys
from typing import Optional

from PyQt6.QtCore import Qt, QSize, QRect, QPoint, QTimer, pyqtSignal, QPointF
from PyQt6.QtGui import (QPainter, QColor, QPen, QBrush, QFont, QFontMetrics,
                          QIcon, QPixmap, QLinearGradient, QRadialGradient,
                          QPainterPath, QPolygonF)
from PyQt6.QtWidgets import (QWidget, QFrame, QLabel, QVBoxLayout, QHBoxLayout,
                              QPushButton, QSizePolicy, QApplication,
                              QDialog, QLineEdit, QListWidget, QListWidgetItem,
                              QAbstractItemView)

from . import theme as th
from ..i18n import t


# ───────────────────────── helpers ──────────────────────────────────────────

def _h(widget: QWidget) -> QHBoxLayout:
    lo = QHBoxLayout(widget)
    lo.setContentsMargins(0, 0, 0, 0)
    lo.setSpacing(0)
    return lo


def _v(widget: QWidget) -> QVBoxLayout:
    lo = QVBoxLayout(widget)
    lo.setContentsMargins(0, 0, 0, 0)
    lo.setSpacing(0)
    return lo


# ───────────────────────── App icon (generated) ─────────────────────────────

def make_app_icon(size: int = 64) -> QIcon:
    """Load icon.ico if available, else draw crescent+star programmatically."""
    import os
    from pathlib import Path
    ico_candidates = [
        Path(__file__).parent.parent.parent / "assets" / "icon.ico",
        Path(os.path.dirname(os.path.abspath(sys.argv[0]))) / "assets" / "icon.ico",
        Path("assets") / "icon.ico",
    ]
    for ico_path in ico_candidates:
        if ico_path.exists():
            return QIcon(str(ico_path))
    return _draw_icon(size)


def _draw_icon(size: int = 64) -> QIcon:
    pix = QPixmap(size, size)
    pix.fill(Qt.GlobalColor.transparent)
    p = QPainter(pix)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)

    grad = QRadialGradient(size * 0.40, size * 0.36, size * 0.58)
    grad.setColorAt(0.0, QColor("#1db954"))
    grad.setColorAt(0.45, QColor("#16a34a"))
    grad.setColorAt(1.0, QColor("#052e16"))
    p.setBrush(QBrush(grad))
    p.setPen(Qt.PenStyle.NoPen)
    p.drawEllipse(1, 1, size - 2, size - 2)

    p.setBrush(QBrush(QColor("white")))
    p.setPen(Qt.PenStyle.NoPen)
    cx, cy, r = size * 0.42, size * 0.50, size * 0.30
    path = QPainterPath()
    path.addEllipse(QPointF(cx, cy), r, r)
    cut = QPainterPath()
    cut.addEllipse(QPointF(cx + r * 0.40, cy - r * 0.06), r * 0.78, r * 0.78)
    path -= cut
    p.drawPath(path)

    star_x, star_y, star_r = size * 0.745, size * 0.285, size * 0.105
    star_pts = []
    for i in range(5):
        outer = math.radians(-90 + i * 72)
        inner = math.radians(-90 + i * 72 + 36)
        star_pts.append(QPointF(star_x + star_r * math.cos(outer),
                                star_y + star_r * math.sin(outer)))
        star_pts.append(QPointF(star_x + star_r * 0.40 * math.cos(inner),
                                star_y + star_r * 0.40 * math.sin(inner)))
    poly = QPolygonF(star_pts)
    star_path = QPainterPath()
    star_path.addPolygon(poly)
    p.drawPath(star_path)
    p.end()
    return QIcon(pix)


# ───────────────────────── NavButton ────────────────────────────────────────

class NavButton(QPushButton):
    """Sidebar navigation button with emoji icon + text."""

    def __init__(self, icon_char: str, label: str, parent=None):
        super().__init__(parent)
        self.setObjectName("NavButton")
        self.setCheckable(True)
        self.setFixedHeight(44)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        row = QHBoxLayout(self)
        row.setContentsMargins(12, 0, 12, 0)
        row.setSpacing(10)

        self._icon_lbl = QLabel(icon_char)
        self._icon_lbl.setFixedWidth(22)
        self._icon_lbl.setStyleSheet("font-size: 16px; background: transparent;")
        self._icon_lbl.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        self._text_lbl = QLabel(label)
        self._text_lbl.setStyleSheet("font-size: 14px; background: transparent;")
        self._text_lbl.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        row.addWidget(self._icon_lbl)
        row.addWidget(self._text_lbl, 1)

    def set_label(self, text: str):
        self._text_lbl.setText(text)


# ───────────────────────── PrayerCard ───────────────────────────────────────

class PrayerCard(QFrame):
    """Card displaying a single prayer time with alarm toggle."""

    alarm_toggled = pyqtSignal(str, bool)   # prayer_en, enabled

    def __init__(self, prayer_en: str, prayer_id: str, color: str, parent=None):
        super().__init__(parent)
        self.prayer_en = prayer_en
        self.setObjectName("PrayerCard")
        self.setMinimumWidth(110)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setFixedHeight(210)

        root = QVBoxLayout(self)
        root.setContentsMargins(20, 18, 20, 16)
        root.setSpacing(6)

        # Colour dot
        dot = QLabel("●")
        dot.setStyleSheet(f"color: {color}; font-size: 11px; background: transparent;")
        root.addWidget(dot)

        # Prayer name
        lbl_id = QLabel(prayer_id)
        lbl_id.setStyleSheet(f"font-size: 17px; font-weight: 700; color: {color};"
                              f"background: transparent;")
        root.addWidget(lbl_id)

        # Time
        self._time_lbl = QLabel("--:--")
        self._time_lbl.setStyleSheet(f"font-size: 36px; font-weight: 800;"
                                      f"color: {th.HEADING}; background: transparent;")
        root.addWidget(self._time_lbl)

        # Countdown (only visible for next prayer)
        self._countdown_lbl = QLabel("")
        self._countdown_lbl.setStyleSheet(f"font-size: 12px; color: {th.MUTED};"
                                           f"background: transparent;")
        root.addWidget(self._countdown_lbl)

        root.addStretch()

        # Alarm button
        self._alarm_btn = QPushButton(t("alarm_active"))
        self._alarm_btn.setObjectName("AlarmOn")
        self._alarm_btn.setFixedHeight(32)
        self._alarm_btn.clicked.connect(self._toggle_alarm)
        root.addWidget(self._alarm_btn)

        self._alarm_on = True

    def set_time(self, time_str: str):
        self._time_lbl.setText(time_str)

    def set_countdown(self, text: str):
        self._countdown_lbl.setText(text)
        self._countdown_lbl.setVisible(bool(text))

    def set_active(self, active: bool):
        self.setProperty("active", "true" if active else "false")
        self.style().unpolish(self)
        self.style().polish(self)

    def set_alarm(self, enabled: bool):
        self._alarm_on = enabled
        if enabled:
            self._alarm_btn.setText(t("alarm_active"))
            self._alarm_btn.setObjectName("AlarmOn")
        else:
            self._alarm_btn.setText(t("alarm_inactive"))
            self._alarm_btn.setObjectName("AlarmOff")
        self._alarm_btn.style().unpolish(self._alarm_btn)
        self._alarm_btn.style().polish(self._alarm_btn)

    def _toggle_alarm(self):
        self._alarm_on = not self._alarm_on
        self.set_alarm(self._alarm_on)
        self.alarm_toggled.emit(self.prayer_en, self._alarm_on)


# ───────────────────────── NextPrayerBanner ─────────────────────────────────

class NextPrayerBanner(QFrame):
    """Full-width banner showing countdown to next prayer — 3-column layout."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("NextPrayerBanner")
        self.setFixedHeight(100)

        root = QHBoxLayout(self)
        root.setContentsMargins(32, 0, 32, 0)
        root.setSpacing(0)

        def _col(caption: str, value_text: str) -> tuple[QVBoxLayout, QLabel]:
            col = QVBoxLayout()
            col.setSpacing(2)
            col.setAlignment(Qt.AlignmentFlag.AlignCenter)
            cap = QLabel(caption)
            cap.setAlignment(Qt.AlignmentFlag.AlignCenter)
            cap.setStyleSheet(f"font-size: 11px; color: {th.MUTED}; font-weight: 500; letter-spacing: 1px;")
            val = QLabel(value_text)
            val.setAlignment(Qt.AlignmentFlag.AlignCenter)
            col.addWidget(cap)
            col.addWidget(val)
            return col, val

        def _sep() -> QFrame:
            s = QFrame()
            s.setFixedWidth(1)
            s.setFixedHeight(52)
            s.setStyleSheet(f"background: {th.BORDER};")
            return s

        col1, self._prayer_name = _col(t("next_prayer"), "—")
        self._prayer_name.setStyleSheet(
            f"font-size: 26px; font-weight: 800; color: {th.ACCENT};"
        )

        col2, self._time_lbl = _col(t("prayer_time_lbl"), "--:--")
        self._time_lbl.setStyleSheet(
            f"font-size: 26px; font-weight: 700; color: {th.HEADING};"
        )

        col3, self._countdown_lbl = _col(t("countdown_lbl"), "--:--:--")
        self._countdown_lbl.setStyleSheet(
            f"font-size: 26px; font-weight: 800; color: {th.ACCENT};"
        )

        root.addLayout(col1, 1)
        root.addWidget(_sep())
        root.addLayout(col2, 1)
        root.addWidget(_sep())
        root.addLayout(col3, 1)

    def update_next(self, name_id: str, time_str: str, countdown: str, color: str):
        self._prayer_name.setText(name_id)
        self._prayer_name.setStyleSheet(
            f"font-size: 26px; font-weight: 800; color: {color};"
        )
        self._time_lbl.setText(time_str)
        self._countdown_lbl.setText(countdown)
        self._countdown_lbl.setStyleSheet(
            f"font-size: 26px; font-weight: 800; color: {color};"
        )


# ───────────────────────── ClockWidget ──────────────────────────────────────

class ClockWidget(QWidget):
    """Digital clock, toggleable between 12h (AM/PM) and 24h format."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._fmt = "24h"
        self.setStyleSheet("background: transparent;")

        row = QHBoxLayout(self)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(6)
        row.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._time_lbl = QLabel("00:00:00")
        self._time_lbl.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        self._time_lbl.setStyleSheet(
            f"font-size: 48px; font-weight: 800; color: {th.HEADING};"
            f"background: transparent; letter-spacing: 4px;"
        )

        self._ampm_lbl = QLabel("AM")
        self._ampm_lbl.setAlignment(Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignLeft)
        self._ampm_lbl.setStyleSheet(
            f"font-size: 16px; font-weight: 700; color: {th.MUTED};"
            f"background: transparent; padding-bottom: 6px;"
        )
        self._ampm_lbl.setVisible(False)

        row.addWidget(self._time_lbl)
        row.addWidget(self._ampm_lbl)

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(1000)
        self._tick()

    def set_format(self, fmt: str):
        """Switch between '12h' and '24h' display."""
        self._fmt = fmt
        self._ampm_lbl.setVisible(fmt == "12h")
        self._tick()

    def _tick(self):
        from datetime import datetime
        now = datetime.now()
        if self._fmt == "12h":
            self._time_lbl.setText(now.strftime("%I:%M:%S"))
            self._ampm_lbl.setText(now.strftime("%p"))
        else:
            self._time_lbl.setText(now.strftime("%H:%M:%S"))


# ───────────────────────── DateHeader ───────────────────────────────────────

class DateHeader(QWidget):
    """Widget showing Gregorian + Hijri date and city."""

    def __init__(self, parent=None):
        super().__init__(parent)
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(2)

        self._greg_lbl  = QLabel("—")
        self._greg_lbl.setStyleSheet(f"font-size: 15px; font-weight: 600; color: {th.TEXT}; background: transparent;")
        self._hijri_lbl = QLabel("—")
        self._hijri_lbl.setStyleSheet(f"font-size: 13px; color: {th.MUTED}; background: transparent;")

        root.addWidget(self._greg_lbl)
        root.addWidget(self._hijri_lbl)

    def update_dates(self, gregorian: str, hijri: str):
        self._greg_lbl.setText(gregorian)
        self._hijri_lbl.setText(hijri)


# ───────────────────────── QiblaCompass ─────────────────────────────────────

class QiblaCompass(QWidget):
    """Animated compass widget pointing towards Mecca."""

    def __init__(self, bearing: float = 0.0, parent=None):
        super().__init__(parent)
        self._bearing = bearing
        self._target  = bearing
        self._anim_timer = QTimer(self)
        self._anim_timer.timeout.connect(self._animate_step)
        self.setMinimumSize(260, 260)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def set_bearing(self, bearing: float):
        self._target = bearing % 360
        if not self._anim_timer.isActive():
            self._anim_timer.start(16)

    def _animate_step(self):
        diff = (self._target - self._bearing + 540) % 360 - 180
        if abs(diff) < 0.5:
            self._bearing = self._target
            self._anim_timer.stop()
        else:
            self._bearing += diff * 0.12
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        W, H = self.width(), self.height()
        cx, cy = W / 2, H / 2
        R = min(W, H) / 2 - 16

        # Background disc
        p.setBrush(QBrush(QColor(th.SURFACE)))
        p.setPen(QPen(QColor(th.BORDER), 2))
        p.drawEllipse(QPointF(cx, cy), R, R)

        # Cardinal labels
        p.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        for angle, label in ((0, "U"), (90, "T"), (180, "S"), (270, "B")):
            rad = math.radians(angle - 90)
            tx = cx + (R - 18) * math.cos(rad)
            ty = cy + (R - 18) * math.sin(rad)
            p.setPen(QColor(th.MUTED))
            p.drawText(QRect(int(tx) - 10, int(ty) - 10, 20, 20),
                       Qt.AlignmentFlag.AlignCenter, label)

        # Tick marks
        p.setPen(QPen(QColor(th.BORDER), 1))
        for deg in range(0, 360, 10):
            rad = math.radians(deg - 90)
            inner = R - (8 if deg % 90 == 0 else 4)
            outer = R
            p.drawLine(
                QPointF(cx + inner * math.cos(rad), cy + inner * math.sin(rad)),
                QPointF(cx + outer * math.cos(rad), cy + outer * math.sin(rad)),
            )

        # North indicator (red)
        rad_n = math.radians(-90)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(QColor("#ef4444")))
        north_pts = [
            QPointF(cx + math.cos(rad_n) * (R - 20), cy + math.sin(rad_n) * (R - 20)),
            QPointF(cx + math.cos(rad_n + 2.44) * 10, cy + math.sin(rad_n + 2.44) * 10),
            QPointF(cx + math.cos(rad_n - 2.44) * 10, cy + math.sin(rad_n - 2.44) * 10),
        ]
        p.drawPolygon(QPolygonF(north_pts))

        # Qibla needle (green)
        qibla_rad = math.radians(self._bearing - 90)
        needle_color = QColor(th.ACCENT_DK)
        p.setBrush(QBrush(needle_color))
        needle_pts = [
            QPointF(cx + math.cos(qibla_rad) * (R - 24),
                    cy + math.sin(qibla_rad) * (R - 24)),
            QPointF(cx + math.cos(qibla_rad + 2.8) * 12,
                    cy + math.sin(qibla_rad + 2.8) * 12),
            QPointF(cx + math.cos(qibla_rad + math.pi) * 18,
                    cy + math.sin(qibla_rad + math.pi) * 18),
            QPointF(cx + math.cos(qibla_rad - 2.8) * 12,
                    cy + math.sin(qibla_rad - 2.8) * 12),
        ]
        p.drawPolygon(QPolygonF(needle_pts))

        # Kaaba icon at needle tip
        p.setFont(QFont("Segoe UI", 14))
        tip_x = cx + math.cos(qibla_rad) * (R - 28)
        tip_y = cy + math.sin(qibla_rad) * (R - 28)
        p.drawText(QRect(int(tip_x) - 12, int(tip_y) - 12, 24, 24),
                   Qt.AlignmentFlag.AlignCenter, "🕋")

        # Center hub
        p.setPen(QPen(QColor(th.BORDER), 2))
        p.setBrush(QBrush(QColor(th.SURFACE_2)))
        p.drawEllipse(QPointF(cx, cy), 10, 10)

        p.end()


# ───────────────────────── Section card ─────────────────────────────────────

# ───────────────────────── CitySearchDialog ─────────────────────────────────

class CitySearchDialog(QDialog):
    """Search city/district using Nominatim and return selected LocationInfo."""

    location_selected = pyqtSignal(object)   # LocationInfo
    # Internal signal to safely deliver results from background thread to UI thread
    _results_ready    = pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(t("city_search_win_title"))
        self.setMinimumSize(560, 460)
        self.setModal(True)
        self._results: list[dict] = []
        self._results_ready.connect(self._on_results)
        self._build()

    def _build(self):
        self.setStyleSheet(f"""
            QDialog {{ background: {th.BG}; border: 1px solid {th.BORDER}; border-radius: 12px; }}
            QLabel  {{ background: transparent; color: {th.TEXT}; }}
        """)
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 18, 20, 18)
        root.setSpacing(12)

        title = QLabel(t("city_search_title"))
        title.setStyleSheet(f"font-size: 16px; font-weight: 700; color: {th.HEADING}; background: transparent;")
        root.addWidget(title)

        hint = QLabel(t("city_search_hint"))
        hint.setStyleSheet(f"font-size: 12px; color: {th.MUTED}; background: transparent;")
        hint.setWordWrap(True)
        root.addWidget(hint)

        # Search row
        row = QHBoxLayout()
        row.setSpacing(8)
        self._search_edit = QLineEdit()
        self._search_edit.setPlaceholderText(t("city_search_placeholder"))
        self._search_edit.returnPressed.connect(self._do_search)
        self._btn_search = QPushButton(t("city_search_btn"))
        self._btn_search.setObjectName("Primary")
        self._btn_search.setFixedWidth(80)
        self._btn_search.clicked.connect(self._do_search)
        row.addWidget(self._search_edit, 1)
        row.addWidget(self._btn_search)
        root.addLayout(row)

        # Status
        self._status_lbl = QLabel("")
        self._status_lbl.setStyleSheet(f"font-size: 12px; color: {th.MUTED}; background: transparent;")
        root.addWidget(self._status_lbl)

        # Results list
        self._list = QListWidget()
        # Hindari border-bottom di dalam item — menyebabkan hover flicker di Qt6
        # Gunakan alternatingRowColors + spacing sebagai pengganti separator
        self._list.setStyleSheet(f"""
            QListWidget {{
                background: {th.SURFACE};
                border: 1px solid {th.BORDER};
                border-radius: 8px;
                outline: 0;
            }}
            QListWidget::item {{
                padding: 11px 14px;
                color: {th.TEXT};
                background: transparent;
            }}
            QListWidget::item:hover {{
                background: {th.SURFACE_2};
                color: {th.TEXT};
            }}
            QListWidget::item:selected,
            QListWidget::item:selected:hover {{
                background: {th.ACCENT_DK};
                color: #ffffff;
            }}
        """)
        self._list.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self._list.setMouseTracking(True)
        # Klik sekali → pilih item; dobel klik → langsung confirm
        self._list.itemClicked.connect(self._on_item_clicked)
        self._list.itemDoubleClicked.connect(self._confirm)
        self._list.currentItemChanged.connect(self._on_item_changed)
        root.addWidget(self._list, 1)

        # Detail label
        self._detail_lbl = QLabel("")
        self._detail_lbl.setStyleSheet(f"font-size: 11px; color: {th.MUTED}; background: transparent;")
        self._detail_lbl.setWordWrap(True)
        root.addWidget(self._detail_lbl)

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)
        btn_row.addStretch()
        btn_cancel = QPushButton(t("btn_cancel"))
        btn_cancel.clicked.connect(self.reject)
        self._btn_pilih = QPushButton(t("city_search_select"))
        self._btn_pilih.setObjectName("Primary")
        self._btn_pilih.setEnabled(False)
        self._btn_pilih.clicked.connect(self._confirm)
        btn_row.addWidget(btn_cancel)
        btn_row.addWidget(self._btn_pilih)
        root.addLayout(btn_row)

    def _do_search(self):
        query = self._search_edit.text().strip()
        if not query:
            return
        self._status_lbl.setText(t("city_search_searching"))
        self._btn_search.setEnabled(False)
        self._list.clear()
        self._results = []
        self._btn_pilih.setEnabled(False)
        self._detail_lbl.setText("")

        import threading
        threading.Thread(target=self._search_thread, args=(query,), daemon=True).start()

    def _search_thread(self, query: str):
        # Absolute import — relative imports fail in background threads
        from src.core.location_service import search_city
        results = search_city(query)
        # Emit signal to deliver results safely to the UI (main) thread
        self._results_ready.emit(results)

    def _on_results(self, results: list):
        self._results = results
        self._btn_search.setEnabled(True)
        if not results:
            self._status_lbl.setText(t("city_search_not_found"))
            return
        self._status_lbl.setText(t("city_search_found", len(results)))
        for item in results:
            li = QListWidgetItem(item["display_name"])
            li.setToolTip(item["full_name"])
            self._list.addItem(li)
        # Pilih baris pertama otomatis dan pindahkan fokus ke list
        self._list.setCurrentRow(0)
        self._list.setFocus()

    def _on_item_clicked(self, item):
        """Single click → seleksi dan tampilkan detail."""
        idx = self._list.row(item)
        if 0 <= idx < len(self._results):
            self._list.setCurrentRow(idx)

    def _on_item_changed(self, current, _prev):
        if current is None:
            return
        idx = self._list.row(current)
        if 0 <= idx < len(self._results):
            r = self._results[idx]
            from src.core.location_service import tz_label
            tz_str = tz_label(r["timezone"])
            self._detail_lbl.setText(
                f"📍 {r['full_name']}\n"
                f"{t('lbl_latitude_short')}: {r['lat']:.6f}°  ·  "
                f"{t('lbl_longitude_short')}: {r['lon']:.6f}°  ·  "
                f"{t('lbl_timezone_short')}: {tz_str}"
            )
            self._btn_pilih.setEnabled(True)

    def _confirm(self, *_):
        idx = self._list.currentRow()
        if 0 <= idx < len(self._results):
            from src.core.location_service import LocationInfo
            r = self._results[idx]
            loc = LocationInfo(
                latitude=r["lat"],
                longitude=r["lon"],
                city=r["city"],
                country=r["country"],
                country_code=r.get("country_code", ""),
                timezone=r["timezone"],
                timezone_name=r.get("timezone_name", ""),
            )
            self.location_selected.emit(loc)
            self.accept()


# ───────────────────────── SectionCard ──────────────────────────────────────

class SectionCard(QFrame):
    """Card with a title header, same style as seko_cyber."""

    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.setObjectName("Card")
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 14, 16, 16)
        root.setSpacing(12)

        lbl = QLabel(title)
        lbl.setStyleSheet(f"font-size: 14px; font-weight: 600; color: {th.HEADING};"
                          f"background: transparent;")
        root.addWidget(lbl)

        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background: {th.BORDER};")
        root.addWidget(sep)

        self._body = QVBoxLayout()
        self._body.setSpacing(8)
        root.addLayout(self._body)

    @property
    def body(self) -> QVBoxLayout:
        return self._body
