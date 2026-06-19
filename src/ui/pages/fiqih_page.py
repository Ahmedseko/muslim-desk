"""Fiqih (Islamic jurisprudence) reference page — 7 categories with search."""
from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QFrame, QPushButton, QScrollArea, QLineEdit,
                              QSizePolicy)

from .. import theme as th
from ...i18n import t, get_language
from ...data.fiqih_data import CATEGORIES, ENTRIES


class FiqihPage(QWidget):
    def __init__(self, main_win):
        super().__init__()
        self._win          = main_win
        self._active_cat   = CATEGORIES[0]["key"]
        self._search_text  = ""
        self._entry_frames: list[tuple[dict, QFrame]] = []
        self._build()
        self._show_category(self._active_cat)

    # ── build ─────────────────────────────────────────────────────────────────

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Main split: sidebar + content
        body = QHBoxLayout()
        body.setSpacing(0)
        body.setContentsMargins(0, 0, 0, 0)

        # ── Sidebar
        self._sidebar = self._build_sidebar()
        body.addWidget(self._sidebar)

        # ── Content area
        content = QVBoxLayout()
        content.setContentsMargins(28, 16, 28, 8)
        content.setSpacing(10)

        # Header
        hdr_row = QHBoxLayout()
        self._title_lbl = QLabel()
        self._title_lbl.setObjectName("H1")
        hdr_row.addWidget(self._title_lbl)
        hdr_row.addStretch()

        self._count_lbl = QLabel("")
        self._count_lbl.setStyleSheet(
            f"color: {th.MUTED}; font-size: 11px; background: transparent;"
        )
        hdr_row.addWidget(self._count_lbl)
        content.addLayout(hdr_row)

        # Search bar
        search_row = QHBoxLayout()
        search_row.setSpacing(8)

        self._search_box = QLineEdit()
        self._search_box.setPlaceholderText(t("fiqih_search_ph"))
        self._search_box.setMaximumWidth(320)
        self._search_box.setStyleSheet(
            f"QLineEdit {{ background: {th.SURFACE_2}; border: 1px solid {th.BORDER}; "
            f"border-radius: 8px; color: {th.TEXT}; padding: 4px 10px; font-size: 12px; }}"
            f"QLineEdit:focus {{ border-color: {th.ACCENT_DK}; }}"
        )
        self._search_box.textChanged.connect(self._on_search)
        search_row.addWidget(self._search_box)

        self._search_result_lbl = QLabel("")
        self._search_result_lbl.setStyleSheet(
            f"font-size: 11px; color: {th.MUTED}; background: transparent;"
        )
        search_row.addWidget(self._search_result_lbl)
        search_row.addStretch()
        content.addLayout(search_row)

        # Scroll area for entries
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self._container = QWidget()
        self._container.setStyleSheet("background: transparent;")
        self._entries_layout = QVBoxLayout(self._container)
        self._entries_layout.setContentsMargins(0, 0, 8, 0)
        self._entries_layout.setSpacing(6)
        self._scroll.setWidget(self._container)
        content.addWidget(self._scroll, 1)

        content_widget = QWidget()
        content_widget.setLayout(content)
        body.addWidget(content_widget, 1)

        root.addLayout(body)

    def _build_sidebar(self) -> QFrame:
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(200)

        lay = QVBoxLayout(sidebar)
        lay.setContentsMargins(8, 20, 8, 20)
        lay.setSpacing(4)

        lbl = QLabel("📚  " + t("nav_fiqih"))
        lbl.setStyleSheet(
            f"font-size: 13px; font-weight: 700; color: {th.ACCENT}; "
            f"background: transparent; padding: 0 6px 10px 6px;"
        )
        lay.addWidget(lbl)

        self._cat_buttons: dict[str, QPushButton] = {}
        for cat in CATEGORIES:
            btn = QPushButton(f"{cat['icon']}  {cat['label_id'] if get_language() == 'id' else cat['label_en']}")
            btn.setCheckable(True)
            btn.setFixedHeight(40)
            btn.setStyleSheet(
                f"QPushButton {{ text-align: left; padding: 0 12px; border: none; "
                f"border-radius: 8px; color: {th.TEXT}; background: transparent; font-size: 12px; }}"
                f"QPushButton:hover {{ background: {th.BTN_HOVER}; }}"
                f"QPushButton:checked {{ background: {th.ACCENT_DK}; color: #fff; font-weight: 700; }}"
            )
            btn.clicked.connect(lambda _, k=cat["key"]: self._show_category(k))
            lay.addWidget(btn)
            self._cat_buttons[cat["key"]] = btn

        lay.addStretch()
        return sidebar

    # ── category display ──────────────────────────────────────────────────────

    def _show_category(self, key: str):
        self._active_cat  = key
        self._search_text = ""
        self._search_box.blockSignals(True)
        self._search_box.clear()
        self._search_box.blockSignals(False)
        self._search_result_lbl.setText("")

        # Update sidebar button states
        for k, btn in self._cat_buttons.items():
            btn.setChecked(k == key)

        # Update title
        cat = next((c for c in CATEGORIES if c["key"] == key), None)
        if cat:
            lang = get_language()
            self._title_lbl.setText(cat["label_id"] if lang == "id" else cat["label_en"])

        # Filter entries for this category
        entries = [e for e in ENTRIES if e["category"] == key]
        self._render_entries(entries)

    def _on_search(self, text: str):
        self._search_text = text.strip().lower()
        if not self._search_text:
            self._show_category(self._active_cat)
            return

        lang = get_language()
        matches: list[dict] = []
        for e in ENTRIES:
            title   = (e["title_id"] if lang == "id" else e["title_en"]).lower()
            content = (e["content_id"] if lang == "id" else e["content_en"]).lower()
            if self._search_text in title or self._search_text in content:
                matches.append(e)

        if matches:
            self._search_result_lbl.setText(f"{len(matches)} hasil")
        else:
            self._search_result_lbl.setText(t("fiqih_no_results"))

        # Deselect category buttons during search
        for btn in self._cat_buttons.values():
            btn.setChecked(False)

        self._render_entries(matches)

    def _render_entries(self, entries: list[dict]):
        # Clear old widgets
        while self._entries_layout.count():
            item = self._entries_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self._entry_frames.clear()

        if not entries:
            lbl = QLabel(t("fiqih_no_results"))
            lbl.setStyleSheet(f"color: {th.MUTED}; background: transparent;")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._entries_layout.addWidget(lbl)
        else:
            self._count_lbl.setText(f"{len(entries)} topik")
            for entry in entries:
                frame = self._make_entry_frame(entry)
                self._entries_layout.addWidget(frame)
                self._entry_frames.append((entry, frame))

        self._entries_layout.addStretch()
        self._scroll.verticalScrollBar().setValue(0)

    def _make_entry_frame(self, entry: dict) -> QFrame:
        lang = get_language()
        title   = entry["title_id"]   if lang == "id" else entry["title_en"]
        content = entry["content_id"] if lang == "id" else entry["content_en"]
        evidence = entry.get("evidence", "")
        source   = entry.get("source", "")

        outer = QFrame()
        outer.setObjectName("Card")
        outer_lay = QVBoxLayout(outer)
        outer_lay.setContentsMargins(0, 0, 0, 0)
        outer_lay.setSpacing(0)

        # ── Header (always visible, clickable to expand)
        header = QFrame()
        header.setCursor(Qt.CursorShape.PointingHandCursor)
        header.setStyleSheet(
            f"QFrame {{ background: transparent; border: none; border-radius: 8px; }}"
        )
        h_lay = QHBoxLayout(header)
        h_lay.setContentsMargins(16, 14, 16, 14)
        h_lay.setSpacing(10)

        title_lbl = QLabel(title)
        title_lbl.setStyleSheet(
            f"font-size: 13px; font-weight: 700; color: {th.HEADING}; background: transparent;"
        )
        title_lbl.setWordWrap(True)
        h_lay.addWidget(title_lbl, 1)

        self._chevron = QPushButton("▼")
        chevron = QPushButton("▼")
        chevron.setFixedSize(24, 24)
        chevron.setFlat(True)
        chevron.setStyleSheet(
            f"QPushButton {{ background: transparent; border: none; "
            f"color: {th.MUTED}; font-size: 11px; }}"
        )
        h_lay.addWidget(chevron)
        outer_lay.addWidget(header)

        # ── Expandable body
        body = QFrame()
        body.setVisible(False)
        body.setStyleSheet("QFrame { border: none; background: transparent; }")
        body_lay = QVBoxLayout(body)
        body_lay.setContentsMargins(16, 0, 16, 14)
        body_lay.setSpacing(8)

        # Separator
        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background: {th.BORDER};")
        body_lay.addWidget(sep)

        # Content
        content_lbl = QLabel(content)
        content_lbl.setWordWrap(True)
        content_lbl.setStyleSheet(
            f"font-size: 13px; color: {th.TEXT}; background: transparent; line-height: 1.7;"
        )
        body_lay.addWidget(content_lbl)

        # Evidence + source
        if evidence:
            ev_row = QHBoxLayout()
            ev_key = QLabel(t("fiqih_evidence"))
            ev_key.setStyleSheet(f"font-size: 11px; font-weight: 700; color: {th.ACCENT}; background: transparent;")
            ev_val = QLabel(evidence)
            ev_val.setStyleSheet(f"font-size: 11px; color: {th.MUTED}; background: transparent;")
            ev_val.setWordWrap(True)
            ev_row.addWidget(ev_key)
            ev_row.addWidget(ev_val, 1)
            body_lay.addLayout(ev_row)

        if source:
            src_row = QHBoxLayout()
            src_key = QLabel(t("fiqih_source"))
            src_key.setStyleSheet(f"font-size: 11px; font-weight: 700; color: {th.MUTED}; background: transparent;")
            src_val = QLabel(source)
            src_val.setStyleSheet(f"font-size: 11px; color: {th.MUTED}; background: transparent;")
            src_val.setWordWrap(True)
            src_row.addWidget(src_key)
            src_row.addWidget(src_val, 1)
            body_lay.addLayout(src_row)

        outer_lay.addWidget(body)

        # Toggle expand on header / chevron click
        def _toggle():
            expanded = body.isVisible()
            body.setVisible(not expanded)
            chevron.setText("▲" if not expanded else "▼")

        header.mousePressEvent = lambda _: _toggle()
        chevron.clicked.connect(_toggle)

        return outer

    def refresh(self):
        pass
