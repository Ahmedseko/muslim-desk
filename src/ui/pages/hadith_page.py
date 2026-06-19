"""Hadith reader page — major shahih collections via api.hadith.gading.dev"""
from __future__ import annotations

import json
import threading
from pathlib import Path

from PyQt6.QtCore import Qt, QObject, pyqtSignal, QTimer
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QFrame, QPushButton, QScrollArea, QComboBox,
                              QLineEdit, QSizePolicy, QSpinBox)

from .. import theme as th
from ...i18n import t, get_language

_CACHE_DIR = Path.home() / ".muslim_desk" / "hadith"
_API_BASE   = "https://api.hadith.gading.dev/books/{book}?range={start}-{end}"
_PER_PAGE   = 20

_COLLECTIONS = [
    ("Shahih Bukhari",    "bukhari",   7563),
    ("Shahih Muslim",     "muslim",    3032),
    ("Sunan Abu Dawud",   "abu-dawud", 5274),
    ("Sunan Tirmidzi",    "tirmidzi",  3956),
    ("Sunan An-Nasai",    "nasai",     5761),
    ("Sunan Ibnu Majah",  "ibn-majah", 4341),
]


class _HadithSignal(QObject):
    loaded = pyqtSignal(list, int, int, bool)   # hadiths, total, page, from_cache
    error  = pyqtSignal(str)


class HadithPage(QWidget):
    def __init__(self, main_win):
        super().__init__()
        self._win        = main_win
        self._col_idx    = 0
        self._page       = 0
        self._total      = _COLLECTIONS[0][2]
        self._hadiths: list[dict] = []

        self._sig = _HadithSignal()
        self._sig.loaded.connect(self._on_loaded)
        self._sig.error.connect(self._on_error)

        self._build()
        self._load_page(0)

    # ── build ─────────────────────────────────────────────────────────────────

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 16, 28, 8)
        root.setSpacing(10)

        # Header
        header = QHBoxLayout()
        lbl = QLabel(t("hadith_title"))
        lbl.setObjectName("H1")
        header.addWidget(lbl)
        header.addStretch()
        self._cache_lbl = QLabel("")
        self._cache_lbl.setStyleSheet(
            f"color: {th.MUTED}; font-size: 11px; background: transparent;"
        )
        header.addWidget(self._cache_lbl)
        root.addLayout(header)

        # Collection + search row
        ctrl_row = QHBoxLayout()
        ctrl_row.setSpacing(8)

        col_lbl = QLabel(t("hadith_collection") + ":")
        col_lbl.setStyleSheet(f"color: {th.MUTED}; background: transparent;")
        ctrl_row.addWidget(col_lbl)

        self._col_combo = QComboBox()
        self._col_combo.setMinimumWidth(200)
        for name, _, _ in _COLLECTIONS:
            self._col_combo.addItem(name)
        self._col_combo.currentIndexChanged.connect(self._on_collection_changed)
        ctrl_row.addWidget(self._col_combo)

        ctrl_row.addStretch()

        search_lbl = QLabel("🔍")
        search_lbl.setStyleSheet("background: transparent; font-size: 14px;")
        ctrl_row.addWidget(search_lbl)

        self._search_box = QLineEdit()
        self._search_box.setPlaceholderText(t("hadith_search_ph"))
        self._search_box.setMaximumWidth(220)
        self._search_box.setStyleSheet(
            f"QLineEdit {{ background: {th.SURFACE_2}; border: 1px solid {th.BORDER}; "
            f"border-radius: 8px; color: {th.TEXT}; padding: 4px 10px; font-size: 12px; }}"
            f"QLineEdit:focus {{ border-color: {th.ACCENT_DK}; }}"
        )
        self._search_box.returnPressed.connect(self._on_search)
        ctrl_row.addWidget(self._search_box)

        btn_search = QPushButton(t("btn_search_city").replace("🔍 ", ""))
        btn_search.setFixedHeight(32)
        btn_search.clicked.connect(self._on_search)
        ctrl_row.addWidget(btn_search)
        root.addLayout(ctrl_row)

        # Navigation row
        nav_row = QHBoxLayout()
        nav_row.setSpacing(8)

        self._btn_prev = QPushButton(t("hadith_prev"))
        self._btn_prev.setFixedHeight(32)
        self._btn_prev.clicked.connect(self._prev_page)
        nav_row.addWidget(self._btn_prev)

        self._page_lbl = QLabel("")
        self._page_lbl.setStyleSheet(
            f"color: {th.MUTED}; font-size: 12px; background: transparent;"
        )
        self._page_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        nav_row.addWidget(self._page_lbl, 1)

        self._btn_next = QPushButton(t("hadith_next"))
        self._btn_next.setObjectName("Primary")
        self._btn_next.setFixedHeight(32)
        self._btn_next.clicked.connect(self._next_page)
        nav_row.addWidget(self._btn_next)

        nav_row.addSpacing(16)

        goto_lbl = QLabel(t("hadith_goto"))
        goto_lbl.setStyleSheet(f"color: {th.MUTED}; font-size: 12px; background: transparent;")
        nav_row.addWidget(goto_lbl)

        self._goto_spin = QSpinBox()
        self._goto_spin.setMinimum(1)
        self._goto_spin.setMaximum(self._total)
        self._goto_spin.setFixedWidth(80)
        self._goto_spin.setFixedHeight(32)
        self._goto_spin.editingFinished.connect(self._on_goto)
        nav_row.addWidget(self._goto_spin)
        root.addLayout(nav_row)

        # Status
        self._status_lbl = QLabel(t("hadith_loading"))
        self._status_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._status_lbl.setStyleSheet(
            f"color: {th.MUTED}; font-size: 12px; background: transparent;"
        )

        self._retry_btn = QPushButton(t("hadith_retry"))
        self._retry_btn.setFixedHeight(30)
        self._retry_btn.hide()
        self._retry_btn.clicked.connect(lambda: self._load_page(self._page, force=True))

        st_row = QHBoxLayout()
        st_row.addStretch()
        st_row.addWidget(self._status_lbl)
        st_row.addWidget(self._retry_btn)
        st_row.addStretch()
        root.addLayout(st_row)

        # Scroll area for hadith cards
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self._container = QWidget()
        self._container.setStyleSheet("background: transparent;")
        self._layout = QVBoxLayout(self._container)
        self._layout.setContentsMargins(0, 0, 8, 0)
        self._layout.setSpacing(8)
        self._scroll.setWidget(self._container)
        root.addWidget(self._scroll, 1)

    # ── navigation ────────────────────────────────────────────────────────────

    def _on_collection_changed(self, idx: int):
        if idx < 0:
            return
        self._col_idx = idx
        self._total   = _COLLECTIONS[idx][2]
        self._goto_spin.setMaximum(self._total)
        self._load_page(0)

    def _prev_page(self):
        if self._page > 0:
            self._load_page(self._page - 1)

    def _next_page(self):
        max_page = (self._total - 1) // _PER_PAGE
        if self._page < max_page:
            self._load_page(self._page + 1)

    def _on_goto(self):
        num = self._goto_spin.value()
        page = (num - 1) // _PER_PAGE
        self._load_page(page)

    def _on_search(self):
        text = self._search_box.text().strip()
        if not text:
            return
        # If it's a number, jump to that hadith
        try:
            num = int(text)
            self._goto_spin.setValue(max(1, min(num, self._total)))
            self._on_goto()
            return
        except ValueError:
            pass
        # Text search: filter within current loaded hadiths
        self._render_hadiths(
            [h for h in self._hadiths
             if text.lower() in h.get("id", "").lower()],
            is_search=True,
        )

    # ── load ──────────────────────────────────────────────────────────────────

    def _load_page(self, page: int, force: bool = False):
        self._page = page
        self._status_lbl.setText(t("hadith_loading"))
        self._status_lbl.show()
        self._retry_btn.hide()
        self._cache_lbl.setText("")
        self._update_nav_labels()
        self._clear_cards()

        _, book, _ = _COLLECTIONS[self._col_idx]
        start = page * _PER_PAGE + 1
        end   = min(start + _PER_PAGE - 1, self._total)

        threading.Thread(
            target=self._fetch_thread,
            args=(book, start, end, page, force),
            daemon=True,
        ).start()

    def _fetch_thread(self, book: str, start: int, end: int, page: int, force: bool):
        cache_path = _CACHE_DIR / f"{book}_{start}_{end}.json"

        if not force and cache_path.exists():
            try:
                data = json.loads(cache_path.read_text(encoding="utf-8"))
                self._sig.loaded.emit(data["hadiths"], data["total"], page, True)
                return
            except Exception:
                pass

        try:
            import requests
            url = _API_BASE.format(book=book, start=start, end=end)
            r = requests.get(url, timeout=15)
            r.raise_for_status()
            body     = r.json()
            d        = body.get("data", {})
            hadiths  = d.get("hadiths", [])
            total    = d.get("available", self._total)

            try:
                _CACHE_DIR.mkdir(parents=True, exist_ok=True)
                cache_path.write_text(
                    json.dumps({"hadiths": hadiths, "total": total}, ensure_ascii=False),
                    encoding="utf-8",
                )
            except Exception:
                pass

            self._sig.loaded.emit(hadiths, total, page, False)
        except Exception:
            self._sig.error.emit(t("hadith_offline"))

    # ── display ───────────────────────────────────────────────────────────────

    def _on_loaded(self, hadiths: list, total: int, page: int, from_cache: bool):
        self._hadiths = hadiths
        self._total   = total
        self._goto_spin.setMaximum(total)
        self._status_lbl.hide()
        self._retry_btn.hide()
        self._cache_lbl.setText(t("hadith_cached") if from_cache else "")
        self._update_nav_labels()
        self._render_hadiths(hadiths)

    def _on_error(self, msg: str):
        self._status_lbl.setText(msg)
        self._status_lbl.show()
        self._retry_btn.show()

    def _update_nav_labels(self):
        _, book, _ = _COLLECTIONS[self._col_idx]
        start = self._page * _PER_PAGE + 1
        end   = min(start + _PER_PAGE - 1, self._total)
        col_name = _COLLECTIONS[self._col_idx][0]
        self._page_lbl.setText(
            f"{col_name}  ·  No. {start}–{end}  {t('hadith_of')}  {self._total}"
        )
        self._btn_prev.setEnabled(self._page > 0)
        self._btn_next.setEnabled(end < self._total)

    def _render_hadiths(self, hadiths: list, is_search: bool = False):
        self._clear_cards()
        col_name = _COLLECTIONS[self._col_idx][0]
        for h in hadiths:
            card = self._make_card(h, col_name)
            self._layout.addWidget(card)
        if not hadiths:
            lbl = QLabel(t("fiqih_no_results"))
            lbl.setStyleSheet(f"color: {th.MUTED}; background: transparent;")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._layout.addWidget(lbl)
        self._layout.addStretch()
        self._scroll.verticalScrollBar().setValue(0)

    def _clear_cards(self):
        while self._layout.count():
            item = self._layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _make_card(self, h: dict, col_name: str) -> QFrame:
        num   = h.get("number", "")
        arab  = h.get("arab", "")
        trans = h.get("id", "")   # Indonesian translation from gading API

        frame = QFrame()
        frame.setObjectName("Card")
        lay = QVBoxLayout(frame)
        lay.setContentsMargins(16, 14, 16, 14)
        lay.setSpacing(10)

        # ── Number + source row
        top_row = QHBoxLayout()
        num_lbl = QLabel(f"{t('hadith_no')} {num}")
        num_lbl.setStyleSheet(
            f"font-size: 13px; font-weight: 700; color: {th.ACCENT}; background: transparent;"
        )
        top_row.addWidget(num_lbl)
        top_row.addStretch()
        src_lbl = QLabel(f"{t('hadith_source')} {col_name} no. {num}")
        src_lbl.setStyleSheet(
            f"font-size: 11px; color: {th.MUTED}; background: transparent;"
        )
        top_row.addWidget(src_lbl)
        lay.addLayout(top_row)

        # Separator
        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background: {th.BORDER};")
        lay.addWidget(sep)

        # ── Arabic text
        if arab:
            ar_lbl = QLabel(arab)
            ar_lbl.setWordWrap(True)
            ar_lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            ar_lbl.setStyleSheet(
                f"font-size: 22px; line-height: 2.0; color: {th.HEADING}; "
                f"font-family: 'Amiri', 'Traditional Arabic', 'Arial Unicode MS', 'Arial'; "
                f"background: transparent; padding: 4px 0;"
            )
            lay.addWidget(ar_lbl)

            sep2 = QFrame()
            sep2.setFixedHeight(1)
            sep2.setStyleSheet(f"background: {th.BORDER};")
            lay.addWidget(sep2)

        # ── Translation
        if trans:
            lang = get_language()
            tr_header = QLabel(t("hadith_translation"))
            tr_header.setStyleSheet(
                f"font-size: 11px; color: {th.MUTED}; background: transparent;"
            )
            lay.addWidget(tr_header)

            tr_lbl = QLabel(trans)
            tr_lbl.setWordWrap(True)
            tr_lbl.setStyleSheet(
                f"font-size: 13px; color: {th.TEXT}; background: transparent; "
                f"line-height: 1.7; padding: 2px 0;"
            )
            lay.addWidget(tr_lbl)

        return frame

    def refresh(self):
        pass
