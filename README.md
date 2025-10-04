# Template Project TikTok Bot (Python + Playwright)

Repository ini adalah sebuah template siap pakai untuk membangun bot TikTok menggunakan Python dan Playwright. Tujuannya adalah menyediakan fondasi yang kokoh, modular, dan mudah dikembangkan, lengkap dengan fitur-fitur penting seperti manajemen sesi, interaksi "mirip manusia", dan integrasi solver captcha.

## Fitur Utama

- **Browser Automation**: Menggunakan **Playwright** untuk mengontrol browser secara non-headless (terlihat), yang penting untuk login awal dan debugging.
- **Anti-Deteksi Bawaan**: Terintegrasi dengan **`playwright-stealth`** untuk secara otomatis menyamarkan jejak bot dari deteksi.
- **Manajemen Sesi**: Menyimpan dan memuat sesi (cookies & local storage) per akun, mengurangi kebutuhan untuk login berulang kali.
- **Humanizer Module**: Modul untuk mensimulasikan interaksi manusia, seperti delay acak, gerakan mouse, pola scroll, dan pengetikan yang natural.
- **Captcha Solver Modular**: Dilengkapi dengan adapter captcha, termasuk solver dummy untuk development dan contoh integrasi ke layanan pihak ketiga (mis. 2Captcha).
- **Konfigurasi Mudah**: Pengaturan dikelola melalui file `.env`.
- **Logging**: Logging terstruktur ke konsol dan file.
- **Struktur Proyek Jelas**: Kode diorganisir ke dalam modul-modul yang logis (`bot`, `scripts`, `tests`).
- **Contoh Implementasi**: Termasuk contoh skrip untuk menjalankan alur kerja umum (like, follow, comment).
- **Testing**: Unit test dasar untuk modul-modul kritis.
- **CI/CD**: Workflow GitHub Actions dasar untuk menjalankan tes secara otomatis.

## Persyaratan

- **Python 3.11+**
- **pip** (Python package installer)

## 1. Instalasi & Setup

**Langkah 1: Kloning Repository**
```bash
git clone <URL_REPOSITORY_INI>
cd TikTokBot
```

**Langkah 2: Buat dan Aktifkan Virtual Environment (Sangat Direkomendasikan)**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

**Langkah 3: Install Dependensi Python**
Proyek ini menggunakan `pyproject.toml` untuk manajemen dependensi.
```bash
pip install -e ".[dev]"
```
Perintah di atas akan menginstall semua dependensi yang dibutuhkan untuk development, termasuk `pytest` dan `playwright-stealth`.

**Langkah 4: Install Browser Playwright**
Playwright memerlukan browser khusus untuk bekerja. Perintah ini akan mengunduh browser yang diperlukan (Chromium secara default).
```bash
playwright install --with-deps
```

**Langkah 5: Konfigurasi Environment**
Salin file contoh `.env.example` menjadi `.env`. File ini adalah tempat Anda menyimpan konfigurasi sensitif.
```bash
# Windows
copy .env.example .env

# macOS / Linux
cp .env.example .env
```
Kemudian, buka file `.env` dan sesuaikan nilainya:
- `HEADLESS=false` (Biarkan `false` untuk login pertama kali).
- `PROXY_URL=` (Isi jika Anda ingin menggunakan proxy).
- `CAPTCHA_API_KEY=` (Isi jika Anda menggunakan layanan seperti 2Captcha).

## 2. Cara Menjalankan Bot

Template ini menyediakan dua cara utama untuk menjalankan bot.

### Opsi A: Menjalankan Alur Kerja Lengkap (Direkomendasikan)
Skrip `run_example.py` dirancang untuk menjalankan alur kerja yang telah ditentukan: login (jika perlu), menyukai 1 postingan, mengikuti 1 pengguna, dan berkomentar di 1 postingan.

**Perintah:**
```bash
python scripts/run_example.py --account <nama_akun>
```
- Ganti `<nama_akun>` dengan ID unik untuk sesi Anda (misalnya, `user_utama` atau `testing123`). Ini akan digunakan untuk membuat file sesi seperti `sessions/user_utama.json`.

**Pada Eksekusi Pertama:**
1. Browser akan terbuka dan mengarah ke halaman login TikTok.
2. Di konsol, Anda akan diminta untuk **login secara manual** di jendela browser.
3. Setelah berhasil login, kembali ke konsol dan **tekan Enter**.
4. Bot akan menyimpan sesi Anda dan kemudian melanjutkan untuk melakukan aksi (like, follow, comment).

**Pada Eksekusi Berikutnya:**
Bot akan mencoba memuat sesi yang tersimpan. Jika berhasil, ia akan langsung melakukan aksi tanpa perlu login lagi.

### Opsi B: Menjalankan Entrypoint Utama (Untuk Debugging)
File `main.py` adalah entrypoint yang lebih sederhana, biasanya hanya untuk login dan melakukan satu aksi.
```bash
python -m bot.main --account <nama_akun>
```

## 3. Struktur Proyek

```
TikTokBot/
├─ bot/                  # Modul inti bot
│  ├─ actions.py         # Fungsi aksi (like, follow, comment)
│  ├─ captcha_adapter.py # Logika untuk menyelesaikan captcha
│  ├─ config.py          # Membaca konfigurasi dari .env
│  ├─ humanizer.py       # Membuat interaksi "mirip manusia"
│  ├─ logger.py          # Konfigurasi logging
│  ├─ main.py            # Entrypoint utama bot
│  ├─ playwright_manager.py # Mengelola Playwright & browser
│  └─ session_manager.py # Menyimpan & memuat sesi
├─ scripts/              # Skrip untuk menjalankan bot
│  └─ run_example.py     # Contoh alur kerja lengkap
├─ tests/                # Unit tests
├─ .github/workflows/    # CI/CD (GitHub Actions)
├─ .env.example          # Contoh file konfigurasi
├─ .gitignore            # File yang diabaikan oleh Git
├─ pyproject.toml        # Dependensi dan metadata proyek
└─ README.md             # Dokumentasi ini
```

## 4. Catatan Penting: Anti-Bot, Etika, dan Keterbatasan

- **Risiko**: Menggunakan bot untuk mengotomatisasi interaksi di platform sosial **melanggar Ketentuan Layanan (ToS)** mereka. Akun Anda berisiko **diblokir atau dihapus secara permanen**. Gunakan dengan risiko Anda sendiri.
- **Etika**: Template ini disediakan untuk tujuan edukasi dan eksperimen. **Jangan gunakan untuk spam**, pelecehan, atau aktivitas jahat lainnya.
- **Deteksi Bot**: TikTok memiliki mekanisme deteksi bot yang canggih. Template ini secara default sudah terintegrasi dengan `playwright-stealth` untuk menyamarkan properti browser yang umum digunakan untuk deteksi. Namun, ini tidak menjamin keamanan 100%. Deteksi masih dapat menargetkan:
  - **IP Address**: Gunakan proxy berkualitas tinggi (residensial) untuk mengurangi jejak.
  - **Fingerprinting Tingkat Lanjut**: `playwright-stealth` menutupi banyak hal, tetapi situs canggih mungkin menggunakan teknik fingerprinting lain (mis. kanvas, WebGL).
  - **Pola Perilaku**: Hindari melakukan terlalu banyak aksi dalam waktu singkat. Gunakan `MAX_ACTIONS_PER_HOUR` dan jeda acak.

## 5. Langkah Lanjutan & Pengembangan

Template ini adalah titik awal. Untuk membangun bot yang lebih tangguh, pertimbangkan:
- **Fingerprint Spoofing Lanjutan**: `playwright-stealth` sudah terpasang. Untuk keamanan lebih, riset dan terapkan konfigurasi atau library tambahan untuk memodifikasi sidik jari kanvas, WebGL, dan audio.
- **Jadwal Acak**: Jalankan bot pada waktu yang tidak terduga, bukan setiap jam pada menit yang sama.
- **Manajemen Antrian (Queue)**: Untuk mengelola banyak akun atau tugas, gunakan sistem antrian seperti Celery atau RQ.
- **Monitoring & Alerting**: Siapkan sistem untuk memberi tahu Anda jika bot gagal login atau menghadapi captcha.
- **Penanganan Error yang Lebih Baik**: Perluas blok `try...except` untuk menangani lebih banyak skenario kegagalan (misalnya, elemen UI berubah).