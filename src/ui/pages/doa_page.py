"""Daily Duas page — authentic supplications from shahih hadith."""
from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QFrame, QScrollArea, QTabWidget)

from .. import theme as th
from ...i18n import t, get_language


# ─── Dua data ────────────────────────────────────────────────────────────────
# Each entry: arabic, translit, meaning_id, meaning_en, occasion_id, occasion_en, ref

_DAILY = [
    {
        "occasion_id": "Doa Masuk Kamar Mandi / WC",
        "occasion_en": "Entering the Toilet",
        "arabic":  "اللَّهُمَّ إِنِّي أَعُوذُ بِكَ مِنَ الْخُبُثِ وَالْخَبَائِثِ",
        "translit": "Allāhumma innī a'ūdzu bika minal-khubutsi wal-khabā'its",
        "meaning_id": "Ya Allah, aku berlindung kepada-Mu dari setan laki-laki dan setan perempuan.",
        "meaning_en": "O Allah, I seek refuge with You from the male and female evil jinn.",
        "ref": "HR. Bukhari no. 142 & Muslim no. 375 · Anas bin Malik RA",
    },
    {
        "occasion_id": "Doa Keluar Kamar Mandi / WC",
        "occasion_en": "Leaving the Toilet",
        "arabic":  "غُفْرَانَكَ",
        "translit": "Ghufrānaka",
        "meaning_id": "Aku memohon ampunan-Mu (ya Allah).",
        "meaning_en": "I seek Your forgiveness (O Allah).",
        "ref": "HR. Abu Dawud no. 30, Tirmidhi no. 7, Ibn Majah no. 300 · Aisyah RA",
    },
    {
        "occasion_id": "Doa Sebelum Makan",
        "occasion_en": "Before Eating",
        "arabic":  "بِسْمِ اللّٰهِ",
        "translit": "Bismillāh",
        "meaning_id": "Dengan nama Allah.",
        "meaning_en": "In the name of Allah.",
        "ref": "HR. Bukhari no. 5376 & Muslim no. 2022 · Umar bin Abi Salamah RA",
    },
    {
        "occasion_id": "Doa Jika Lupa Baca Bismillah Saat Makan",
        "occasion_en": "If Bismillah Was Forgotten Before Eating",
        "arabic":  "بِسْمِ اللّٰهِ أَوَّلَهُ وَآخِرَهُ",
        "translit": "Bismillāhi awwalahu wa ākhirahu",
        "meaning_id": "Dengan nama Allah dari awal hingga akhirnya.",
        "meaning_en": "In the name of Allah, at its beginning and at its end.",
        "ref": "HR. Abu Dawud no. 3767 & Tirmidhi no. 1858 · Aisyah RA",
    },
    {
        "occasion_id": "Doa Setelah Makan",
        "occasion_en": "After Eating",
        "arabic": (
            "اَلْحَمْدُ لِلّٰهِ الَّذِي أَطْعَمَنِي هٰذَا وَرَزَقَنِيهِ"
            " مِنْ غَيْرِ حَوْلٍ مِنِّي وَلَا قُوَّةٍ"
        ),
        "translit": (
            "Alḥamdulillāhil-ladzī aṭ'amanī hādzā wa razaqanīhi"
            " min ghairi ḥaulin minnī wa lā quwwah"
        ),
        "meaning_id": (
            "Segala puji bagi Allah yang telah memberi makan ini kepadaku"
            " dan menganugerahkannya tanpa daya dan upayaku."
        ),
        "meaning_en": (
            "Praise be to Allah who fed me this and provided it for me"
            " without any power or strength from me."
        ),
        "ref": "HR. Abu Dawud no. 4023 & Tirmidhi no. 3458 (Hasan) · Mu'adz bin Anas RA",
    },
    {
        "occasion_id": "Doa Memakai Pakaian",
        "occasion_en": "When Getting Dressed",
        "arabic": (
            "اَلْحَمْدُ لِلّٰهِ الَّذِي كَسَانِي هٰذَا وَرَزَقَنِيهِ"
            " مِنْ غَيْرِ حَوْلٍ مِنِّي وَلَا قُوَّةٍ"
        ),
        "translit": (
            "Alḥamdulillāhil-ladzī kasānī hādzā wa razaqanīhi"
            " min ghairi ḥaulin minnī wa lā quwwah"
        ),
        "meaning_id": (
            "Segala puji bagi Allah yang telah memakaikan pakaian ini kepadaku"
            " dan menganugerahkannya tanpa daya dan upayaku."
        ),
        "meaning_en": (
            "Praise be to Allah who clothed me with this and provided it for me"
            " without any power or strength from me."
        ),
        "ref": "HR. Abu Dawud no. 4023 & Tirmidhi no. 3458 (Hasan) · Mu'adz bin Anas RA",
    },
    {
        "occasion_id": "Doa Melihat Cermin",
        "occasion_en": "When Looking in the Mirror",
        "arabic": "اَللّٰهُمَّ كَمَا حَسَّنْتَ خَلْقِي فَحَسِّنْ خُلُقِي",
        "translit": "Allāhumma kamā ḥassanta khalqī fa-ḥassin khuluqī",
        "meaning_id": "Ya Allah, sebagaimana Engkau telah memperindah rupaku, maka perindahkanlah akhlakku.",
        "meaning_en": "O Allah, just as You have made my form beautiful, make my character beautiful too.",
        "ref": "HR. Ahmad no. 3834 (Hasan lighairihi) · Ibn Mas'ud RA",
    },
]

_SLEEP = [
    {
        "occasion_id": "Doa Sebelum Tidur",
        "occasion_en": "Before Sleeping",
        "arabic": "بِاسْمِكَ اللّٰهُمَّ أَمُوتُ وَأَحْيَا",
        "translit": "Bismika Allāhumma amūtu wa aḥyā",
        "meaning_id": "Dengan nama-Mu ya Allah, aku mati dan aku hidup.",
        "meaning_en": "In Your name, O Allah, I die and I live.",
        "ref": "HR. Bukhari no. 6324 · Hudzaifah bin Al-Yaman RA",
    },
    {
        "occasion_id": "Doa Tambahan Sebelum Tidur",
        "occasion_en": "Additional Supplication Before Sleep",
        "arabic": (
            "اَللّٰهُمَّ أَسْلَمْتُ نَفْسِي إِلَيْكَ، وَفَوَّضْتُ أَمْرِي إِلَيْكَ،"
            " وَوَجَّهْتُ وَجْهِي إِلَيْكَ، وَأَلْجَأْتُ ظَهْرِي إِلَيْكَ،"
            " رَغْبَةً وَرَهْبَةً إِلَيْكَ، لَا مَلْجَأَ وَلَا مَنْجَا مِنْكَ إِلَّا إِلَيْكَ،"
            " آمَنْتُ بِكِتَابِكَ الَّذِي أَنْزَلْتَ، وَبِنَبِيِّكَ الَّذِي أَرْسَلْتَ"
        ),
        "translit": (
            "Allāhumma aslamtu nafsī ilayk, wa fawwaḍtu amrī ilayk,"
            " wa wajjahtu wajhī ilayk, wa alja'tu ẓahrī ilayk,"
            " raghbatan wa rahbatan ilayk, lā malja'a wa lā manjā minka illā ilayk,"
            " āmantu bi-kitābikal-ladzī anzalta wa bi-nabiyyikal-ladzī arsalt"
        ),
        "meaning_id": (
            "Ya Allah, aku menyerahkan diriku kepada-Mu, menyerahkan urusanku kepada-Mu,"
            " menghadapkan wajahku kepada-Mu, bersandar kepada-Mu dengan penuh harap dan takut."
            " Tidak ada tempat berlindung dan tidak ada keselamatan dari-Mu kecuali kepada-Mu."
            " Aku beriman kepada kitab-Mu yang Engkau turunkan, dan Nabi-Mu yang Engkau utus."
        ),
        "meaning_en": (
            "O Allah, I surrender myself to You, entrust my affairs to You,"
            " turn my face to You, and rely on You with hope and fear."
            " There is no refuge nor escape from You except to You."
            " I believe in Your Book which You revealed and Your Prophet whom You sent."
        ),
        "ref": "HR. Bukhari no. 247 & Muslim no. 2710 · Al-Barra' bin 'Azib RA",
    },
    {
        "occasion_id": "Doa Bangun Tidur",
        "occasion_en": "Upon Waking Up",
        "arabic": (
            "اَلْحَمْدُ لِلّٰهِ الَّذِي أَحْيَانَا بَعْدَ مَا أَمَاتَنَا"
            " وَإِلَيْهِ النُّشُورُ"
        ),
        "translit": (
            "Alḥamdulillāhil-ladzī aḥyānā ba'da mā amātanā"
            " wa ilaihin-nushūr"
        ),
        "meaning_id": (
            "Segala puji bagi Allah yang telah menghidupkan kami setelah mematikan kami,"
            " dan kepada-Nya lah kami dikembalikan."
        ),
        "meaning_en": (
            "Praise be to Allah who gave us life after causing us to die,"
            " and to Him is the resurrection."
        ),
        "ref": "HR. Bukhari no. 6312 · Hudzaifah bin Al-Yaman RA",
    },
]

_HOME = [
    {
        "occasion_id": "Doa Keluar Rumah",
        "occasion_en": "When Leaving Home",
        "arabic": (
            "بِسْمِ اللّٰهِ، تَوَكَّلْتُ عَلَى اللّٰهِ،"
            " لَا حَوْلَ وَلَا قُوَّةَ إِلَّا بِاللّٰهِ"
        ),
        "translit": (
            "Bismillāh, tawakkaltu 'alallāh,"
            " lā ḥaula wa lā quwwata illā billāh"
        ),
        "meaning_id": (
            "Dengan nama Allah, aku bertawakkal kepada Allah."
            " Tidak ada daya dan upaya kecuali dengan pertolongan Allah."
        ),
        "meaning_en": (
            "In the name of Allah, I rely upon Allah."
            " There is no power and no strength except with Allah."
        ),
        "ref": "HR. Abu Dawud no. 5095 & Tirmidhi no. 3426 (Shahih) · Anas bin Malik RA",
    },
    {
        "occasion_id": "Doa Masuk Rumah",
        "occasion_en": "When Entering Home",
        "arabic": (
            "بِسْمِ اللّٰهِ وَلَجْنَا، وَبِسْمِ اللّٰهِ خَرَجْنَا،"
            " وَعَلَى اللّٰهِ رَبِّنَا تَوَكَّلْنَا"
        ),
        "translit": (
            "Bismillāhi walajanā, wa bismillāhi kharajnā,"
            " wa 'alallāhi rabbanā tawakkalnā"
        ),
        "meaning_id": (
            "Dengan nama Allah kami masuk, dan dengan nama Allah kami keluar,"
            " serta hanya kepada Allah Tuhan kami kami bertawakkal."
        ),
        "meaning_en": (
            "In the name of Allah we enter, and in the name of Allah we leave,"
            " and upon Allah our Lord we rely."
        ),
        "ref": "HR. Abu Dawud no. 5096 (Hasan) · Abu Malik al-Asy'ari RA",
    },
    {
        "occasion_id": "Doa Masuk Masjid",
        "occasion_en": "Entering the Mosque",
        "arabic": "اَللّٰهُمَّ افْتَحْ لِي أَبْوَابَ رَحْمَتِكَ",
        "translit": "Allāhumma iftaḥ lī abwāba raḥmatika",
        "meaning_id": "Ya Allah, bukakanlah untukku pintu-pintu rahmat-Mu.",
        "meaning_en": "O Allah, open for me the doors of Your mercy.",
        "ref": "HR. Muslim no. 713 & Abu Dawud no. 465 · Abu Humaid / Abu Usayd RA",
    },
    {
        "occasion_id": "Doa Keluar Masjid",
        "occasion_en": "Leaving the Mosque",
        "arabic": "اَللّٰهُمَّ إِنِّي أَسْأَلُكَ مِنْ فَضْلِكَ",
        "translit": "Allāhumma innī as'aluka min faḍlik",
        "meaning_id": "Ya Allah, sesungguhnya aku memohon kepada-Mu dari karunia-Mu.",
        "meaning_en": "O Allah, I ask You from Your bounty.",
        "ref": "HR. Muslim no. 713 & Ibn Majah no. 772 · Abu Humaid / Abu Usayd RA",
    },
]

_TRAVEL = [
    {
        "occasion_id": "Doa Naik Kendaraan",
        "occasion_en": "When Riding a Vehicle",
        "arabic": (
            "سُبْحَانَ الَّذِي سَخَّرَ لَنَا هٰذَا وَمَا كُنَّا لَهُ مُقْرِنِينَ،"
            " وَإِنَّا إِلَى رَبِّنَا لَمُنْقَلِبُونَ"
        ),
        "translit": (
            "Subḥānal-ladzī sakhkhara lanā hādzā wa mā kunnā lahu muqrinīn,"
            " wa innā ilā rabbinā lamunqalibūn"
        ),
        "meaning_id": (
            "Maha Suci Dzat yang telah menundukkan kendaraan ini untuk kami,"
            " padahal kami sebelumnya tidak mampu menguasainya."
            " Dan sesungguhnya kami pasti kembali kepada Tuhan kami."
        ),
        "meaning_en": (
            "Glory be to the One who has subjected this for us,"
            " though we were not able to have mastered it."
            " And surely to our Lord we are returning."
        ),
        "ref": "HR. Muslim no. 1342 · Ali bin Abi Thalib RA (berdasarkan QS. Az-Zukhruf: 13–14)",
    },
    {
        "occasion_id": "Doa Memulai Perjalanan (Safar)",
        "occasion_en": "Supplication at the Start of a Journey",
        "arabic": (
            "اَللّٰهُ أَكْبَرُ، اَللّٰهُ أَكْبَرُ، اَللّٰهُ أَكْبَرُ،"
            " سُبْحَانَ الَّذِي سَخَّرَ لَنَا هٰذَا وَمَا كُنَّا لَهُ مُقْرِنِينَ،"
            " وَإِنَّا إِلَى رَبِّنَا لَمُنْقَلِبُونَ،"
            " اَللّٰهُمَّ إِنَّا نَسْأَلُكَ فِي سَفَرِنَا هٰذَا الْبِرَّ وَالتَّقْوَى،"
            " وَمِنَ الْعَمَلِ مَا تَرْضَى،"
            " اَللّٰهُمَّ هَوِّنْ عَلَيْنَا سَفَرَنَا هٰذَا وَاطْوِ عَنَّا بُعْدَهُ،"
            " اَللّٰهُمَّ أَنْتَ الصَّاحِبُ فِي السَّفَرِ وَالْخَلِيفَةُ فِي الْأَهْلِ"
        ),
        "translit": (
            "Allāhu Akbar (×3), Subḥānal-ladzī sakhkhara lanā hādzā..., wa innā ilā rabbinā lamunqalibūn,"
            " Allāhumma innā nas'aluka fī safarinā hādzal-birra wat-taqwā,"
            " wa minal-'amali mā tarḍā,"
            " Allāhumma hawwin 'alaynā safaranā hādzā waṭwi 'annā bu'dahu,"
            " Allāhumma antas-ṣāḥibu fis-safari wal-khalīfatu fil-ahl"
        ),
        "meaning_id": (
            "Allah Maha Besar (3×). Maha Suci Dzat yang menundukkan kendaraan ini..., kami kembali kepada Tuhan kami."
            " Ya Allah, kami memohon kepada-Mu dalam perjalanan ini kebaikan dan ketakwaan,"
            " dan amalan yang Engkau ridhai."
            " Ya Allah, mudahkanlah perjalanan kami ini dan dekatkanlah jaraknya."
            " Ya Allah, Engkaulah yang menemani dalam perjalanan dan yang menggantikan (menjaga) keluarga."
        ),
        "meaning_en": (
            "Allah is the Greatest (×3). Glory be to the One who subjected this for us..., to our Lord we return."
            " O Allah, we ask You during this journey for righteousness, piety,"
            " and deeds that please You."
            " O Allah, make this journey easy for us and shorten its distance."
            " O Allah, You are the Companion during travel and the Guardian of the family."
        ),
        "ref": "HR. Muslim no. 1342 · Abdullah bin Umar RA",
    },
]


# ─── Page ────────────────────────────────────────────────────────────────────

class DoaPage(QWidget):
    def __init__(self, main_win):
        super().__init__()
        self._win = main_win
        self._build()

    # ─── build ──────────────────────────────────────────────────────────────

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 20, 28, 20)
        root.setSpacing(14)

        # Header
        hdr = QHBoxLayout()
        lbl = QLabel(t("doa_title"))
        lbl.setObjectName("H1")
        hdr.addWidget(lbl)
        hdr.addStretch()
        sub = QLabel(t("doa_subtitle"))
        sub.setObjectName("Muted")
        hdr.addWidget(sub)
        root.addLayout(hdr)

        # Tabs
        tabs = QTabWidget()
        tabs.addTab(self._make_tab(_DAILY),  t("doa_tab_daily"))
        tabs.addTab(self._make_tab(_SLEEP),  t("doa_tab_sleep"))
        tabs.addTab(self._make_tab(_HOME),   t("doa_tab_home"))
        tabs.addTab(self._make_tab(_TRAVEL), t("doa_tab_travel"))
        root.addWidget(tabs, 1)

    def _make_tab(self, dataset: list[dict]) -> QWidget:
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
            vbox.addWidget(self._make_card(item, lang))

        vbox.addStretch()
        scroll.setWidget(container)
        return scroll

    def _make_card(self, item: dict, lang: str) -> QFrame:
        card = QFrame()
        card.setObjectName("Card")
        lay = QVBoxLayout(card)
        lay.setContentsMargins(20, 16, 20, 18)
        lay.setSpacing(8)

        # Occasion label (chip style)
        occasion = item["occasion_id"] if lang == "id" else item["occasion_en"]
        occ_lbl = QLabel(occasion)
        occ_lbl.setStyleSheet(
            f"font-size: 12px; font-weight: 700; color: {th.ACCENT_DK};"
            f" background: transparent; text-transform: uppercase; letter-spacing: 0.5px;"
        )
        lay.addWidget(occ_lbl)

        # Separator
        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background: {th.BORDER};")
        lay.addWidget(sep)

        # Arabic
        ar = QLabel(item["arabic"])
        ar.setStyleSheet(
            f"font-size: 22px; color: {th.ACCENT}; background: transparent;"
            f" font-family: 'Traditional Arabic', 'Scheherazade New', 'Amiri', serif;"
            f" line-height: 2.0; padding: 6px 0;"
        )
        ar.setAlignment(Qt.AlignmentFlag.AlignRight)
        ar.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        ar.setWordWrap(True)
        lay.addWidget(ar)

        # Transliteration
        tr_lbl = QLabel(f"<i>{item['translit']}</i>")
        tr_lbl.setStyleSheet(f"font-size: 12px; color: {th.MUTED}; background: transparent;")
        tr_lbl.setWordWrap(True)
        tr_lbl.setTextFormat(Qt.TextFormat.RichText)
        lay.addWidget(tr_lbl)

        # Meaning
        meaning = item["meaning_id"] if lang == "id" else item["meaning_en"]
        m_lbl = QLabel(f'<b>{t("doa_meaning")}</b> {meaning}')
        m_lbl.setStyleSheet(f"font-size: 13px; color: {th.TEXT}; background: transparent;")
        m_lbl.setWordWrap(True)
        m_lbl.setTextFormat(Qt.TextFormat.RichText)
        lay.addWidget(m_lbl)

        # Reference
        ref_lbl = QLabel(f"📖  {item['ref']}")
        ref_lbl.setStyleSheet(
            f"font-size: 11px; font-weight: 600; color: {th.ACCENT_DK}; background: transparent;"
        )
        ref_lbl.setWordWrap(True)
        lay.addWidget(ref_lbl)

        return card

    def refresh(self):
        pass
