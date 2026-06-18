"""Internationalisation — Indonesian (id) and English (en)."""
from __future__ import annotations

_STRINGS: dict[str, dict[str, str]] = {
    # ── Navigation ───────────────────────────────────────────────────────────
    "nav_dashboard":  {"id": "Dashboard",   "en": "Dashboard"},
    "nav_qibla":      {"id": "Kiblat",      "en": "Qibla"},
    "nav_settings":   {"id": "Pengaturan",  "en": "Settings"},

    # ── Prayer names ─────────────────────────────────────────────────────────
    "prayer_fajr":    {"id": "Subuh",    "en": "Fajr"},
    "prayer_sunrise": {"id": "Syuruk",   "en": "Sunrise"},
    "prayer_dhuhr":   {"id": "Dzuhur",   "en": "Dhuhr"},
    "prayer_asr":     {"id": "Ashar",    "en": "Asr"},
    "prayer_maghrib": {"id": "Maghrib",  "en": "Maghrib"},
    "prayer_isha":    {"id": "Isya",     "en": "Isha"},

    # ── Dashboard labels ─────────────────────────────────────────────────────
    "dashboard_title":       {"id": "Dashboard",                        "en": "Dashboard"},
    "current_time":          {"id": "Waktu Sekarang",                   "en": "Current Time"},
    "next_prayer":           {"id": "SHOLAT BERIKUTNYA",                "en": "NEXT PRAYER"},
    "prayer_time_lbl":       {"id": "WAKTU SHOLAT",                     "en": "PRAYER TIME"},
    "countdown_lbl":         {"id": "HITUNG MUNDUR",                    "en": "COUNTDOWN"},
    "progress_lbl":          {"id": "Waktu berlalu menuju sholat berikutnya", "en": "Time elapsed to next prayer"},
    "sunrise_row":           {"id": "Syuruk (Matahari Terbit)",         "en": "Sunrise"},
    "alarm_active":          {"id": "🔔 Aktif",                         "en": "🔔 Active"},
    "alarm_inactive":        {"id": "🔕 Nonaktif",                      "en": "🔕 Inactive"},
    "tomorrow_suffix":       {"id": " (Besok)",                         "en": " (Tomorrow)"},
    "search_city_btn":       {"id": "🔍 Cari Kota",                     "en": "🔍 Search City"},
    "auto_location_btn":     {"id": "🔄 Auto Lokasi",                   "en": "🔄 Auto Location"},
    "detecting_loc":         {"id": "⌛ Mendeteksi...",                 "en": "⌛ Detecting..."},
    "loading_loc":           {"id": "📍 Memuat lokasi...",              "en": "📍 Loading location..."},
    "refresh_location_btn":  {"id": "🔄 Perbarui Lokasi",              "en": "🔄 Refresh"},
    "loc_updated":           {"id": "Lokasi diperbarui: ",              "en": "Location updated: "},
    "calc_failed":           {"id": "Gagal hitung waktu: ",             "en": "Failed to calculate: "},
    "detecting_via_ip":      {"id": "Mendeteksi lokasi via IP...",      "en": "Detecting location via IP..."},
    "tz_warning":            {"id": "Peringatan zona waktu",            "en": "Timezone warning"},
    "tz_use_system":         {"id": "Gunakan Waktu Sistem",             "en": "Use System Time"},
    "tz_dismiss":            {"id": "Abaikan",                         "en": "Dismiss"},
    "weekly_title":          {"id": "Jadwal Sholat 7 Hari Ke Depan",   "en": "7-Day Prayer Schedule"},
    "weekly_col_date":       {"id": "Hari / Tanggal",                  "en": "Day / Date"},
    "hijri_title":           {"id": "🌙  Kalender Hijriah & Puasa Sunnah", "en": "🌙  Hijri Calendar & Sunnah Fasting"},
    "ayyamul_label":         {"id": "Puasa Ayyamul Bidh bulan ini:\n", "en": "Ayyamul Bidh fasting this month:\n"},

    # ── Days ─────────────────────────────────────────────────────────────────
    "day_0": {"id": "Senin",   "en": "Monday"},
    "day_1": {"id": "Selasa",  "en": "Tuesday"},
    "day_2": {"id": "Rabu",    "en": "Wednesday"},
    "day_3": {"id": "Kamis",   "en": "Thursday"},
    "day_4": {"id": "Jum'at",  "en": "Friday"},
    "day_5": {"id": "Sabtu",   "en": "Saturday"},
    "day_6": {"id": "Ahad",    "en": "Sunday"},

    "day_short_0": {"id": "Sen", "en": "Mon"},
    "day_short_1": {"id": "Sel", "en": "Tue"},
    "day_short_2": {"id": "Rab", "en": "Wed"},
    "day_short_3": {"id": "Kam", "en": "Thu"},
    "day_short_4": {"id": "Jum", "en": "Fri"},
    "day_short_5": {"id": "Sab", "en": "Sat"},
    "day_short_6": {"id": "Min", "en": "Sun"},

    # ── Months ───────────────────────────────────────────────────────────────
    "month_1":  {"id": "Januari",   "en": "January"},
    "month_2":  {"id": "Februari",  "en": "February"},
    "month_3":  {"id": "Maret",     "en": "March"},
    "month_4":  {"id": "April",     "en": "April"},
    "month_5":  {"id": "Mei",       "en": "May"},
    "month_6":  {"id": "Juni",      "en": "June"},
    "month_7":  {"id": "Juli",      "en": "July"},
    "month_8":  {"id": "Agustus",   "en": "August"},
    "month_9":  {"id": "September", "en": "September"},
    "month_10": {"id": "Oktober",   "en": "October"},
    "month_11": {"id": "November",  "en": "November"},
    "month_12": {"id": "Desember",  "en": "December"},

    "month_short_1":  {"id": "Jan", "en": "Jan"},
    "month_short_2":  {"id": "Feb", "en": "Feb"},
    "month_short_3":  {"id": "Mar", "en": "Mar"},
    "month_short_4":  {"id": "Apr", "en": "Apr"},
    "month_short_5":  {"id": "Mei", "en": "May"},
    "month_short_6":  {"id": "Jun", "en": "Jun"},
    "month_short_7":  {"id": "Jul", "en": "Jul"},
    "month_short_8":  {"id": "Agu", "en": "Aug"},
    "month_short_9":  {"id": "Sep", "en": "Sep"},
    "month_short_10": {"id": "Okt", "en": "Oct"},
    "month_short_11": {"id": "Nov", "en": "Nov"},
    "month_short_12": {"id": "Des", "en": "Dec"},

    # ── Notification dialog ───────────────────────────────────────────────────
    "notif_title":        {"id": "Waktu Sholat",       "en": "Prayer Time"},
    "notif_its_time":     {"id": "Waktunya Sholat",    "en": "Time to pray"},
    "notif_remind":       {"id": "⏰ Ingatkan {} menit", "en": "⏰ Remind in {} min"},
    "notif_close":        {"id": "Tutup",               "en": "Close"},
    "tray_prayer_time":   {"id": "Waktunya Sholat",     "en": "Prayer Time"},
    "tray_at":            {"id": "Pukul",               "en": "At"},
    "tray_show":          {"id": "Tampilkan",            "en": "Show"},
    "tray_quit":          {"id": "Keluar",               "en": "Quit"},
    "tray_bg_msg":        {"id": "Aplikasi berjalan di latar belakang.", "en": "App is running in the background."},

    # ── Settings page ─────────────────────────────────────────────────────────
    "settings_title":     {"id": "Pengaturan",           "en": "Settings"},
    "btn_save":           {"id": "💾 Simpan Pengaturan", "en": "💾 Save Settings"},
    "saved_ok":           {"id": "✅ Pengaturan berhasil disimpan.", "en": "✅ Settings saved."},

    "sec_appearance":     {"id": "🎨  Tampilan",                   "en": "🎨  Appearance"},
    "lbl_theme":          {"id": "Tema",                           "en": "Theme"},
    "theme_dark":         {"id": "Gelap (Dark)",                   "en": "Dark"},
    "theme_light":        {"id": "Terang (Light)",                 "en": "Light"},
    "theme_system":       {"id": "Ikuti Sistem",                   "en": "Follow System"},
    "lbl_time_format":    {"id": "Format Waktu",                   "en": "Time Format"},
    "fmt_24h":            {"id": "24 Jam  (13:06)",                "en": "24h  (13:06)"},
    "fmt_12h":            {"id": "12 Jam  (1:06 PM)",              "en": "12h  (1:06 PM)"},
    "lbl_language":       {"id": "Bahasa / Language",              "en": "Language"},
    "hint_theme":         {"id": "Perubahan tema diterapkan setelah disimpan.", "en": "Theme change applied after saving."},

    "sec_calc":           {"id": "🕌  Metode Perhitungan",         "en": "🕌  Calculation Method"},
    "lbl_method":         {"id": "Metode Hisab",                   "en": "Calculation Method"},
    "lbl_asr":            {"id": "Metode Ashar",                   "en": "Asr Calculation"},
    "asr_shafii":         {"id": "Syafi'i / Maliki / Hanbali (faktor 1)", "en": "Shafi'i / Maliki / Hanbali (factor 1)"},
    "asr_hanafi":         {"id": "Hanafi (faktor 2)",              "en": "Hanafi (factor 2)"},

    "sec_location":       {"id": "📍  Lokasi",                     "en": "📍  Location"},
    "auto_loc_cb":        {"id": "Deteksi lokasi otomatis via internet", "en": "Auto-detect location via internet"},
    "lbl_lat":            {"id": "Lintang (°)",                    "en": "Latitude (°)"},
    "lbl_lon":            {"id": "Bujur (°)",                      "en": "Longitude (°)"},
    "lbl_tz":             {"id": "Zona Waktu (UTC+)",              "en": "Timezone (UTC+)"},
    "lbl_alt":            {"id": "Ketinggian (mdpl)",              "en": "Altitude (m)"},
    "lbl_city":           {"id": "Nama Kota",                      "en": "City Name"},
    "lbl_country":        {"id": "Negara",                         "en": "Country"},
    "lbl_search_city":    {"id": "Cari kota / kecamatan",          "en": "Search city / district"},
    "btn_search_city":    {"id": "🔍 Cari Kota / Kecamatan",       "en": "🔍 Search City / District"},
    "hint_city":          {"id": "Gunakan 'Cari Kota' untuk menemukan kecamatan/kabupaten secara akurat.", "en": "Use 'Search City' to find your district accurately."},
    "loc_set_to":         {"id": "✅ Lokasi diset ke: ",           "en": "✅ Location set to: "},

    "sec_notif":          {"id": "🔔  Notifikasi & Alarm",         "en": "🔔  Notifications & Alarms"},
    "notif_cb":           {"id": "Aktifkan notifikasi waktu sholat", "en": "Enable prayer time notifications"},
    "sound_cb":           {"id": "Aktifkan suara adzan",           "en": "Enable adhan sound"},
    "lbl_sound_file":     {"id": "File suara (.wav)",              "en": "Sound file (.wav)"},
    "sound_placeholder":  {"id": "Kosong = suara default Windows", "en": "Empty = default Windows sound"},
    "btn_choose_file":    {"id": "Pilih File",                     "en": "Choose File"},
    "btn_clear":          {"id": "Hapus",                          "en": "Clear"},
    "lbl_reminder":       {"id": "Pengingat sebelum waktu sholat", "en": "Reminder before prayer"},
    "reminder_off":       {"id": "Tidak ada pengingat",            "en": "No reminder"},
    "reminder_5":         {"id": "5 menit sebelum",                "en": "5 minutes before"},
    "reminder_10":        {"id": "10 menit sebelum",               "en": "10 minutes before"},
    "reminder_15":        {"id": "15 menit sebelum",               "en": "15 minutes before"},
    "alarm_section_lbl":  {"id": "Alarm & Suara per Waktu Sholat", "en": "Alarm & Sound per Prayer"},
    "hint_sound":              {"id": "Centang = aktifkan alarm sholat. Kosong = gunakan suara global di atas.", "en": "Check = enable alarm. Empty = use global sound above."},
    "sound_prayer_placeholder":{"id": "(gunakan suara global / default)", "en": "(use global/default sound)"},

    "sec_window":         {"id": "🖥️  Jendela Aplikasi",          "en": "🖥️  Window"},
    "startup_cb":         {"id": "Jalankan otomatis saat Windows startup", "en": "Run automatically at Windows startup"},
    "start_min_cb":       {"id": "Mulai dalam kondisi diminimalkan (ke system tray)", "en": "Start minimized (to system tray)"},
    "tray_cb":            {"id": "Minimize ke System Tray (bukan taskbar)", "en": "Minimize to System Tray (not taskbar)"},

    "sec_about":          {"id": "ℹ️  Tentang Aplikasi",          "en": "ℹ️  About"},
    "about_desc":         {"id": "Aplikasi jadwal sholat 5 waktu untuk Windows 11.", "en": "5 daily prayer schedule app for Windows 11."},
    "about_dev":          {"id": "Developer",                      "en": "Developer"},
    "about_algo":         {"id": "Algoritma",                      "en": "Algorithm"},
    "about_hijri":        {"id": "Kalender Hijriah",               "en": "Hijri Calendar"},
    "about_geo":          {"id": "Geolokasi",                      "en": "Geolocation"},
    "about_fw":           {"id": "Framework",                      "en": "Framework"},
    "hint_theme_save":    {"id": "Perubahan tema diterapkan setelah disimpan.", "en": "Theme changes apply after saving."},

    # ── Auto-update banner ────────────────────────────────────────────────────
    "update_available": {"id": "🔔  Versi baru tersedia: v{}  —  Unduh sekarang untuk mendapatkan fitur terbaru.",
                         "en": "🔔  New version available: v{}  —  Download now to get the latest features."},
    "update_download":  {"id": "Unduh",  "en": "Download"},
    "update_later":     {"id": "Nanti",  "en": "Later"},

    # ── City search dialog ────────────────────────────────────────────────────
    "city_search_win_title":  {"id": "Cari Kota / Lokasi",         "en": "Search City / Location"},
    "city_search_title":      {"id": "🔍  Cari Kota / Lokasi",     "en": "🔍  Search City / Location"},
    "city_search_hint":       {"id": ("Ketik nama kota, kecamatan, atau tempat lalu tekan Enter.\n"
                                       "Mendukung pencarian seluruh dunia. Tips: gunakan 2–4 kata kunci."),
                               "en": ("Type a city, district, or place name and press Enter.\n"
                                       "Worldwide search supported. Tip: use 2–4 keywords.")},
    "city_search_placeholder":{"id": "Contoh: Banjarmasin  atau  London  atau  New York",
                               "en": "Example: Jakarta  or  London, UK  or  New York"},
    "city_search_btn":        {"id": "Cari",                        "en": "Search"},
    "city_search_searching":  {"id": "⌛ Mencari...",               "en": "⌛ Searching..."},
    "city_search_not_found":  {"id": "❌ Tidak ditemukan. Coba kata kunci yang berbeda.",
                               "en": "❌ Not found. Try different keywords."},
    "city_search_found":      {"id": "✅ {} hasil — klik untuk memilih, dobel klik untuk konfirmasi:",
                               "en": "✅ {} results — click to select, double-click to confirm:"},
    "btn_cancel":             {"id": "Batal",                       "en": "Cancel"},
    "city_search_select":     {"id": "Pilih Lokasi",                "en": "Select Location"},
    "lbl_timezone_short":     {"id": "Zona Waktu",                  "en": "Timezone"},
    "method_auto_set":        {"id": "✅ Metode hisab diset otomatis: {}",
                               "en": "✅ Calculation method auto-set: {}"},

    # ── Qibla page ────────────────────────────────────────────────────────────
    "qibla_title":        {"id": "Arah Kiblat",                    "en": "Qibla Direction"},
    "qibla_subtitle":     {"id": "Arah menuju Ka'bah, Masjidil Haram, Makkah Al-Mukarramah",
                           "en": "Direction to Ka'bah, Masjidil Haram, Makkah Al-Mukarramah"},
    "qibla_compass_lbl":  {"id": "Kompas Kiblat",                  "en": "Qibla Compass"},
    "qibla_from_north":   {"id": "dari Utara",                     "en": "from North"},
    "compass_north_lbl":  {"id": "● Utara (N)",                    "en": "● North (N)"},
    "compass_qibla_lbl":  {"id": "● Arah Kiblat",                  "en": "● Qibla Direction"},
    "your_location_card": {"id": "📍  Lokasi Anda",                 "en": "📍  Your Location"},
    "lbl_latitude_short": {"id": "Lintang",                        "en": "Latitude"},
    "lbl_longitude_short":{"id": "Bujur",                          "en": "Longitude"},
    "lbl_city_short":     {"id": "Kota",                           "en": "City"},
    "qibla_card_title":   {"id": "🕋  Arah Kiblat",                "en": "🕋  Qibla Direction"},
    "qibla_angle_lbl":    {"id": "Sudut dari Utara",               "en": "Angle from North"},
    "compass_dir_lbl":    {"id": "Arah Kompas",                    "en": "Compass Direction"},
    "dist_to_mecca":      {"id": "Jarak ke Makkah",                "en": "Distance to Mecca"},
    "kaaba_ref_card":     {"id": "🕌  Ka'bah (Patokan)",           "en": "🕌  Ka'bah (Reference)"},
    "kaaba_location_val": {"id": "Makkah Al-Mukarramah, Arab Saudi","en": "Makkah Al-Mukarramah, Saudi Arabia"},
    "how_to_use_card":    {"id": "📖  Cara Menggunakan di Laptop",  "en": "📖  How to Use on Laptop"},
    "qibla_static_warn":  {
        "id": ("<b>Kompas ini bersifat statis — tidak real-time.</b><br>"
               "Laptop umumnya <b>tidak memiliki sensor magnetometer</b> seperti ponsel, "
               "sehingga jarum tidak dapat berputar mengikuti arah fisik laptop. "
               "Gunakan panduan di bawah untuk menentukan arah kiblat secara akurat."),
        "en": ("<b>This compass is static — not real-time.</b><br>"
               "Laptops generally <b>have no magnetometer sensor</b> like smartphones, "
               "so the needle cannot rotate with the physical orientation of the laptop. "
               "Use the guide below to determine the qibla direction accurately."),
    },
    "qibla_steps": {
        "id": ("<b>Langkah 1</b> — Cari arah Utara terlebih dahulu.<br>"
               "Gunakan kompas HP, Google Maps, atau matahari (pagi = Timur).<br><br>"
               "<b>Langkah 2</b> — Putar badan/laptop sehingga menghadap Utara.<br><br>"
               "<b>Langkah 3</b> — Dari posisi menghadap Utara, putar badan<br>"
               "sesuai sudut kiblat yang tertera (misal: <b>292°</b> = hampir ke Barat, sedikit ke Utara).<br><br>"
               "<b>Langkah 4</b> — Arah wajah Anda sekarang = arah Kiblat. ✅<br><br>"
               "<span style='color: #8b949e; font-size: 12px;'>"
               "💡 Untuk akurasi real-time, gunakan kompas HP bersama bearing dari aplikasi ini.</span>"),
        "en": ("<b>Step 1</b> — First, find North.<br>"
               "Use your phone's compass, Google Maps, or the sun (morning = East).<br><br>"
               "<b>Step 2</b> — Rotate your body/laptop to face North.<br><br>"
               "<b>Step 3</b> — From facing North, rotate your body<br>"
               "by the qibla angle shown (e.g. <b>292°</b> = nearly West, slightly North).<br><br>"
               "<b>Step 4</b> — The direction you now face = Qibla. ✅<br><br>"
               "<span style='color: #8b949e; font-size: 12px;'>"
               "💡 For real-time accuracy, use your phone's compass with this app's bearing.</span>"),
    },

    # ── Font size (#3) ───────────────────────────────────────────────────────
    "lbl_font_size":    {"id": "Ukuran Teks",           "en": "Font Size"},
    "font_size_small":  {"id": "Kecil (12px)",           "en": "Small (12px)"},
    "font_size_med":    {"id": "Sedang (13px)",           "en": "Medium (13px)"},
    "font_size_large":  {"id": "Besar (15px)",            "en": "Large (15px)"},
    "font_size_xl":     {"id": "Sangat Besar (17px)",     "en": "Extra Large (17px)"},

    # ── Ramadan / Imsak (#2) ─────────────────────────────────────────────────
    "prayer_imsak":     {"id": "Imsak",                  "en": "Imsak"},
    "imsak_row":        {"id": "Imsak (batas sahur)",     "en": "Imsak (end of suhoor)"},
    "ramadan_badge":    {"id": "🌙 Ramadhan",             "en": "🌙 Ramadan"},
    "lbl_imsak_min":    {"id": "Imsak sebelum Subuh (menit)",  "en": "Imsak before Fajr (min)"},
    "imsak_off":        {"id": "Nonaktif (0)",            "en": "Off (0)"},

    # ── Monthly schedule (#5) ────────────────────────────────────────────────
    "schedule_7days":   {"id": "7 Hari",                 "en": "7 Days"},
    "schedule_month":   {"id": "Bulan Ini",              "en": "This Month"},

    # ── Location profiles (#6) ───────────────────────────────────────────────
    "sec_profiles":     {"id": "📌  Profil Lokasi",       "en": "📌  Location Profiles"},
    "profile_save_btn": {"id": "💾  Simpan Profil Saat Ini", "en": "💾  Save Current Profile"},
    "profile_use":      {"id": "Pakai",                  "en": "Use"},
    "profile_delete":   {"id": "Hapus",                  "en": "Delete"},
    "profile_name_lbl": {"id": "Nama profil:",            "en": "Profile name:"},
    "profile_name_ph":  {"id": "mis. Rumah / Kantor / Kampung", "en": "e.g. Home / Office / Village"},
    "profile_saved":    {"id": "✅ Profil '{}' disimpan.", "en": "✅ Profile '{}' saved."},
    "profile_applied":  {"id": "✅ Profil '{}' diterapkan.", "en": "✅ Profile '{}' applied."},
    "profile_none":     {"id": "Belum ada profil tersimpan.", "en": "No saved profiles yet."},

    # ── Toast notification (#9) ──────────────────────────────────────────────
    "lbl_toast":        {"id": "Notifikasi sistem (Windows Toast)", "en": "System notification (Windows Toast)"},
    "toast_msg":        {"id": "Waktu {} telah tiba: {}", "en": "{} time: {}"},

    # ── Navigation for new pages ─────────────────────────────────────────────
    "nav_dzikir":       {"id": "Dzikir",                 "en": "Dhikr"},
    "nav_quran":        {"id": "Quran",                  "en": "Quran"},

    # ── Dzikir page (#12) ────────────────────────────────────────────────────
    "dzikir_title":     {"id": "Dzikir & Doa",            "en": "Dhikr & Dua"},
    "dzikir_post":      {"id": "📿  Dzikir Setelah Sholat", "en": "📿  Post-Prayer Dhikr"},
    "dzikir_morning":   {"id": "🌅  Dzikir Pagi",          "en": "🌅  Morning Adhkar"},
    "dzikir_evening":   {"id": "🌙  Dzikir Petang",        "en": "🌙  Evening Adhkar"},
    "dzikir_reset":     {"id": "Reset Semua",             "en": "Reset All"},
    "dzikir_tap":       {"id": "Ketuk untuk menghitung",  "en": "Tap to count"},
    "dzikir_complete":  {"id": "✅ Selesai",               "en": "✅ Complete"},
    "dzikir_meaning":   {"id": "Artinya:",                "en": "Meaning:"},
    "dzikir_times":     {"id": "kali",                   "en": "times"},
    "dzikir_tab_post":  {"id": "Setelah Sholat",         "en": "Post-Prayer"},
    "dzikir_tab_morn":  {"id": "Pagi",                   "en": "Morning"},
    "dzikir_tab_eve":   {"id": "Petang",                 "en": "Evening"},

    # ── Quran page (#15) ─────────────────────────────────────────────────────
    "quran_title":      {"id": "Al-Quran Al-Karim",       "en": "The Holy Quran"},
    "quran_select":     {"id": "Pilih Surah:",            "en": "Select Surah:"},
    "quran_loading":    {"id": "⌛ Memuat surah...",       "en": "⌛ Loading surah..."},
    "quran_offline":    {"id": "❌ Gagal memuat. Periksa koneksi internet.", "en": "❌ Failed to load. Check internet connection."},
    "quran_cached":     {"id": "📱 Data dari cache lokal", "en": "📱 Data from local cache"},
    "quran_verse":      {"id": "Ayat",                   "en": "Verse"},
    "quran_bismillah":  {"id": "بِسْمِ اللّٰهِ الرَّحْمٰنِ الرَّحِيمِ", "en": "بِسْمِ اللّٰهِ الرَّحْمٰنِ الرَّحِيمِ"},
    "quran_prev":       {"id": "◀ Sebelumnya",           "en": "◀ Previous"},
    "quran_next":       {"id": "Berikutnya ▶",           "en": "Next ▶"},
    "quran_search_ph":  {"id": "Cari surah...",           "en": "Search surah..."},
    "quran_retry":      {"id": "🔄 Coba Lagi",            "en": "🔄 Retry"},

    # ── Compass 16-point directions ───────────────────────────────────────────
    "compass_N":   {"id": "U",   "en": "N"},
    "compass_NNE": {"id": "UTL", "en": "NNE"},
    "compass_NE":  {"id": "TL",  "en": "NE"},
    "compass_ENE": {"id": "TTL", "en": "ENE"},
    "compass_E":   {"id": "T",   "en": "E"},
    "compass_ESE": {"id": "TTG", "en": "ESE"},
    "compass_SE":  {"id": "TG",  "en": "SE"},
    "compass_SSE": {"id": "BTG", "en": "SSE"},
    "compass_S":   {"id": "S",   "en": "S"},
    "compass_SSW": {"id": "BSD", "en": "SSW"},
    "compass_SW":  {"id": "SD",  "en": "SW"},
    "compass_WSW": {"id": "BLD", "en": "WSW"},
    "compass_W":   {"id": "B",   "en": "W"},
    "compass_WNW": {"id": "BBL", "en": "WNW"},
    "compass_NW":  {"id": "BL",  "en": "NW"},
    "compass_NNW": {"id": "UBL", "en": "NNW"},
}

_lang: str = "id"
SUPPORTED = ("id", "en")


def set_language(lang: str) -> None:
    global _lang
    _lang = lang if lang in SUPPORTED else "id"


def get_language() -> str:
    return _lang


def t(key: str, *args) -> str:
    """Return translated string for current language.  args are format() positional params."""
    row = _STRINGS.get(key)
    if row is None:
        return key
    text = row.get(_lang) or row.get("id") or key
    if args:
        text = text.format(*args)
    return text


def day_name(weekday: int, short: bool = False) -> str:
    key = f"day_short_{weekday}" if short else f"day_{weekday}"
    return t(key)


def month_name(month: int, short: bool = False) -> str:
    key = f"month_short_{month}" if short else f"month_{month}"
    return t(key)


_COMPASS_KEYS = [
    "compass_N",   "compass_NNE", "compass_NE",  "compass_ENE",
    "compass_E",   "compass_ESE", "compass_SE",  "compass_SSE",
    "compass_S",   "compass_SSW", "compass_SW",  "compass_WSW",
    "compass_W",   "compass_WNW", "compass_NW",  "compass_NNW",
]


def compass_dir(bearing: float) -> str:
    """Return localised 16-point compass abbreviation."""
    return t(_COMPASS_KEYS[round(bearing / 22.5) % 16])


def prayer_name(prayer_en: str) -> str:
    """Return localised prayer name from English key."""
    _map = {
        "Fajr":    "prayer_fajr",
        "Sunrise": "prayer_sunrise",
        "Dhuhr":   "prayer_dhuhr",
        "Asr":     "prayer_asr",
        "Maghrib": "prayer_maghrib",
        "Isha":    "prayer_isha",
        "Imsak":   "prayer_imsak",
    }
    return t(_map.get(prayer_en, ""))
