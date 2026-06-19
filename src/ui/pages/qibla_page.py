"""Qibla compass page — compact modern layout."""
from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame)

from ..widgets import QiblaCompass
from .. import theme as th
from ...core.qibla_calculator import qibla_bearing, distance_to_mecca_km
from ...i18n import t, compass_dir as _compass_dir


class QiblaPage(QWidget):
    def __init__(self, main_win):
        super().__init__()
        self._win = main_win
        self._build()
        self.refresh()

    # ─── build ──────────────────────────────────────────────────────────────

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 20, 28, 20)
        root.setSpacing(14)

        # Header
        lbl = QLabel(t("qibla_title"))
        lbl.setObjectName("H1")
        root.addWidget(lbl)
        sub = QLabel(t("qibla_subtitle"))
        sub.setObjectName("Muted")
        root.addWidget(sub)

        # ── Content row
        content = QHBoxLayout()
        content.setSpacing(16)
        content.addWidget(self._build_compass_card())
        content.addLayout(self._build_right_col(), 1)
        root.addLayout(content, 1)

    # ─── left: compact compass card ─────────────────────────────────────────

    def _build_compass_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("Card")
        card.setFixedWidth(264)
        cl = QVBoxLayout(card)
        cl.setContentsMargins(18, 16, 18, 16)
        cl.setSpacing(8)

        # Compass widget
        self._compass = QiblaCompass()
        self._compass.setFixedSize(220, 220)
        cl.addWidget(self._compass, 0, Qt.AlignmentFlag.AlignHCenter)

        # Big bearing number
        self._bearing_lbl = QLabel("—")
        self._bearing_lbl.setStyleSheet(
            f"font-size: 32px; font-weight: 800; color: {th.ACCENT}; "
            f"background: transparent; letter-spacing: 1px;"
        )
        self._bearing_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cl.addWidget(self._bearing_lbl)

        # Direction · Distance
        self._dir_dist_lbl = QLabel("—")
        self._dir_dist_lbl.setStyleSheet(
            f"font-size: 13px; color: {th.MUTED}; background: transparent;"
        )
        self._dir_dist_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cl.addWidget(self._dir_dist_lbl)

        # Needle legend
        leg = QHBoxLayout()
        leg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        leg.setSpacing(16)
        for color, text in (("#ef4444", "● Utara (N)"), (th.ACCENT_DK, "● Kiblat")):
            ll = QLabel(text)
            ll.setStyleSheet(f"color: {color}; font-size: 11px; background: transparent;")
            leg.addWidget(ll)
        cl.addLayout(leg)

        # Static-compass note
        warn = QLabel("🧭 Kompas statis — arahkan laptop ke Utara")
        warn.setStyleSheet(
            f"color: {th.WARN}; font-size: 11px; background: transparent; padding-top: 4px;"
        )
        warn.setAlignment(Qt.AlignmentFlag.AlignCenter)
        warn.setWordWrap(True)
        cl.addWidget(warn)

        return card

    # ─── right: info + steps ────────────────────────────────────────────────

    def _build_right_col(self) -> QVBoxLayout:
        col = QVBoxLayout()
        col.setSpacing(12)

        # Row 1: Location + Qibla stats
        stats_row = QHBoxLayout()
        stats_row.setSpacing(12)
        stats_row.addWidget(self._build_loc_card(), 1)
        stats_row.addWidget(self._build_qibla_card(), 1)
        col.addLayout(stats_row)

        # Row 2: Ka'bah reference (compact single line)
        kaaba = QFrame()
        kaaba.setObjectName("Card")
        kl = QHBoxLayout(kaaba)
        kl.setContentsMargins(14, 10, 14, 10)
        kl.setSpacing(10)
        kl.addWidget(QLabel("🕋"), 0)
        info = QLabel(
            "<b>Ka'bah</b> · Masjidil Haram, Makkah Al-Mukarramah, Saudi Arabia"
            "  <span style='color: #8b949e'>  21.4225°, 39.8262°</span>"
        )
        info.setStyleSheet(f"font-size: 12px; color: {th.TEXT}; background: transparent;")
        info.setTextFormat(Qt.TextFormat.RichText)
        kl.addWidget(info, 1)
        col.addWidget(kaaba)

        # Row 3: Steps guide
        col.addWidget(self._build_steps_card(), 1)

        return col

    def _build_loc_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("Card")
        vl = QVBoxLayout(card)
        vl.setContentsMargins(14, 12, 14, 14)
        vl.setSpacing(6)

        hdr = QLabel("📍 " + t("your_location_card"))
        hdr.setStyleSheet(
            f"font-size: 11px; font-weight: 700; color: {th.MUTED}; "
            f"background: transparent; text-transform: uppercase; letter-spacing: 1px;"
        )
        vl.addWidget(hdr)

        self._loc_city = QLabel("—")
        self._loc_city.setStyleSheet(
            f"font-size: 15px; font-weight: 700; color: {th.HEADING}; background: transparent;"
        )
        self._loc_city.setWordWrap(True)
        vl.addWidget(self._loc_city)

        coords = QHBoxLayout()
        coords.setSpacing(10)
        self._loc_lat = QLabel("—")
        self._loc_lat.setStyleSheet(f"font-size: 11px; color: {th.MUTED}; background: transparent;")
        self._loc_lon = QLabel("—")
        self._loc_lon.setStyleSheet(f"font-size: 11px; color: {th.MUTED}; background: transparent;")
        coords.addWidget(self._loc_lat)
        coords.addWidget(self._loc_lon)
        coords.addStretch()
        vl.addLayout(coords)

        return card

    def _build_qibla_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("Card")
        vl = QVBoxLayout(card)
        vl.setContentsMargins(14, 12, 14, 14)
        vl.setSpacing(6)

        hdr = QLabel("🕌 " + t("qibla_card_title"))
        hdr.setStyleSheet(
            f"font-size: 11px; font-weight: 700; color: {th.MUTED}; "
            f"background: transparent; text-transform: uppercase; letter-spacing: 1px;"
        )
        vl.addWidget(hdr)

        self._q_bearing_big = QLabel("—")
        self._q_bearing_big.setStyleSheet(
            f"font-size: 28px; font-weight: 800; color: {th.ACCENT}; background: transparent;"
        )
        vl.addWidget(self._q_bearing_big)

        detail = QHBoxLayout()
        detail.setSpacing(14)
        self._q_dir = QLabel("—")
        self._q_dir.setStyleSheet(
            f"font-size: 13px; font-weight: 700; color: {th.TEXT}; background: transparent;"
        )
        self._q_dist = QLabel("—")
        self._q_dist.setStyleSheet(f"font-size: 13px; color: {th.MUTED}; background: transparent;")
        detail.addWidget(self._q_dir)
        detail.addWidget(self._q_dist)
        detail.addStretch()
        vl.addLayout(detail)

        return card

    def _build_steps_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("Card")
        vl = QVBoxLayout(card)
        vl.setContentsMargins(14, 12, 14, 14)
        vl.setSpacing(10)

        hdr = QLabel("📖 " + t("how_to_use_card"))
        hdr.setStyleSheet(
            f"font-size: 13px; font-weight: 700; color: {th.HEADING}; background: transparent;"
        )
        vl.addWidget(hdr)

        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background: {th.BORDER};")
        vl.addWidget(sep)

        self._steps_lbl = QLabel()
        self._steps_lbl.setStyleSheet(
            f"font-size: 12px; color: {th.TEXT}; background: transparent; line-height: 1.8;"
        )
        self._steps_lbl.setWordWrap(True)
        self._steps_lbl.setTextFormat(Qt.TextFormat.RichText)
        vl.addWidget(self._steps_lbl)

        return card

    # ─── refresh ────────────────────────────────────────────────────────────

    def refresh(self):
        s = self._win.settings
        lat, lon = s.latitude, s.longitude
        bearing   = qibla_bearing(lat, lon)
        dist      = distance_to_mecca_km(lat, lon)
        dir_label = _compass_dir(bearing)
        b_int     = int(round(bearing))

        self._compass.set_bearing(bearing)
        self._bearing_lbl.setText(f"{bearing:.1f}°")
        self._dir_dist_lbl.setText(f"{dir_label}  ·  {dist:,.0f} km dari Mekkah")

        self._loc_city.setText(f"{s.city}, {s.country}")
        self._loc_lat.setText(f"Lat {lat:.4f}°")
        self._loc_lon.setText(f"Lon {lon:.4f}°")

        self._q_bearing_big.setText(f"{bearing:.1f}°")
        self._q_dir.setText(dir_label)
        self._q_dist.setText(f"{dist:,.0f} km")

        muted = th.MUTED
        accent = th.ACCENT
        self._steps_lbl.setText(
            f"<b>1.</b> Cari arah Utara menggunakan kompas HP atau Google Maps.<br>"
            f"<b>2.</b> Hadapkan laptop/badan ke arah <b>Utara (N)</b>.<br>"
            f"<b>3.</b> Dari Utara, putar <b style='color:{accent}'>{b_int}° searah jarum jam</b>"
            f" &nbsp;≈ arah <b>{dir_label}</b>.<br>"
            f"<b>4.</b> Arah yang dihadapi = <b>Kiblat</b> ✅<br>"
            f"<br><span style='color:{muted}; font-size:11px;'>"
            f"💡 Untuk akurasi lebih tinggi, gunakan kompas HP dengan sudut {b_int}° dari Utara.</span>"
        )
