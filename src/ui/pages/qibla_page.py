"""Qibla compass page."""
from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QFrame, QPushButton)

from ..widgets import QiblaCompass, SectionCard
from .. import theme as th
from ...core.qibla_calculator import qibla_bearing, distance_to_mecca_km, compass_direction


class QiblaPage(QWidget):
    def __init__(self, main_win):
        super().__init__()
        self._win = main_win
        self._build()
        self.refresh()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 20, 28, 20)
        root.setSpacing(16)

        # Header
        lbl = QLabel("Arah Kiblat")
        lbl.setObjectName("H1")
        root.addWidget(lbl)

        sub = QLabel("Arah menuju Ka'bah, Masjidil Haram, Makkah Al-Mukarramah")
        sub.setObjectName("Muted")
        root.addWidget(sub)

        # ── Info bar: keterbatasan sensor
        info_bar = QFrame()
        info_bar.setObjectName("Card")
        info_bar.setStyleSheet(
            f"QFrame#Card {{ background: {th.SURFACE}; border: 1px solid {th.BORDER};"
            f"border-left: 4px solid {th.WARN}; border-radius: 10px; }}"
        )
        info_layout = QHBoxLayout(info_bar)
        info_layout.setContentsMargins(16, 12, 16, 12)
        info_layout.setSpacing(12)

        icon_lbl = QLabel("⚠️")
        icon_lbl.setStyleSheet("font-size: 18px; background: transparent;")
        info_layout.addWidget(icon_lbl)

        info_text = QLabel(
            "<b>Kompas ini bersifat statis — tidak real-time.</b><br>"
            "Laptop umumnya <b>tidak memiliki sensor magnetometer</b> seperti ponsel, "
            "sehingga jarum tidak dapat berputar mengikuti arah fisik laptop. "
            "Gunakan panduan di bawah untuk menentukan arah kiblat secara akurat."
        )
        info_text.setStyleSheet(f"color: {th.TEXT}; font-size: 13px; background: transparent;")
        info_text.setWordWrap(True)
        info_text.setTextFormat(Qt.TextFormat.RichText)
        info_layout.addWidget(info_text, 1)
        root.addWidget(info_bar)

        # Content row: compass on left, info on right
        content = QHBoxLayout()
        content.setSpacing(20)

        # ── Compass card
        compass_card = QFrame()
        compass_card.setObjectName("Card")
        compass_layout = QVBoxLayout(compass_card)
        compass_layout.setContentsMargins(20, 20, 20, 20)
        compass_layout.setSpacing(10)
        compass_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        lbl_compass = QLabel("Kompas Kiblat")
        lbl_compass.setStyleSheet(
            f"font-size: 14px; font-weight: 600; color: {th.HEADING}; background: transparent;"
        )
        lbl_compass.setAlignment(Qt.AlignmentFlag.AlignCenter)
        compass_layout.addWidget(lbl_compass)

        self._compass = QiblaCompass()
        compass_layout.addWidget(self._compass, 1)

        # Bearing + legend row
        self._bearing_lbl = QLabel("0.0° dari Utara")
        self._bearing_lbl.setStyleSheet(
            f"font-size: 18px; font-weight: 700; color: {th.ACCENT}; background: transparent;"
        )
        self._bearing_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        compass_layout.addWidget(self._bearing_lbl)

        # Needle legend
        legend = QHBoxLayout()
        legend.setSpacing(16)
        legend.setAlignment(Qt.AlignmentFlag.AlignCenter)
        for color, text in (("#ef4444", "● Utara (N)"), (th.ACCENT_DK, "● Arah Kiblat")):
            lbl_leg = QLabel(text)
            lbl_leg.setStyleSheet(f"color: {color}; font-size: 12px; background: transparent;")
            legend.addWidget(lbl_leg)
        compass_layout.addLayout(legend)

        content.addWidget(compass_card, 3)

        # ── Info panel (right)
        info_col = QVBoxLayout()
        info_col.setSpacing(12)

        # Location card
        self._loc_card = SectionCard("📍  Lokasi Anda")
        self._loc_lat  = self._add_info_row(self._loc_card, "Lintang", "—")
        self._loc_lon  = self._add_info_row(self._loc_card, "Bujur", "—")
        self._loc_city = self._add_info_row(self._loc_card, "Kota", "—")
        info_col.addWidget(self._loc_card)

        # Qibla card
        self._qibla_card = SectionCard("🕋  Arah Kiblat")
        self._q_bearing  = self._add_info_row(self._qibla_card, "Sudut dari Utara", "—")
        self._q_dir      = self._add_info_row(self._qibla_card, "Arah Kompas", "—")
        self._q_dist     = self._add_info_row(self._qibla_card, "Jarak ke Makkah", "—")
        info_col.addWidget(self._qibla_card)

        # Kaaba info
        kaaba_card = SectionCard("🕌  Ka'bah (Patokan)")
        self._add_info_row(kaaba_card, "Lintang", "21.4225° U")
        self._add_info_row(kaaba_card, "Bujur", "39.8262° T")
        self._add_info_row(kaaba_card, "Lokasi", "Makkah Al-Mukarramah, Arab Saudi")
        info_col.addWidget(kaaba_card)

        # Cara pakai — diperjelas karena laptop tidak ada sensor
        cara_card = SectionCard("📖  Cara Menggunakan di Laptop")
        cara_text = QLabel(
            "<b>Langkah 1</b> — Cari arah Utara terlebih dahulu.<br>"
            "Gunakan kompas HP, Google Maps, atau matahari (pagi = Timur).<br><br>"
            "<b>Langkah 2</b> — Putar badan/laptop sehingga menghadap Utara.<br><br>"
            "<b>Langkah 3</b> — Dari posisi menghadap Utara, putar badan<br>"
            "sesuai sudut kiblat yang tertera (misal: <b>292°</b> = hampir ke Barat, sedikit ke Utara).<br><br>"
            "<b>Langkah 4</b> — Arah wajah Anda sekarang = arah Kiblat. ✅<br><br>"
            "<span style='color: #8b949e; font-size: 12px;'>"
            "💡 Untuk akurasi real-time, gunakan kompas HP bersama bearing dari aplikasi ini.</span>"
        )
        cara_text.setStyleSheet(f"color: {th.TEXT}; font-size: 13px; background: transparent;")
        cara_text.setWordWrap(True)
        cara_text.setTextFormat(Qt.TextFormat.RichText)
        cara_card.body.addWidget(cara_text)
        info_col.addWidget(cara_card)

        info_col.addStretch()
        content.addLayout(info_col, 2)
        root.addLayout(content, 1)

    def _add_info_row(self, card: SectionCard, label: str, value: str) -> QLabel:
        row = QHBoxLayout()
        row.setSpacing(8)
        lbl = QLabel(label)
        lbl.setStyleSheet(f"color: {th.MUTED}; font-size: 13px; min-width: 140px; background: transparent;")
        val = QLabel(value)
        val.setStyleSheet(f"color: {th.TEXT}; font-size: 13px; font-weight: 600; background: transparent;")
        row.addWidget(lbl)
        row.addWidget(val, 1)
        card.body.addLayout(row)
        return val

    def refresh(self):
        s = self._win.settings
        lat = s.latitude
        lon = s.longitude

        bearing  = qibla_bearing(lat, lon)
        dist     = distance_to_mecca_km(lat, lon)
        direction = compass_direction(bearing)

        self._compass.set_bearing(bearing)
        self._bearing_lbl.setText(f"{bearing:.1f}° dari Utara")

        self._loc_lat.setText(f"{lat:.6f}°")
        self._loc_lon.setText(f"{lon:.6f}°")
        self._loc_city.setText(f"{s.city}, {s.country}")

        self._q_bearing.setText(f"{bearing:.2f}°")
        self._q_dir.setText(direction)
        self._q_dist.setText(f"{dist:,.1f} km")
