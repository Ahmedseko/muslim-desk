"""Dua & Dzikir page — post-prayer dhikr counter, morning/evening adhkar."""
from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QFrame, QPushButton, QScrollArea, QTabWidget,
                              QSizePolicy, QGridLayout)

from .. import theme as th
from ...i18n import t, get_language


# ─── Dhikr data ──────────────────────────────────────────────────────────────

_POST_PRAYER = [
    {
        "arabic": "سُبْحَانَ اللّٰهِ",
        "translit": "SubḥānAllāh",
        "meaning_id": "Maha Suci Allah",
        "meaning_en": "Glory be to Allah",
        "count": 33,
    },
    {
        "arabic": "اَلْحَمْدُ لِلّٰهِ",
        "translit": "Alḥamdulillāh",
        "meaning_id": "Segala puji bagi Allah",
        "meaning_en": "All praise is for Allah",
        "count": 33,
    },
    {
        "arabic": "اَللّٰهُ أَكْبَرُ",
        "translit": "Allāhu Akbar",
        "meaning_id": "Allah Maha Besar",
        "meaning_en": "Allah is the Greatest",
        "count": 33,
    },
    {
        "arabic": "لَا إِلٰهَ إِلَّا اللّٰهُ وَحْدَهُ لَا شَرِيكَ لَهُ، لَهُ الْمُلْكُ وَلَهُ الْحَمْدُ وَهُوَ عَلَى كُلِّ شَيْءٍ قَدِيرٌ",
        "translit": "Lā ilāha illAllāh waḥdahu lā sharīka lah, lahul-mulku wa lahul-ḥamdu wa huwa ʿalā kulli shay'in qadīr",
        "meaning_id": "Tiada Tuhan selain Allah, tiada sekutu bagi-Nya. Bagi-Nya kerajaan dan segala pujian. Dia Mahakuasa atas segala sesuatu.",
        "meaning_en": "None has the right to be worshipped but Allah alone, Who has no partner. His is the dominion, His is the praise, and He is able to do all things.",
        "count": 1,
    },
]

_MORNING = [
    {
        "arabic": "أَعُوذُ بِاللّٰهِ مِنَ الشَّيْطَانِ الرَّجِيمِ\n﴿اللّٰهُ لَا إِلٰهَ إِلَّا هُوَ الْحَيُّ الْقَيُّومُ...﴾",
        "translit": "Ayat Kursi (QS 2:255)",
        "meaning_id": "Ayat Kursi — perlindungan dari gangguan setan",
        "meaning_en": "Ayat al-Kursi — protection from shaytan",
        "count": 1,
    },
    {
        "arabic": "أَصْبَحْنَا وَأَصْبَحَ الْمُلْكُ لِلّٰهِ، وَالْحَمْدُ لِلّٰهِ، لَا إِلٰهَ إِلَّا اللّٰهُ وَحْدَهُ لَا شَرِيكَ لَهُ",
        "translit": "Aṣbaḥnā wa aṣbaḥal-mulku lillāh...",
        "meaning_id": "Kami berpagi hari dan kerajaan hanyalah milik Allah...",
        "meaning_en": "We have entered the morning and the dominion belongs to Allah...",
        "count": 1,
    },
    {
        "arabic": "سُبْحَانَ اللّٰهِ وَبِحَمْدِهِ",
        "translit": "SubḥānAllāhi wa biḥamdih",
        "meaning_id": "Maha Suci Allah dan segala puji bagi-Nya",
        "meaning_en": "Glory be to Allah and His is the praise",
        "count": 100,
    },
    {
        "arabic": "أَسْتَغْفِرُ اللّٰهَ",
        "translit": "Astaghfirullāh",
        "meaning_id": "Aku memohon ampunan kepada Allah",
        "meaning_en": "I seek forgiveness from Allah",
        "count": 100,
    },
    {
        "arabic": "لَا إِلٰهَ إِلَّا اللّٰهُ وَحْدَهُ لَا شَرِيكَ لَهُ، لَهُ الْمُلْكُ وَلَهُ الْحَمْدُ وَهُوَ عَلَى كُلِّ شَيْءٍ قَدِيرٌ",
        "translit": "Lā ilāha illAllāh waḥdahu...",
        "meaning_id": "Tiada Tuhan selain Allah, tiada sekutu bagi-Nya...",
        "meaning_en": "None has the right to be worshipped but Allah alone...",
        "count": 10,
    },
]

_EVENING = [
    {
        "arabic": "أَمْسَيْنَا وَأَمْسَى الْمُلْكُ لِلّٰهِ، وَالْحَمْدُ لِلّٰهِ، لَا إِلٰهَ إِلَّا اللّٰهُ وَحْدَهُ لَا شَرِيكَ لَهُ",
        "translit": "Amsaynā wa amsyal-mulku lillāh...",
        "meaning_id": "Kami bersore hari dan kerajaan hanyalah milik Allah...",
        "meaning_en": "We have entered the evening and the dominion belongs to Allah...",
        "count": 1,
    },
    {
        "arabic": "سُبْحَانَ اللّٰهِ وَبِحَمْدِهِ",
        "translit": "SubḥānAllāhi wa biḥamdih",
        "meaning_id": "Maha Suci Allah dan segala puji bagi-Nya",
        "meaning_en": "Glory be to Allah and His is the praise",
        "count": 100,
    },
    {
        "arabic": "أَعُوذُ بِكَلِمَاتِ اللّٰهِ التَّامَّاتِ مِنْ شَرِّ مَا خَلَقَ",
        "translit": "A'ūdhu bi kalimātillāhit-tāmmāti min sharri mā khalaq",
        "meaning_id": "Aku berlindung dengan kalimat-kalimat Allah yang sempurna dari kejahatan makhluk-Nya",
        "meaning_en": "I seek refuge in the Perfect Words of Allah from the evil of what He has created",
        "count": 3,
    },
    {
        "arabic": "اَللّٰهُمَّ بِكَ أَمْسَيْنَا وَبِكَ أَصْبَحْنَا وَبِكَ نَحْيَا وَبِكَ نَمُوتُ وَإِلَيْكَ الْمَصِيرُ",
        "translit": "Allāhumma bika amsaynā wa bika aṣbaḥnā...",
        "meaning_id": "Ya Allah, dengan-Mu kami bersore hari, dengan-Mu kami berpagi hari...",
        "meaning_en": "O Allah, by You we enter the evening, by You we enter the morning...",
        "count": 1,
    },
]


# ─── Page ────────────────────────────────────────────────────────────────────

class DzikirPage(QWidget):
    def __init__(self, main_win):
        super().__init__()
        self._win = main_win
        self._counters: list[int] = []
        self._counter_lbls: list[QLabel] = []
        self._counter_btns: list[QPushButton] = []
        self._active_set: list[dict] = []
        self._build()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 20, 28, 20)
        root.setSpacing(16)

        # Header
        header = QHBoxLayout()
        lbl = QLabel(t("dzikir_title"))
        lbl.setObjectName("H1")
        header.addWidget(lbl)
        header.addStretch()
        btn_reset = QPushButton(t("dzikir_reset"))
        btn_reset.setFixedHeight(34)
        btn_reset.clicked.connect(self._reset_all)
        header.addWidget(btn_reset)
        root.addLayout(header)

        # Tabs
        tabs = QTabWidget()
        tabs.addTab(self._make_tab(_POST_PRAYER, 0), t("dzikir_tab_post"))
        tabs.addTab(self._make_tab(_MORNING, 1), t("dzikir_tab_morn"))
        tabs.addTab(self._make_tab(_EVENING, 2), t("dzikir_tab_eve"))
        tabs.currentChanged.connect(self._on_tab_changed)
        root.addWidget(tabs, 1)
        self._tabs = tabs
        self._on_tab_changed(0)

    def _make_tab(self, dataset: list[dict], tab_idx: int) -> QWidget:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        container = QWidget()
        container.setStyleSheet("background: transparent;")
        vbox = QVBoxLayout(container)
        vbox.setContentsMargins(0, 8, 0, 8)
        vbox.setSpacing(12)

        lang = get_language()
        for item in dataset:
            card = self._make_dhikr_card(item, lang, tab_idx)
            vbox.addWidget(card)

        vbox.addStretch()
        scroll.setWidget(container)
        return scroll

    def _make_dhikr_card(self, item: dict, lang: str, tab_idx: int) -> QFrame:
        card = QFrame()
        card.setObjectName("Card")
        lay = QVBoxLayout(card)
        lay.setContentsMargins(20, 16, 20, 16)
        lay.setSpacing(8)

        # Arabic text
        arabic = QLabel(item["arabic"])
        arabic.setAlignment(Qt.AlignmentFlag.AlignRight)
        arabic.setStyleSheet(
            f"font-size: 28px; color: {th.HEADING}; "
            f"font-family: 'Amiri', 'Traditional Arabic', 'Arial Unicode MS', 'Arial'; "
            f"background: transparent; line-height: 2.2; padding: 6px 0;"
        )
        arabic.setWordWrap(True)
        lay.addWidget(arabic)

        # Transliteration
        translit = QLabel(item["translit"])
        translit.setStyleSheet(
            f"font-size: 13px; color: {th.MUTED}; font-style: italic; background: transparent;"
        )
        translit.setWordWrap(True)
        lay.addWidget(translit)

        # Meaning
        meaning_key = "meaning_id" if lang == "id" else "meaning_en"
        meaning = item.get(meaning_key, item.get("meaning_id", ""))
        if meaning:
            lbl_meaning = QLabel(f"{t('dzikir_meaning')} {meaning}")
            lbl_meaning.setStyleSheet(f"font-size: 13px; color: {th.TEXT}; background: transparent;")
            lbl_meaning.setWordWrap(True)
            lay.addWidget(lbl_meaning)

        # Separator
        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background: {th.BORDER};")
        lay.addWidget(sep)

        # Counter row
        count_row = QHBoxLayout()
        count_row.setSpacing(12)

        target = item["count"]
        idx = len(self._counters)
        self._counters.append(0)

        counter_lbl = QLabel(f"0 / {target}")
        counter_lbl.setStyleSheet(
            f"font-size: 18px; font-weight: 700; color: {th.HEADING}; background: transparent;"
        )
        self._counter_lbls.append(counter_lbl)

        btn = QPushButton(f"0 / {target}   {t('dzikir_tap')}" if target > 1 else t("dzikir_tap"))
        btn.setObjectName("DzikirBtn")
        btn.setMinimumHeight(56)
        btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._counter_btns.append(btn)

        def _tap(i=idx, t_val=target, b=btn, _item=item):
            self._counters[i] = min(self._counters[i] + 1, t_val)
            c = self._counters[i]
            if c >= t_val:
                b.setObjectName("DzikirDone")
                b.setText(t("dzikir_complete"))
            else:
                b.setObjectName("DzikirBtn")
                b.setText(f"{c} / {t_val}")
            b.style().unpolish(b)
            b.style().polish(b)

        btn.clicked.connect(_tap)

        if target == 1:
            btn.setText(t("dzikir_tap"))
        else:
            btn.setText(f"0 / {target}")

        count_row.addWidget(btn, 1)
        lay.addLayout(count_row)

        return card

    def _on_tab_changed(self, idx: int):
        sets = [_POST_PRAYER, _MORNING, _EVENING]
        if idx < len(sets):
            self._active_set = sets[idx]

    def _reset_all(self):
        for i in range(len(self._counters)):
            self._counters[i] = 0
        # Reset button appearances
        post_len = len(_POST_PRAYER)
        morn_len = len(_MORNING)
        for i, btn in enumerate(self._counter_btns):
            if i < post_len:
                target = _POST_PRAYER[i]["count"]
            elif i < post_len + morn_len:
                target = _MORNING[i - post_len]["count"]
            else:
                target = _EVENING[i - post_len - morn_len]["count"]

            btn.setObjectName("DzikirBtn")
            btn.setText(f"0 / {target}" if target > 1 else t("dzikir_tap"))
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    def refresh(self):
        pass
