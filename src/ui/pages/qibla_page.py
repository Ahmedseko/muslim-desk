"""Qibla compass page."""
from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QFrame, QPushButton)

from ..widgets import QiblaCompass, SectionCard
from .. import theme as th
from ...core.qibla_calculator import qibla_bearing, distance_to_mecca_km
from ...i18n import t, compass_dir as _compass_dir


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
        lbl = QLabel(t("qibla_title"))
        lbl.setObjectName("H1")
        root.addWidget(lbl)

        sub = QLabel(t("qibla_subtitle"))
        sub.setObjectName("Muted")
        root.addWidget(sub)

        # ── Info bar: sensor limitation warning
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

        info_text = QLabel(t("qibla_static_warn"))
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

        lbl_compass = QLabel(t("qibla_compass_lbl"))
        lbl_compass.setStyleSheet(
            f"font-size: 14px; font-weight: 600; color: {th.HEADING}; background: transparent;"
        )
        lbl_compass.setAlignment(Qt.AlignmentFlag.AlignCenter)
        compass_layout.addWidget(lbl_compass)

        self._compass = QiblaCompass()
        compass_layout.addWidget(self._compass, 1)

        # Bearing label
        self._bearing_lbl = QLabel(f"0.0° {t('qibla_from_north')}")
        self._bearing_lbl.setStyleSheet(
            f"font-size: 18px; font-weight: 700; color: {th.ACCENT}; background: transparent;"
        )
        self._bearing_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        compass_layout.addWidget(self._bearing_lbl)

        # Needle legend
        legend = QHBoxLayout()
        legend.setSpacing(16)
        legend.setAlignment(Qt.AlignmentFlag.AlignCenter)
        for color, key in (("#ef4444", "compass_north_lbl"), (th.ACCENT_DK, "compass_qibla_lbl")):
            lbl_leg = QLabel(t(key))
            lbl_leg.setStyleSheet(f"color: {color}; font-size: 12px; background: transparent;")
            legend.addWidget(lbl_leg)
        compass_layout.addLayout(legend)

        content.addWidget(compass_card, 3)

        # ── Info panel (right)
        info_col = QVBoxLayout()
        info_col.setSpacing(12)

        # Location card
        self._loc_card = SectionCard(t("your_location_card"))
        self._loc_lat  = self._add_info_row(self._loc_card, t("lbl_latitude_short"), "—")
        self._loc_lon  = self._add_info_row(self._loc_card, t("lbl_longitude_short"), "—")
        self._loc_city = self._add_info_row(self._loc_card, t("lbl_city_short"), "—")
        info_col.addWidget(self._loc_card)

        # Qibla card
        self._qibla_card = SectionCard(t("qibla_card_title"))
        self._q_bearing  = self._add_info_row(self._qibla_card, t("qibla_angle_lbl"), "—")
        self._q_dir      = self._add_info_row(self._qibla_card, t("compass_dir_lbl"), "—")
        self._q_dist     = self._add_info_row(self._qibla_card, t("dist_to_mecca"), "—")
        info_col.addWidget(self._qibla_card)

        # Kaaba reference card
        kaaba_card = SectionCard(t("kaaba_ref_card"))
        self._add_info_row(kaaba_card, t("lbl_latitude_short"), "21.4225°")
        self._add_info_row(kaaba_card, t("lbl_longitude_short"), "39.8262°")
        self._add_info_row(kaaba_card, t("lbl_city_short"), t("kaaba_location_val"))
        info_col.addWidget(kaaba_card)

        # How-to-use card
        cara_card = SectionCard(t("how_to_use_card"))
        cara_text = QLabel(t("qibla_steps"))
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

        bearing = qibla_bearing(lat, lon)
        dist    = distance_to_mecca_km(lat, lon)

        self._compass.set_bearing(bearing)
        self._bearing_lbl.setText(f"{bearing:.1f}° {t('qibla_from_north')}")

        self._loc_lat.setText(f"{lat:.6f}°")
        self._loc_lon.setText(f"{lon:.6f}°")
        self._loc_city.setText(f"{s.city}, {s.country}")

        self._q_bearing.setText(f"{bearing:.2f}°")
        self._q_dir.setText(_compass_dir(bearing))
        self._q_dist.setText(f"{dist:,.1f} km")
