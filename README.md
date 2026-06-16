# Muslim Desk 🕌

Aplikasi jadwal sholat 5 waktu untuk **Windows 11** — berjalan di system tray, notifikasi adzan otomatis, dan tampilan yang bersih.

## Fitur

- **Jadwal sholat harian** — Subuh, Syuruq, Dzuhur, Ashar, Maghrib, Isya
- **Countdown waktu sholat berikutnya** — progress bar real-time
- **Kalender Hijriah** — tampil di dashboard
- **Notifikasi & suara adzan** — per-waktu sholat, bisa pilih file `.wav` sendiri
- **Lokasi otomatis** via IP atau cari kota manual
- **Format waktu** 12 jam / 24 jam
- **Tema gelap / terang / ikuti sistem**
- **System tray** — minimize ke tray, mulai saat startup
- **Jadwal mingguan** — tabel 7 hari ke depan

## Screenshot

> *(akan ditambahkan)*

## Instalasi (End User)

1. Download `MuslimDesk-Setup-v1.0.0.exe` dari halaman [Releases](../../releases)
2. Jalankan installer → Next → Install
3. Aplikasi otomatis berjalan setelah instalasi selesai

## Menjalankan dari Source

**Prasyarat:** Python 3.11+ dan pip

```bash
git clone https://github.com/Ahmedseko/muslim-desk.git
cd muslim-desk
pip install -r requirements.txt
python main.py
```

## Build Installer

```bash
# 1. Build executable
python -m PyInstaller muslim_desk.spec --noconfirm

# 2. Compile installer (butuh Inno Setup 6)
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer\muslim_desk.iss
```

Output: `release\MuslimDesk-Setup-v1.0.0.exe`

## Teknologi

| Komponen | Library / Sumber |
|---|---|
| GUI | PyQt6 |
| Algoritma Sholat | [PrayTimes.org](http://praytimes.org) |
| Kalender Hijriah | Umm al-Qura / Tabular |
| Geolokasi | ip-api.com |
| Installer | Inno Setup 6 |

## Metode Hisab

Mendukung: Kemenag, MWL, ISNA, Makkah, Egypt, Karachi, Tehran, Jafari

## Developer

**Ahmed Seko** — [@Ahmedseko](https://github.com/Ahmedseko)

## Lisensi

[MIT License](LICENSE)
