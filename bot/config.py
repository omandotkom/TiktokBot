import os
from dotenv import load_dotenv

# Muat variabel dari file .env di root proyek
load_dotenv()

class Config:
    """
    Kelas untuk mengelola konfigurasi dari environment variables.
    """
    # --- Konfigurasi Playwright ---
    PLAYWRIGHT_BROWSER: str = os.getenv("PLAYWRIGHT_BROWSER", "chromium")
    HEADLESS: bool = os.getenv("HEADLESS", "false").lower() in ("true", "1", "t")
    SESSION_DIR: str = os.getenv("SESSION_DIR", "./sessions")

    # --- Konfigurasi Proxy ---
    # Contoh: "http://user:pass@host:port"
    PROXY_URL: str | None = os.getenv("PROXY_URL")

    # --- Konfigurasi Captcha Solver ---
    # Ganti dengan API key dari layanan captcha Anda (mis. 2Captcha, Anti-Captcha)
    CAPTCHA_API_KEY: str | None = os.getenv("CAPTCHA_API_KEY")

    # --- Konfigurasi Bot ---
    MAX_ACTIONS_PER_HOUR: int = int(os.getenv("MAX_ACTIONS_PER_HOUR", "30"))
    TIKTOK_LOGIN_URL: str = "https://www.tiktok.com/login"

    # --- Contoh URL untuk Aksi ---
    # URL ini bisa diganti melalui argumen CLI atau file konfigurasi lain
    EXAMPLE_POST_URL_TO_LIKE: str = os.getenv("EXAMPLE_POST_URL_TO_LIKE", "https://www.tiktok.com/@rairairaissa/video/7359338392157130017")
    EXAMPLE_USER_URL_TO_FOLLOW: str = os.getenv("EXAMPLE_USER_URL_TO_FOLLOW", "https://www.tiktok.com/@rairairaissa")
    EXAMPLE_POST_URL_TO_COMMENT: str = os.getenv("EXAMPLE_POST_URL_TO_COMMENT", "https://www.tiktok.com/@rairairaissa/video/7359338392157130017")

# Buat instance tunggal dari konfigurasi untuk diimpor di modul lain
config = Config()

# Pastikan direktori sesi ada
os.makedirs(config.SESSION_DIR, exist_ok=True)