"""Al-Quran reader page — surah list + verse display with API + local cache."""
from __future__ import annotations

import json
import threading
from pathlib import Path

from PyQt6.QtCore import Qt, pyqtSignal, QObject, QUrl
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QFrame, QPushButton, QScrollArea, QComboBox,
                              QLineEdit, QSizePolicy)

from .. import theme as th
from ..widgets import VerseNumberBadge
from ...i18n import t, get_language

_CACHE_DIR      = Path.home() / ".muslim_desk" / "quran"
_AUDIO_CACHE_DIR = _CACHE_DIR / "audio"
_STATE_FILE     = _CACHE_DIR / "state.json"

# Precompute global ayah offset for each surah (1-indexed → 0-based index)
_GLOBAL_OFFSET: list[int] = []
_total_ayahs = 0

_RECITERS = [
    ("Mishary Rashid Alafasy", "ar.alafasy"),
    ("Abdul Basit (Murattal)", "ar.abdulbasitmurattal"),
    ("Saad Al-Ghamdi",         "ar.saadalghamdi"),
    ("Yasser Al-Dosari",       "ar.yasseraldossary"),
]
_CDN_AUDIO = "https://cdn.islamic.network/quran/audio/128/{edition}/{num}.mp3"
_BOOKMARKS_FILE = _CACHE_DIR / "bookmarks.json"

# 114 surahs: (number, latin_name, arabic_name, ayah_count, has_bismillah)
_SURAHS = [
    (1,"Al-Fatihah","الفاتحة",7,False),(2,"Al-Baqarah","البقرة",286,True),
    (3,"Ali 'Imran","آل عمران",200,True),(4,"An-Nisa'","النساء",176,True),
    (5,"Al-Ma'idah","المائدة",120,True),(6,"Al-An'am","الأنعام",165,True),
    (7,"Al-A'raf","الأعراف",206,True),(8,"Al-Anfal","الأنفال",75,True),
    (9,"At-Tawbah","التوبة",129,False),(10,"Yunus","يونس",109,True),
    (11,"Hud","هود",123,True),(12,"Yusuf","يوسف",111,True),
    (13,"Ar-Ra'd","الرعد",43,True),(14,"Ibrahim","إبراهيم",52,True),
    (15,"Al-Hijr","الحجر",99,True),(16,"An-Nahl","النحل",128,True),
    (17,"Al-Isra'","الإسراء",111,True),(18,"Al-Kahf","الكهف",110,True),
    (19,"Maryam","مريم",98,True),(20,"Ta-Ha","طه",135,True),
    (21,"Al-Anbiya'","الأنبياء",112,True),(22,"Al-Hajj","الحج",78,True),
    (23,"Al-Mu'minun","المؤمنون",118,True),(24,"An-Nur","النور",64,True),
    (25,"Al-Furqan","الفرقان",77,True),(26,"Ash-Shu'ara'","الشعراء",227,True),
    (27,"An-Naml","النمل",93,True),(28,"Al-Qasas","القصص",88,True),
    (29,"Al-'Ankabut","العنكبوت",69,True),(30,"Ar-Rum","الروم",60,True),
    (31,"Luqman","لقمان",34,True),(32,"As-Sajdah","السجدة",30,True),
    (33,"Al-Ahzab","الأحزاب",73,True),(34,"Saba'","سبأ",54,True),
    (35,"Fatir","فاطر",45,True),(36,"Ya-Sin","يس",83,True),
    (37,"As-Saffat","الصافات",182,True),(38,"Sad","ص",88,True),
    (39,"Az-Zumar","الزمر",75,True),(40,"Ghafir","غافر",85,True),
    (41,"Fussilat","فصلت",54,True),(42,"Ash-Shura","الشورى",53,True),
    (43,"Az-Zukhruf","الزخرف",89,True),(44,"Ad-Dukhan","الدخان",59,True),
    (45,"Al-Jathiyah","الجاثية",37,True),(46,"Al-Ahqaf","الأحقاف",35,True),
    (47,"Muhammad","محمد",38,True),(48,"Al-Fath","الفتح",29,True),
    (49,"Al-Hujurat","الحجرات",18,True),(50,"Qaf","ق",45,True),
    (51,"Adh-Dhariyat","الذاريات",60,True),(52,"At-Tur","الطور",49,True),
    (53,"An-Najm","النجم",62,True),(54,"Al-Qamar","القمر",55,True),
    (55,"Ar-Rahman","الرحمن",78,True),(56,"Al-Waqi'ah","الواقعة",96,True),
    (57,"Al-Hadid","الحديد",29,True),(58,"Al-Mujadila","المجادلة",22,True),
    (59,"Al-Hashr","الحشر",24,True),(60,"Al-Mumtahanah","الممتحنة",13,True),
    (61,"As-Saf","الصف",14,True),(62,"Al-Jumu'ah","الجمعة",11,True),
    (63,"Al-Munafiqun","المنافقون",11,True),(64,"At-Taghabun","التغابن",18,True),
    (65,"At-Talaq","الطلاق",12,True),(66,"At-Tahrim","التحريم",12,True),
    (67,"Al-Mulk","الملك",30,True),(68,"Al-Qalam","القلم",52,True),
    (69,"Al-Haqqah","الحاقة",52,True),(70,"Al-Ma'arij","المعارج",44,True),
    (71,"Nuh","نوح",28,True),(72,"Al-Jinn","الجن",28,True),
    (73,"Al-Muzzammil","المزمل",20,True),(74,"Al-Muddaththir","المدثر",56,True),
    (75,"Al-Qiyamah","القيامة",40,True),(76,"Al-Insan","الإنسان",31,True),
    (77,"Al-Mursalat","المرسلات",50,True),(78,"An-Naba'","النبأ",40,True),
    (79,"An-Nazi'at","النازعات",46,True),(80,"'Abasa","عبس",42,True),
    (81,"At-Takwir","التكوير",29,True),(82,"Al-Infitar","الانفطار",19,True),
    (83,"Al-Mutaffifin","المطففين",36,True),(84,"Al-Inshiqaq","الانشقاق",25,True),
    (85,"Al-Buruj","البروج",22,True),(86,"At-Tariq","الطارق",17,True),
    (87,"Al-A'la","الأعلى",19,True),(88,"Al-Ghashiyah","الغاشية",26,True),
    (89,"Al-Fajr","الفجر",30,True),(90,"Al-Balad","البلد",20,True),
    (91,"Ash-Shams","الشمس",15,True),(92,"Al-Layl","الليل",21,True),
    (93,"Ad-Duha","الضحى",11,True),(94,"Ash-Sharh","الشرح",8,True),
    (95,"At-Tin","التين",8,True),(96,"Al-'Alaq","العلق",19,True),
    (97,"Al-Qadr","القدر",5,True),(98,"Al-Bayyinah","البينة",8,True),
    (99,"Az-Zalzalah","الزلزلة",8,True),(100,"Al-'Adiyat","العاديات",11,True),
    (101,"Al-Qari'ah","القارعة",11,True),(102,"At-Takathur","التكاثر",8,True),
    (103,"Al-'Asr","العصر",3,True),(104,"Al-Humazah","الهمزة",9,True),
    (105,"Al-Fil","الفيل",5,True),(106,"Quraysh","قريش",4,True),
    (107,"Al-Ma'un","الماعون",7,True),(108,"Al-Kawthar","الكوثر",3,True),
    (109,"Al-Kafirun","الكافرون",6,True),(110,"An-Nasr","النصر",3,True),
    (111,"Al-Masad","المسد",5,True),(112,"Al-Ikhlas","الإخلاص",4,True),
    (113,"Al-Falaq","الفلق",5,True),(114,"An-Nas","الناس",6,True),
]

_API_BASE = "https://api.alquran.cloud/v1/surah/{n}/editions/quran-uthmani,{tr}"
_TR_EDITIONS = {"id": "id.indonesian", "en": "en.sahih"}

# Build global ayah offset table (surah 1 starts at global ayah 1)
for _s in _SURAHS:
    _GLOBAL_OFFSET.append(_total_ayahs + 1)   # 1-indexed global start for this surah
    _total_ayahs += _s[3]


class _QuranSignal(QObject):
    loaded = pyqtSignal(list, list, bool)   # arabic_ayahs, id_ayahs, from_cache
    error  = pyqtSignal(str)


class _AudioSignal(QObject):
    ready = pyqtSignal(str, object)   # (cache_path, btn)
    error = pyqtSignal(object)        # btn


class QuranPage(QWidget):
    def __init__(self, main_win):
        super().__init__()
        self._win           = main_win
        self._current_surah = 1
        self._sig = _QuranSignal()
        self._sig.loaded.connect(self._on_loaded)
        self._sig.error.connect(self._on_error)

        self._bookmarks: list[dict] = []
        self._bm_visible = False
        self._load_bookmarks()

        # Verse tracking for search
        self._verse_widgets: list[tuple[int, QWidget, str]] = []  # (num, widget, translation)

        # Audio player
        self._player     = QMediaPlayer(self)
        self._audio_out  = QAudioOutput(self)
        self._player.setAudioOutput(self._audio_out)
        self._audio_out.setVolume(1.0)
        self._playing_btn: QPushButton | None = None
        self._audio_sig = _AudioSignal()
        self._audio_sig.ready.connect(self._on_audio_ready)
        self._audio_sig.error.connect(self._on_audio_error)
        self._current_reciter = _RECITERS[0][1]   # default Alafasy

        self._build()

        # Auto-load last read surah
        self._load_surah(self._read_state())

    # ─── persistence: last-read state ─────────────────────────────────────────

    def _read_state(self) -> int:
        try:
            return int(json.loads(_STATE_FILE.read_text(encoding="utf-8")).get("surah", 1))
        except Exception:
            return 1

    def _write_state(self, surah: int):
        try:
            _CACHE_DIR.mkdir(parents=True, exist_ok=True)
            _STATE_FILE.write_text(json.dumps({"surah": surah}), encoding="utf-8")
        except Exception:
            pass

    # ─── persistence: bookmarks ───────────────────────────────────────────────

    def _load_bookmarks(self):
        try:
            self._bookmarks = json.loads(_BOOKMARKS_FILE.read_text(encoding="utf-8"))
        except Exception:
            self._bookmarks = []

    def _save_bookmarks(self):
        try:
            _CACHE_DIR.mkdir(parents=True, exist_ok=True)
            _BOOKMARKS_FILE.write_text(
                json.dumps(self._bookmarks, ensure_ascii=False), encoding="utf-8"
            )
        except Exception:
            pass

    def _is_bookmarked(self, surah: int, ayah: int) -> bool:
        return any(b["surah"] == surah and b["ayah"] == ayah for b in self._bookmarks)

    def _toggle_bookmark(self, surah: int, ayah: int, preview: str, btn: QPushButton):
        if self._is_bookmarked(surah, ayah):
            self._bookmarks = [b for b in self._bookmarks
                               if not (b["surah"] == surah and b["ayah"] == ayah)]
        else:
            self._bookmarks.append({
                "surah":      surah,
                "surah_name": _SURAHS[surah - 1][1],
                "ayah":       ayah,
                "preview":    preview[:80],
            })
        self._save_bookmarks()
        self._update_bm_btn(btn, self._is_bookmarked(surah, ayah))
        self._refresh_bm_panel()
        self._update_bm_toggle_label()

    # ─── build ────────────────────────────────────────────────────────────────

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 20, 28, 20)
        root.setSpacing(10)

        # ── Header
        header = QHBoxLayout()
        lbl_title = QLabel(t("quran_title"))
        lbl_title.setObjectName("H1")
        header.addWidget(lbl_title)
        header.addStretch()

        self._cache_lbl = QLabel("")
        self._cache_lbl.setStyleSheet(
            f"color: {th.MUTED}; font-size: 11px; background: transparent;"
        )
        header.addWidget(self._cache_lbl)

        self._bm_toggle_btn = QPushButton("🔖  " + t("quran_bookmarks") + "  (0)")
        self._bm_toggle_btn.setFixedHeight(34)
        self._bm_toggle_btn.setStyleSheet(
            f"QPushButton {{ background: {th.SURFACE_2}; border: 1px solid {th.BORDER}; "
            f"border-radius: 8px; color: {th.TEXT}; font-size: 12px; padding: 0 14px; }}"
            f"QPushButton:hover {{ border-color: {th.ACCENT_DK}; color: {th.ACCENT}; }}"
        )
        self._bm_toggle_btn.clicked.connect(self._toggle_bm_panel)
        header.addWidget(self._bm_toggle_btn)
        root.addLayout(header)

        # ── Selector row
        sel_row = QHBoxLayout()
        sel_row.setSpacing(8)

        lbl_sel = QLabel(t("quran_select"))
        lbl_sel.setStyleSheet(f"color: {th.MUTED}; background: transparent;")
        sel_row.addWidget(lbl_sel)

        self._search_box = QLineEdit()
        self._search_box.setPlaceholderText(t("quran_search_ph"))
        self._search_box.setMaximumWidth(180)
        self._search_box.textChanged.connect(self._filter_surahs)
        sel_row.addWidget(self._search_box)

        self._surah_combo = QComboBox()
        self._surah_combo.setMinimumWidth(240)
        self._populate_combo()
        self._surah_combo.currentIndexChanged.connect(self._on_surah_selected)
        sel_row.addWidget(self._surah_combo, 1)

        btn_prev = QPushButton(t("quran_prev"))
        btn_prev.setFixedHeight(32)
        btn_prev.clicked.connect(self._prev_surah)
        sel_row.addWidget(btn_prev)

        btn_next = QPushButton(t("quran_next"))
        btn_next.setObjectName("Primary")
        btn_next.setFixedHeight(32)
        btn_next.clicked.connect(self._next_surah)
        sel_row.addWidget(btn_next)
        root.addLayout(sel_row)

        # ── Last-read banner
        self._last_read_frame = QFrame()
        self._last_read_frame.setStyleSheet(
            f"QFrame {{ background: rgba(74,222,128,0.08); "
            f"border: 1px solid rgba(74,222,128,0.28); border-radius: 8px; }}"
        )
        lr_lay = QHBoxLayout(self._last_read_frame)
        lr_lay.setContentsMargins(14, 8, 14, 8)
        lr_lay.setSpacing(10)

        lr_icon = QLabel("📖")
        lr_icon.setStyleSheet("font-size: 15px; background: transparent; border: none;")
        lr_lay.addWidget(lr_icon)

        self._last_read_lbl = QLabel("")
        self._last_read_lbl.setStyleSheet(
            f"color: {th.TEXT}; font-size: 12px; background: transparent; border: none;"
        )
        lr_lay.addWidget(self._last_read_lbl, 1)

        self._last_read_frame.setVisible(False)
        root.addWidget(self._last_read_frame)

        # ── Status
        self._status_lbl = QLabel(t("quran_loading"))
        self._status_lbl.setStyleSheet(
            f"color: {th.MUTED}; font-size: 12px; background: transparent;"
        )
        self._status_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._retry_btn = QPushButton(t("quran_retry"))
        self._retry_btn.setFixedHeight(30)
        self._retry_btn.hide()
        self._retry_btn.clicked.connect(
            lambda: self._load_surah(self._current_surah, force=True)
        )

        status_row = QHBoxLayout()
        status_row.addStretch()
        status_row.addWidget(self._status_lbl)
        status_row.addWidget(self._retry_btn)
        status_row.addStretch()
        root.addLayout(status_row)

        # ── Surah info bar
        self._surah_info = QLabel("")
        self._surah_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._surah_info.setStyleSheet(
            f"color: {th.ACCENT}; font-size: 15px; font-weight: 700; background: transparent;"
        )
        root.addWidget(self._surah_info)

        # ── Bismillah
        self._bismillah_lbl = QLabel("")
        self._bismillah_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._bismillah_lbl.setStyleSheet(
            f"font-size: 34px; color: {th.ACCENT}; "
            f"font-family: 'Amiri', 'Traditional Arabic', 'Arial'; "
            f"background: transparent; padding: 14px 0;"
        )
        root.addWidget(self._bismillah_lbl)

        # ── Verse search bar + reciter selector
        tools_row = QHBoxLayout()
        tools_row.setSpacing(8)

        self._verse_search = QLineEdit()
        self._verse_search.setPlaceholderText(t("quran_verse_search_ph"))
        self._verse_search.setMaximumWidth(260)
        self._verse_search.textChanged.connect(self._filter_verses)
        self._verse_search.setStyleSheet(
            f"QLineEdit {{ background: {th.SURFACE_2}; border: 1px solid {th.BORDER};"
            f" border-radius: 8px; color: {th.TEXT}; padding: 4px 10px; font-size: 12px; }}"
            f"QLineEdit:focus {{ border-color: {th.ACCENT_DK}; }}"
        )
        tools_row.addWidget(self._verse_search)

        self._search_result_lbl = QLabel("")
        self._search_result_lbl.setStyleSheet(
            f"font-size: 11px; color: {th.MUTED}; background: transparent;"
        )
        tools_row.addWidget(self._search_result_lbl)
        tools_row.addStretch()

        reciter_lbl = QLabel(t("quran_reciter") + ":")
        reciter_lbl.setStyleSheet(f"font-size: 12px; color: {th.MUTED}; background: transparent;")
        tools_row.addWidget(reciter_lbl)

        self._reciter_combo = QComboBox()
        self._reciter_combo.setFixedHeight(30)
        for name, edition in _RECITERS:
            self._reciter_combo.addItem(name, userData=edition)
        self._reciter_combo.currentIndexChanged.connect(
            lambda i: setattr(self, "_current_reciter", self._reciter_combo.itemData(i))
        )
        tools_row.addWidget(self._reciter_combo)

        root.addLayout(tools_row)

        # ── Content: verse area + bookmark panel side by side
        content_row = QHBoxLayout()
        content_row.setSpacing(12)

        self._verse_scroll = QScrollArea()
        self._verse_scroll.setWidgetResizable(True)
        self._verse_scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self._verse_container = QWidget()
        self._verse_container.setStyleSheet("background: transparent;")
        self._verse_layout = QVBoxLayout(self._verse_container)
        self._verse_layout.setContentsMargins(0, 0, 8, 0)
        self._verse_layout.setSpacing(6)
        self._verse_scroll.setWidget(self._verse_container)
        content_row.addWidget(self._verse_scroll, 1)

        self._bm_panel = self._build_bm_panel()
        content_row.addWidget(self._bm_panel)

        root.addLayout(content_row, 1)

    def _build_bm_panel(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("Card")
        panel.setFixedWidth(270)
        panel.setVisible(False)

        lay = QVBoxLayout(panel)
        lay.setContentsMargins(12, 14, 12, 12)
        lay.setSpacing(8)

        # Title row
        title_row = QHBoxLayout()
        lbl = QLabel("🔖  " + t("quran_bookmarks"))
        lbl.setStyleSheet(
            f"font-size: 13px; font-weight: 700; color: {th.HEADING}; background: transparent;"
        )
        title_row.addWidget(lbl, 1)

        btn_close = QPushButton("✕")
        btn_close.setFixedSize(24, 24)
        btn_close.setStyleSheet(
            f"QPushButton {{ background: transparent; border: none; "
            f"color: {th.MUTED}; font-size: 13px; font-weight: 700; }}"
            f"QPushButton:hover {{ color: {th.TEXT}; }}"
        )
        btn_close.clicked.connect(self._toggle_bm_panel)
        title_row.addWidget(btn_close)
        lay.addLayout(title_row)

        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background: {th.BORDER};")
        lay.addWidget(sep)

        # Scroll area for bookmark list
        bm_scroll = QScrollArea()
        bm_scroll.setWidgetResizable(True)
        bm_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        bm_scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        self._bm_list_container = QWidget()
        self._bm_list_container.setStyleSheet("background: transparent;")
        self._bm_list_layout = QVBoxLayout(self._bm_list_container)
        self._bm_list_layout.setContentsMargins(0, 0, 0, 0)
        self._bm_list_layout.setSpacing(6)

        bm_scroll.setWidget(self._bm_list_container)
        lay.addWidget(bm_scroll, 1)

        return panel

    # ─── bookmark panel helpers ───────────────────────────────────────────────

    def _toggle_bm_panel(self):
        self._bm_visible = not self._bm_visible
        self._bm_panel.setVisible(self._bm_visible)
        if self._bm_visible:
            self._refresh_bm_panel()
        self._update_bm_toggle_label()

    def _update_bm_toggle_label(self):
        n = len(self._bookmarks)
        label = f"🔖  {t('quran_bookmarks')}  ({n})"
        self._bm_toggle_btn.setText(label)
        active = self._bm_visible
        self._bm_toggle_btn.setStyleSheet(
            f"QPushButton {{ background: {th.ACCENT_DK if active else th.SURFACE_2}; "
            f"border: 1px solid {th.ACCENT_DK}; border-radius: 8px; "
            f"color: {'#fff' if active else th.TEXT}; font-size: 12px; padding: 0 14px; }}"
            f"QPushButton:hover {{ border-color: {th.ACCENT}; }}"
        )

    def _refresh_bm_panel(self):
        # Clear existing items
        while self._bm_list_layout.count():
            item = self._bm_list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not self._bookmarks:
            lbl = QLabel(t("quran_no_bm"))
            lbl.setStyleSheet(
                f"color: {th.MUTED}; font-size: 12px; background: transparent;"
            )
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setWordWrap(True)
            self._bm_list_layout.addWidget(lbl)
            self._bm_list_layout.addStretch()
            return

        for bm in reversed(self._bookmarks):   # newest first
            self._bm_list_layout.addWidget(self._make_bm_item(bm))
        self._bm_list_layout.addStretch()

    def _make_bm_item(self, bm: dict) -> QFrame:
        frame = QFrame()
        frame.setStyleSheet(
            f"QFrame {{ background: {th.SURFACE_2}; border: 1px solid {th.BORDER}; "
            f"border-radius: 8px; }}"
        )
        lay = QVBoxLayout(frame)
        lay.setContentsMargins(10, 8, 10, 8)
        lay.setSpacing(4)

        # Surah + ayah info
        info_lbl = QLabel(
            f"{bm['surah_name']}  ·  {t('quran_verse')} {bm['ayah']}"
        )
        info_lbl.setStyleSheet(
            f"color: {th.ACCENT}; font-size: 12px; font-weight: 700; "
            f"background: transparent; border: none;"
        )
        lay.addWidget(info_lbl)

        # Arabic preview
        if bm.get("preview"):
            prev_lbl = QLabel(bm["preview"])
            prev_lbl.setStyleSheet(
                f"color: {th.MUTED}; font-size: 11px; background: transparent; border: none;"
            )
            prev_lbl.setWordWrap(True)
            prev_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
            prev_lbl.setMaximumHeight(36)
            lay.addWidget(prev_lbl)

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(6)

        btn_open = QPushButton(t("quran_bm_open"))
        btn_open.setFixedHeight(26)
        btn_open.setObjectName("Primary")
        surah_num = bm["surah"]
        btn_open.clicked.connect(lambda _, n=surah_num: self._load_surah(n))
        btn_row.addWidget(btn_open, 1)

        btn_del = QPushButton("🗑")
        btn_del.setFixedSize(26, 26)
        btn_del.setStyleSheet(
            f"QPushButton {{ background: transparent; border: 1px solid {th.BORDER}; "
            f"border-radius: 6px; color: {th.MUTED}; font-size: 12px; }}"
            f"QPushButton:hover {{ background: {th.DANGER_BG}; border-color: #ef4444; color: #ef4444; }}"
        )
        ayah_num = bm["ayah"]
        btn_del.clicked.connect(
            lambda _, s=surah_num, a=ayah_num: self._delete_bookmark(s, a)
        )
        btn_row.addWidget(btn_del)
        lay.addLayout(btn_row)
        return frame

    def _delete_bookmark(self, surah: int, ayah: int):
        self._bookmarks = [
            b for b in self._bookmarks
            if not (b["surah"] == surah and b["ayah"] == ayah)
        ]
        self._save_bookmarks()
        self._refresh_bm_panel()
        self._update_bm_toggle_label()
        # Refresh verse button states if currently viewing this surah
        if self._current_surah == surah:
            self._refresh_verse_bm_buttons()

    def _refresh_verse_bm_buttons(self):
        for i in range(self._verse_layout.count()):
            item = self._verse_layout.itemAt(i)
            if item and item.widget():
                widget = item.widget()
                btn = widget.findChild(QPushButton, "BmBtn")
                if btn:
                    ayah = btn.property("ayah_num")
                    if ayah is not None:
                        self._update_bm_btn(btn, self._is_bookmarked(self._current_surah, ayah))

    @staticmethod
    def _update_bm_btn(btn: QPushButton, bookmarked: bool):
        if bookmarked:
            btn.setText("🔖")
            btn.setToolTip("Remove bookmark")
            btn.setStyleSheet(
                "QPushButton {"
                "  background: qlineargradient(x1:0,y1:0,x2:1,y2:1,"
                "    stop:0 rgba(251,191,36,0.30),stop:1 rgba(217,119,6,0.25));"
                "  border: 1.5px solid #fbbf24;"
                "  border-radius: 8px;"
                "  color: #fbbf24;"
                "  font-size: 15px;"
                "  padding: 0;"
                "}"
                "QPushButton:hover {"
                "  background: rgba(251,191,36,0.45);"
                "  border-color: #f59e0b;"
                "}"
            )
        else:
            btn.setText("🔖")
            btn.setToolTip("Add bookmark")
            btn.setStyleSheet(
                f"QPushButton {{"
                f"  background: transparent;"
                f"  border: 1px solid {th.BORDER};"
                f"  border-radius: 8px;"
                f"  color: {th.MUTED};"
                f"  font-size: 15px;"
                f"  padding: 0;"
                f"}}"
                f"QPushButton:hover {{"
                f"  background: rgba(251,191,36,0.10);"
                f"  border-color: #fbbf24;"
                f"  color: #fbbf24;"
                f"}}"
            )

    # ─── last-read banner ─────────────────────────────────────────────────────

    def _update_last_read_bar(self, surah_num: int):
        info = _SURAHS[surah_num - 1]
        self._last_read_lbl.setText(
            f"{t('quran_last_read')}:  {info[0]}. {info[1]}  {info[2]}"
        )
        self._last_read_frame.setVisible(True)

    # ─── surah combo ─────────────────────────────────────────────────────────

    def _populate_combo(self, filter_text: str = ""):
        self._surah_combo.blockSignals(True)
        self._surah_combo.clear()
        for num, latin, arabic, ayahs, _ in _SURAHS:
            if (filter_text.lower() in latin.lower()
                    or filter_text in arabic
                    or filter_text in str(num)):
                label = f"{num}. {latin}  {arabic}  ({ayahs} {t('quran_verse')})"
                self._surah_combo.addItem(label, userData=num)
        self._surah_combo.blockSignals(False)

    def _filter_surahs(self, text: str):
        self._populate_combo(text)

    # ─── navigation ──────────────────────────────────────────────────────────

    def _on_surah_selected(self, idx: int):
        if idx < 0:
            return
        num = self._surah_combo.itemData(idx)
        if num and num != self._current_surah:
            self._load_surah(num)

    def _prev_surah(self):
        if self._current_surah > 1:
            self._load_surah(self._current_surah - 1)

    def _next_surah(self):
        if self._current_surah < 114:
            self._load_surah(self._current_surah + 1)

    def _sync_combo(self, surah_num: int):
        for i in range(self._surah_combo.count()):
            if self._surah_combo.itemData(i) == surah_num:
                self._surah_combo.blockSignals(True)
                self._surah_combo.setCurrentIndex(i)
                self._surah_combo.blockSignals(False)
                break

    # ─── load ─────────────────────────────────────────────────────────────────

    def _load_surah(self, num: int, force: bool = False):
        self._current_surah = num
        self._sync_combo(num)
        self._clear_verses()
        self._bismillah_lbl.setText("")
        self._status_lbl.setText(t("quran_loading"))
        self._status_lbl.show()
        self._retry_btn.hide()

        info = _SURAHS[num - 1]
        self._surah_info.setText(
            f"{info[0]}. {info[1]}  ·  {info[2]}  ·  {info[3]} {t('quran_verse')}"
        )

        # Save state and update last-read bar
        self._write_state(num)
        self._update_last_read_bar(num)

        threading.Thread(
            target=self._fetch_thread, args=(num, force), daemon=True
        ).start()

    def _fetch_thread(self, num: int, force: bool):
        lang       = get_language()
        tr_edition = _TR_EDITIONS.get(lang, "en.sahih")
        cache_path = _CACHE_DIR / f"{num}_{lang}.json"

        if not force and cache_path.exists():
            try:
                data   = json.loads(cache_path.read_text(encoding="utf-8"))
                arabic = data["arabic"]
                trans  = data["trans"]
                self._sig.loaded.emit(arabic, trans, True)
                return
            except Exception:
                pass

        try:
            import requests
            url = _API_BASE.format(n=num, tr=tr_edition)
            r = requests.get(url, timeout=15)
            r.raise_for_status()
            body      = r.json()
            editions  = body["data"]
            arabic_ed = next((e for e in editions if "uthmani" in e["edition"]["identifier"]), None)
            trans_ed  = next((e for e in editions if e["edition"]["identifier"] == tr_edition), None)
            if not arabic_ed or not trans_ed:
                self._sig.error.emit(t("quran_offline"))
                return

            arabic = [a["text"] for a in arabic_ed["ayahs"]]
            trans  = [a["text"] for a in trans_ed["ayahs"]]

            try:
                _CACHE_DIR.mkdir(parents=True, exist_ok=True)
                cache_path.write_text(
                    json.dumps({"arabic": arabic, "trans": trans}, ensure_ascii=False),
                    encoding="utf-8",
                )
            except Exception:
                pass

            self._sig.loaded.emit(arabic, trans, False)
        except Exception:
            self._sig.error.emit(t("quran_offline"))

    # ─── display ─────────────────────────────────────────────────────────────

    def _on_loaded(self, arabic: list, indo: list, from_cache: bool):
        self._status_lbl.hide()
        self._retry_btn.hide()
        self._cache_lbl.setText(t("quran_cached") if from_cache else "")
        self._clear_verses()

        # Stop any playing audio
        self._player.stop()
        self._playing_btn = None

        # Clear verse search
        self._verse_search.blockSignals(True)
        self._verse_search.clear()
        self._verse_search.blockSignals(False)
        self._search_result_lbl.setText("")

        info = _SURAHS[self._current_surah - 1]
        self._bismillah_lbl.setText(t("quran_bismillah") if info[4] else "")

        lang = get_language()
        self._verse_widgets.clear()
        for i, (ar, tr) in enumerate(zip(arabic, indo), start=1):
            widget = self._make_verse_widget(i, ar, tr, lang, self._current_surah)
            self._verse_layout.addWidget(widget)
            self._verse_widgets.append((i, widget, tr))

        self._verse_layout.addStretch()
        self._verse_scroll.verticalScrollBar().setValue(0)

    def _on_error(self, msg: str):
        self._status_lbl.setText(msg)
        self._status_lbl.show()
        self._retry_btn.show()
        self._cache_lbl.setText("")

    def _clear_verses(self):
        self._verse_widgets.clear()
        while self._verse_layout.count():
            item = self._verse_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    # ─── verse search ─────────────────────────────────────────────────────────

    def _filter_verses(self, text: str):
        text = text.strip().lower()
        if not text:
            for _, w, _ in self._verse_widgets:
                w.setVisible(True)
            self._search_result_lbl.setText("")
            return
        count = 0
        for _, w, tr in self._verse_widgets:
            match = text in tr.lower()
            w.setVisible(match)
            if match:
                count += 1
        if count:
            self._search_result_lbl.setText(t("quran_search_results", count))
        else:
            self._search_result_lbl.setText(t("quran_search_none"))

    # ─── audio ────────────────────────────────────────────────────────────────

    def _play_verse(self, surah: int, ayah: int, btn: QPushButton):
        # Stop currently playing if same button
        if self._playing_btn is btn:
            self._player.stop()
            btn.setText("▶")
            self._playing_btn = None
            return

        # Reset previous button
        if self._playing_btn is not None:
            self._playing_btn.setText("▶")

        global_num = _GLOBAL_OFFSET[surah - 1] + ayah - 1
        edition    = self._current_reciter
        cache_file = _AUDIO_CACHE_DIR / edition / f"{global_num}.mp3"

        self._playing_btn = btn
        btn.setText(t("quran_audio_loading"))

        if cache_file.exists():
            self._on_audio_ready(str(cache_file), btn)
        else:
            url = _CDN_AUDIO.format(edition=edition, num=global_num)
            threading.Thread(
                target=self._download_audio,
                args=(url, cache_file, btn),
                daemon=True,
            ).start()

    def _download_audio(self, url: str, cache_file: Path, btn: QPushButton):
        try:
            import urllib.request
            cache_file.parent.mkdir(parents=True, exist_ok=True)
            urllib.request.urlretrieve(url, str(cache_file))
            self._audio_sig.ready.emit(str(cache_file), btn)
        except Exception:
            self._audio_sig.error.emit(btn)

    def _on_audio_ready(self, path: str, btn: QPushButton):
        if self._playing_btn is not btn:
            return  # user switched away
        self._player.setSource(QUrl.fromLocalFile(path))
        self._player.play()
        btn.setText("⏹")
        self._player.playbackStateChanged.connect(
            lambda state, b=btn: self._on_playback_changed(state, b)
        )

    def _on_audio_error(self, btn: QPushButton):
        if self._playing_btn is btn:
            btn.setText(t("quran_audio_error"))
            self._playing_btn = None

    def _on_playback_changed(self, state, btn: QPushButton):
        from PyQt6.QtMultimedia import QMediaPlayer as _MP
        if state == _MP.PlaybackState.StoppedState:
            try:
                if btn and self._playing_btn is btn:
                    btn.setText("▶")
                    self._playing_btn = None
            except RuntimeError:
                pass
            try:
                self._player.playbackStateChanged.disconnect()
            except Exception:
                pass

    def _make_verse_widget(self, num: int, arabic: str, translation: str,
                           lang: str, surah: int) -> QFrame:
        frame = QFrame()
        frame.setStyleSheet(
            f"QFrame {{ background: {'transparent' if num % 2 == 0 else th.SURFACE}; "
            f"border-radius: 8px; margin: 1px 0; }}"
        )
        lay = QVBoxLayout(frame)
        lay.setContentsMargins(16, 16, 20, 14)
        lay.setSpacing(10)

        # ── Arabic row: [badge at left = end of RTL] [arabic text] [bookmark]
        ar_row = QHBoxLayout()
        ar_row.setSpacing(0)

        # Verse number badge at LEFT (= end of Arabic verse, RTL)
        badge = VerseNumberBadge(num)
        ar_row.addWidget(badge, 0, Qt.AlignmentFlag.AlignVCenter)
        ar_row.addSpacing(18)

        # Arabic text (fills, right-aligned = reads from right)
        ar_lbl = QLabel(arabic)
        ar_lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        ar_lbl.setWordWrap(True)
        ar_lbl.setStyleSheet(
            f"font-size: 28px; line-height: 2.2; color: {th.HEADING}; "
            f"font-family: 'Amiri', 'Traditional Arabic', 'Arial Unicode MS', 'Arial'; "
            f"background: transparent; padding: 4px 0;"
        )
        ar_row.addWidget(ar_lbl, 1)
        ar_row.addSpacing(12)

        # Bookmark button at right
        bm_btn = QPushButton("🔖")
        bm_btn.setObjectName("BmBtn")
        bm_btn.setFixedSize(36, 32)
        bm_btn.setProperty("ayah_num", num)
        bookmarked = self._is_bookmarked(surah, num)
        self._update_bm_btn(bm_btn, bookmarked)
        bm_btn.clicked.connect(
            lambda _, s=surah, a=num, p=arabic, b=bm_btn:
                self._toggle_bookmark(s, a, p, b)
        )
        ar_row.addWidget(bm_btn, 0, Qt.AlignmentFlag.AlignVCenter)
        ar_row.addSpacing(4)

        # Audio play button
        play_btn = QPushButton("▶")
        play_btn.setFixedSize(32, 32)
        play_btn.setStyleSheet(
            f"QPushButton {{ background: transparent; border: 1px solid {th.BORDER};"
            f" border-radius: 8px; color: {th.ACCENT}; font-size: 13px; }}"
            f"QPushButton:hover {{ background: {th.ACCENT_DK}22; border-color: {th.ACCENT_DK}; }}"
        )
        play_btn.clicked.connect(
            lambda _, s=surah, a=num, b=play_btn: self._play_verse(s, a, b)
        )
        ar_row.addWidget(play_btn, 0, Qt.AlignmentFlag.AlignVCenter)
        lay.addLayout(ar_row)

        # ── Translation (indented to align with Arabic text, not badge)
        tr_lbl = QLabel(translation)
        tr_lbl.setWordWrap(True)
        tr_lbl.setContentsMargins(58, 0, 48, 0)   # 40px badge + 18px gap | 36px btn + 12px gap
        tr_lbl.setStyleSheet(
            f"font-size: 13px; color: {th.MUTED}; background: transparent; "
            f"padding: 2px 0; line-height: 1.6;"
        )
        lay.addWidget(tr_lbl)

        return frame

    def refresh(self):
        pass
