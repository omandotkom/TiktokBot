import json
import os
from playwright.async_api import BrowserContext

from bot.config import config
from bot.logger import log

class SessionManager:
    """
    Mengelola penyimpanan dan pemuatan sesi (cookies & local storage).
    """
    def _get_session_path(self, account_id: str) -> str:
        """Mendapatkan path file sesi untuk sebuah akun."""
        return os.path.join(config.SESSION_DIR, f"{account_id}.json")

    async def save_session(self, context: BrowserContext, account_id: str) -> None:
        """
        Menyimpan cookies dan local storage dari konteks ke file JSON.

        Args:
            context: Konteks browser yang sesi-nya akan disimpan.
            account_id: ID unik untuk akun.
        """
        session_path = self._get_session_path(account_id)
        log.info(f"Menyimpan sesi untuk akun '{account_id}' ke {session_path}")

        try:
            cookies = await context.cookies()

            # Ekstrak local storage. Perlu dievaluasi di dalam konteks halaman.
            # Pastikan ada halaman terbuka untuk mengekstrak local storage.
            if not context.pages:
                await context.new_page() # Buka halaman sementara jika belum ada

            page = context.pages[0]
            local_storage = await page.evaluate("() => JSON.stringify(window.localStorage)")

            session_data = {
                "cookies": cookies,
                "localStorage": json.loads(local_storage)
            }

            os.makedirs(os.path.dirname(session_path), exist_ok=True)
            with open(session_path, "w", encoding="utf-8") as f:
                json.dump(session_data, f, indent=4)

            log.info(f"Sesi untuk akun '{account_id}' berhasil disimpan.")

        except Exception as e:
            log.error(f"Gagal menyimpan sesi untuk akun '{account_id}': {e}")

    async def load_session(self, context: BrowserContext, account_id: str) -> bool:
        """
        Memuat cookies dan local storage dari file JSON ke konteks.

        Args:
            context: Konteks browser tujuan.
            account_id: ID unik akun yang sesi-nya akan dimuat.

        Returns:
            True jika sesi berhasil dimuat, False jika tidak.
        """
        session_path = self._get_session_path(account_id)

        if not os.path.exists(session_path):
            log.warning(f"File sesi tidak ditemukan untuk akun '{account_id}'. Lewati pemuatan.")
            return False

        log.info(f"Memuat sesi untuk akun '{account_id}' dari {session_path}")
        try:
            with open(session_path, "r", encoding="utf-8") as f:
                session_data = json.load(f)

            # Muat cookies
            if "cookies" in session_data:
                await context.add_cookies(session_data["cookies"])
                log.info("Cookies berhasil dimuat.")

            # Muat local storage
            if "localStorage" in session_data:
                # Local storage harus di-set melalui skrip yang dievaluasi di halaman
                local_storage_script = ""
                for key, value in session_data["localStorage"].items():
                    # Escape backticks, backslashes, and dollar signs for template literal
                    escaped_value = value.replace('\\', '\\\\').replace('`', '\\`').replace('$', '\\$')
                    local_storage_script += f"localStorage.setItem(`{key}`, `{escaped_value}`);"

                await context.add_init_script(local_storage_script)
                log.info("Local storage akan dimuat pada halaman baru.")

            log.info(f"Sesi untuk akun '{account_id}' berhasil dikonfigurasi untuk dimuat.")
            return True

        except Exception as e:
            log.error(f"Gagal memuat sesi untuk akun '{account_id}': {e}")
            return False

# Instance tunggal untuk digunakan di seluruh aplikasi
session_manager = SessionManager()