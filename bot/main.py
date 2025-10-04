import asyncio
import argparse

from bot.playwright_manager import playwright_manager
from bot.session_manager import session_manager
from bot.config import config
from bot.logger import log
from bot.actions import action_manager

async def main():
    """
    Entrypoint utama untuk menjalankan bot TikTok.
    Contoh ini menunjukkan alur dasar: inisialisasi, login/load sesi, dan satu aksi.
    """
    parser = argparse.ArgumentParser(description="Template Bot TikTok dengan Playwright")
    parser.add_argument(
        "--account",
        type=str,
        default="demo",
        help="ID Akun yang akan digunakan (mis. 'user1'). Ini akan menjadi nama file sesi.",
    )
    args = parser.parse_args()
    account_id = args.account

    log.info(f"Memulai bot untuk akun: {account_id}")

    await playwright_manager.start()

    try:
        context = await playwright_manager.create_context(account_id)

        # Coba muat sesi yang ada
        session_loaded = await session_manager.load_session(context, account_id)

        page = await playwright_manager.new_page(context)

        if not session_loaded:
            log.info("Tidak ada sesi aktif. Harap login secara manual.")
            await page.goto(config.TIKTOK_LOGIN_URL, wait_until="networkidle", timeout=90000)

            print("\n" + "="*50)
            print("PERHATIAN: Silakan login ke akun TikTok Anda di jendela browser.")
            print("Setelah berhasil login, JANGAN TUTUP BROWSER.")
            print("Bot akan mencoba menyimpan sesi Anda secara otomatis.")
            print("Tekan Enter di sini setelah Anda selesai login...")
            print("="*50)
            input() # Tunggu input dari pengguna untuk melanjutkan

            # Simpan sesi setelah login manual
            await session_manager.save_session(context, account_id)
            log.info("Sesi baru telah disimpan. Silakan jalankan kembali skrip untuk melakukan aksi.")

        else:
            log.info("Sesi berhasil dimuat. Memverifikasi status login...")
            # Kunjungi halaman utama untuk memastikan sesi valid
            await page.goto("https://www.tiktok.com/foryou", wait_until="networkidle", timeout=60000)

            # Cek sederhana jika login berhasil (misalnya, dengan mencari ikon profil)
            # Selector ini mungkin perlu disesuaikan
            profile_icon_selector = "a[href*='/profile']"
            try:
                await page.wait_for_selector(profile_icon_selector, timeout=15000)
                log.info("Verifikasi login berhasil. Anda sudah masuk.")

                # --- CONTOH AKSI ---
                # Jalankan satu contoh aksi setelah login berhasil
                log.info("Menjalankan contoh aksi: Auto-Like.")
                await action_manager.auto_like(page, config.EXAMPLE_POST_URL_TO_LIKE)
                log.info("Contoh aksi selesai.")

            except Exception:
                log.error("Gagal memverifikasi login. Sesi mungkin sudah kedaluwarsa.")
                log.info("Harap hapus file sesi lama dan coba lagi untuk login ulang.")
                # Hapus file sesi yang rusak/kedaluwarsa
                import os
                session_file = os.path.join(config.SESSION_DIR, f"{account_id}.json")
                if os.path.exists(session_file):
                    os.remove(session_file)
                    log.info(f"File sesi '{session_file}' telah dihapus.")

    except Exception as e:
        log.error(f"Terjadi kesalahan fatal: {e}", exc_info=True)
    finally:
        await playwright_manager.close()
        log.info("Bot telah berhenti.")

if __name__ == "__main__":
    # Untuk menjalankan file ini secara langsung: python -m bot.main --account my_account
    asyncio.run(main())