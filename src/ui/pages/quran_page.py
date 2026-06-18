"""Al-Quran reader page — surah list + verse display with API + local cache."""
from __future__ import annotations

import json
import threading
from pathlib import Path

from PyQt6.QtCore import Qt, pyqtSignal, QObject
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QFrame, QPushButton, QScrollArea, QComboBox,
                              QLineEdit, QSizePolicy, QProgressBar, QSplitter)

from .. import theme as th
from ...i18n import t, get_language

_CACHE_DIR = Path.home() / ".muslim_desk" / "quran"

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

_API_URL = "https://api.alquran.cloud/v1/surah/{n}/editions/quran-uthmani,id.indonesian"


class _QuranSignal(QObject):
    loaded = pyqtSignal(list, list, bool)  # arabic_ayahs, id_ayahs, from_cache
    error  = pyqtSignal(str)


class QuranPage(QWidget):
    def __init__(self, main_win):
        super().__init__()
        self._win = main_win
        self._current_surah = 1
        self._sig = _QuranSignal()
        self._sig.loaded.connect(self._on_loaded)
        self._sig.error.connect(self._on_error)
        self._build()
        self._load_surah(1)

    # ─── build ────────────────────────────────────────────────────────────────

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 20, 28, 20)
        root.setSpacing(12)

        # Header row
        header = QHBoxLayout()
        lbl_title = QLabel(t("quran_title"))
        lbl_title.setObjectName("H1")
        header.addWidget(lbl_title)
        header.addStretch()
        self._cache_lbl = QLabel("")
        self._cache_lbl.setStyleSheet(f"color: {th.MUTED}; font-size: 11px; background: transparent;")
        header.addWidget(self._cache_lbl)
        root.addLayout(header)

        # Search + surah selector row
        sel_row = QHBoxLayout()
        sel_row.setSpacing(8)

        lbl_sel = QLabel(t("quran_select"))
        lbl_sel.setStyleSheet(f"color: {th.MUTED}; background: transparent;")
        sel_row.addWidget(lbl_sel)

        self._search_box = QLineEdit()
        self._search_box.setPlaceholderText(t("quran_search_ph"))
        self._search_box.setMaximumWidth(200)
        self._search_box.textChanged.connect(self._filter_surahs)
        sel_row.addWidget(self._search_box)

        self._surah_combo = QComboBox()
        self._surah_combo.setMinimumWidth(260)
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

        # Status / loading bar
        self._status_lbl = QLabel(t("quran_loading"))
        self._status_lbl.setStyleSheet(f"color: {th.MUTED}; font-size: 12px; background: transparent;")
        self._status_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._retry_btn = QPushButton(t("quran_retry"))
        self._retry_btn.setFixedHeight(30)
        self._retry_btn.hide()
        self._retry_btn.clicked.connect(lambda: self._load_surah(self._current_surah, force=True))

        status_row = QHBoxLayout()
        status_row.addStretch()
        status_row.addWidget(self._status_lbl)
        status_row.addWidget(self._retry_btn)
        status_row.addStretch()
        root.addLayout(status_row)

        # Surah info bar
        self._surah_info = QLabel("")
        self._surah_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._surah_info.setStyleSheet(
            f"color: {th.ACCENT}; font-size: 13px; font-weight: 700; "
            f"background: transparent;"
        )
        root.addWidget(self._surah_info)

        # Bismillah
        self._bismillah_lbl = QLabel("")
        self._bismillah_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._bismillah_lbl.setStyleSheet(
            f"font-size: 24px; color: {th.ACCENT}; "
            f"font-family: 'Amiri', 'Traditional Arabic', 'Arial'; "
            f"background: transparent; padding: 10px 0;"
        )
        root.addWidget(self._bismillah_lbl)

        # Verse scroll area
        self._verse_scroll = QScrollArea()
        self._verse_scroll.setWidgetResizable(True)
        self._verse_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self._verse_container = QWidget()
        self._verse_container.setStyleSheet("background: transparent;")
        self._verse_layout = QVBoxLayout(self._verse_container)
        self._verse_layout.setContentsMargins(0, 0, 8, 0)
        self._verse_layout.setSpacing(2)

        self._verse_scroll.setWidget(self._verse_container)
        root.addWidget(self._verse_scroll, 1)

    def _populate_combo(self, filter_text: str = ""):
        self._surah_combo.blockSignals(True)
        self._surah_combo.clear()
        for num, latin, arabic, ayahs, _ in _SURAHS:
            label = f"{num}. {latin}  {arabic}  ({ayahs} {t('quran_verse')})"
            if filter_text.lower() in latin.lower() or filter_text in arabic or filter_text in str(num):
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

        # surah info
        info = _SURAHS[num - 1]
        self._surah_info.setText(
            f"{info[0]}. {info[1]}  ·  {info[2]}  ·  {info[3]} {t('quran_verse')}"
        )

        threading.Thread(
            target=self._fetch_thread, args=(num, force), daemon=True
        ).start()

    def _fetch_thread(self, num: int, force: bool):
        cache_path = _CACHE_DIR / f"{num}.json"
        if not force and cache_path.exists():
            try:
                data = json.loads(cache_path.read_text(encoding="utf-8"))
                arabic = data["arabic"]
                indo   = data["indo"]
                self._sig.loaded.emit(arabic, indo, True)
                return
            except Exception:
                pass

        try:
            import requests
            url = _API_URL.format(n=num)
            r = requests.get(url, timeout=15)
            r.raise_for_status()
            body = r.json()
            editions = body["data"]
            arabic_ed = next((e for e in editions if "uthmani" in e["edition"]["identifier"]), None)
            indo_ed   = next((e for e in editions if "indonesian" in e["edition"]["identifier"]), None)
            if not arabic_ed or not indo_ed:
                self._sig.error.emit(t("quran_offline"))
                return

            arabic = [a["text"] for a in arabic_ed["ayahs"]]
            indo   = [a["text"] for a in indo_ed["ayahs"]]

            # Cache
            try:
                _CACHE_DIR.mkdir(parents=True, exist_ok=True)
                cache_path.write_text(
                    json.dumps({"arabic": arabic, "indo": indo}, ensure_ascii=False),
                    encoding="utf-8",
                )
            except Exception:
                pass

            self._sig.loaded.emit(arabic, indo, False)
        except Exception as e:
            self._sig.error.emit(t("quran_offline"))

    # ─── display ─────────────────────────────────────────────────────────────

    def _on_loaded(self, arabic: list, indo: list, from_cache: bool):
        self._status_lbl.hide()
        self._retry_btn.hide()
        self._cache_lbl.setText(t("quran_cached") if from_cache else "")
        self._clear_verses()

        # Bismillah
        info = _SURAHS[self._current_surah - 1]
        has_bismillah = info[4]
        if has_bismillah:
            self._bismillah_lbl.setText(t("quran_bismillah"))
        else:
            self._bismillah_lbl.setText("")

        lang = get_language()
        for i, (ar, tr) in enumerate(zip(arabic, indo), start=1):
            widget = self._make_verse_widget(i, ar, tr, lang)
            self._verse_layout.addWidget(widget)

        self._verse_layout.addStretch()

        # Scroll to top
        self._verse_scroll.verticalScrollBar().setValue(0)

    def _on_error(self, msg: str):
        self._status_lbl.setText(msg)
        self._status_lbl.show()
        self._retry_btn.show()
        self._cache_lbl.setText("")

    def _clear_verses(self):
        while self._verse_layout.count():
            item = self._verse_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _make_verse_widget(self, num: int, arabic: str, translation: str, lang: str) -> QFrame:
        frame = QFrame()
        frame.setObjectName("Card" if num % 2 == 0 else "")
        frame.setStyleSheet(
            f"QFrame {{ background: {'transparent' if num % 2 == 0 else th.SURFACE}; "
            f"border-radius: 8px; margin: 1px 0; }}"
        )
        lay = QVBoxLayout(frame)
        lay.setContentsMargins(16, 12, 16, 12)
        lay.setSpacing(6)

        # Verse number badge + arabic
        top_row = QHBoxLayout()

        badge = QLabel(str(num))
        badge.setFixedSize(28, 28)
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge.setStyleSheet(
            f"background: {th.SURFACE_2}; border: 1px solid {th.BORDER}; "
            f"border-radius: 14px; color: {th.MUTED}; font-size: 11px; font-weight: 700;"
        )
        top_row.addWidget(badge)
        top_row.addStretch()
        lay.addLayout(top_row)

        # Arabic
        ar_lbl = QLabel(arabic)
        ar_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
        ar_lbl.setWordWrap(True)
        ar_lbl.setStyleSheet(
            f"font-size: 20px; line-height: 2.0; color: {th.HEADING}; "
            f"font-family: 'Amiri', 'Traditional Arabic', 'Arial Unicode MS', 'Arial'; "
            f"background: transparent; padding: 4px 0;"
        )
        lay.addWidget(ar_lbl)

        # Translation
        tr_lbl = QLabel(translation)
        tr_lbl.setWordWrap(True)
        tr_lbl.setStyleSheet(
            f"font-size: 12px; color: {th.MUTED}; background: transparent; "
            f"padding: 2px 0; line-height: 1.5;"
        )
        lay.addWidget(tr_lbl)

        return frame

    def refresh(self):
        pass
