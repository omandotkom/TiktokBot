import asyncio
import argparse
import random

from bot.playwright_manager import playwright_manager
from bot.session_manager import session_manager
from bot.config import config
from bot.logger import log
from bot.actions import action_manager
from bot.humanizer import humanizer

async def run_bot_flow(account_id: str):
    """
    Menjalankan alur kerja bot yang lebih lengkap: login, like, follow, comment.
    """
    log.info(f"Memulai alur kerja bot untuk akun: {account_id}")

    await playwright_manager.start()

    try:
        context = await playwright_manager.create_context(account_id)
        session_loaded = await session_manager.load_session(context, account_id)
        page = await playwright_manager.new_page(context)

        if not session_loaded:
            log.info("Sesi tidak ditemukan. Harap login secara manual di browser.")
            await page.goto(config.TIKTOK_LOGIN_URL, wait_until="networkidle", timeout=90000)

            print("\n" + "="*50)
            print("PERHATIAN: Silakan login ke akun TikTok Anda.")
            print("Setelah login, bot akan menyimpan sesi Anda.")
            print("Tekan Enter di konsol ini setelah Anda berhasil login...")
            print("="*50)
            input()

            await session_manager.save_session(context, account_id)
            log.info("Sesi baru berhasil disimpan.")
        else:
            log.info("Sesi berhasil dimuat. Memverifikasi status login...")
            await page.goto("https://www.tiktok.com/foryou", wait_until="networkidle")
            # Cek sederhana untuk memastikan login berhasil
            try:
                await page.wait_for_selector("a[href*='/profile']", timeout=15000)
                log.info("Login berhasil diverifikasi.")
            except Exception:
                log.error("Verifikasi login gagal. Sesi mungkin kedaluwarsa. Hapus file sesi dan coba lagi.")
                return

        # --- ALUR KERJA AKSI ---
        log.info("Memulai alur kerja aksi (like, follow, comment).")

        # 1. Aksi Like
        log.info("--- Langkah 1: Menyukai Postingan ---")
        like_target_url = config.EXAMPLE_POST_URL_TO_LIKE
        await action_manager.auto_like(page, like_target_url)
        await humanizer.sleep_random(5, 10) # Jeda antar aksi besar

        # 2. Aksi Follow
        log.info("--- Langkah 2: Mengikuti Pengguna ---")
        follow_target_url = config.EXAMPLE_USER_URL_TO_FOLLOW
        await action_manager.auto_follow(page, follow_target_url)
        await humanizer.sleep_random(5, 10)

        # 3. Aksi Comment
        log.info("--- Langkah 3: Berkomentar di Postingan ---")
        comment_target_url = config.EXAMPLE_POST_URL_TO_COMMENT

        # Contoh daftar komentar acak
        comments = [
            "Wow, keren banget! 🔥",
            "Suka banget sama kontennya! 👍",
            "This is amazing!",
            "Keep it up! 😊",
            "Nice one!",
        ]
        comment_to_post = random.choice(comments)
        await action_manager.auto_comment(page, comment_target_url, comment_to_post)

        log.info("Alur kerja bot telah selesai.")

    except Exception as e:
        log.error(f"Terjadi kesalahan pada alur kerja bot: {e}", exc_info=True)
    finally:
        await playwright_manager.close()
        log.info("Bot berhenti.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Contoh skrip untuk menjalankan alur kerja TikTok Bot.")
    parser.add_argument(
        "--account",
        type=str,
        default="demo_user",
        help="ID Akun untuk menjalankan bot.",
    )
    args = parser.parse_args()

    asyncio.run(run_bot_flow(args.account))