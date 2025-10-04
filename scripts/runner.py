import argparse
import asyncio
import random
from typing import List

from playwright.async_api import BrowserContext, Page

from bot.actions import action_manager
from bot.config import config
from bot.humanizer import humanizer
from bot.logger import log
from bot.playwright_manager import playwright_manager
from bot.session_manager import session_manager

VALID_ACTIONS = ["like", "follow", "comment"]


def _choose_comment(default_text: str | None) -> str:
    if default_text:
        return default_text
    presets = [
        "Wow, keren banget!",
        "Kontennya mantap!",
        "This is amazing!",
        "Keep it up!",
        "Nice one!",
    ]
    return random.choice(presets)


async def _ensure_authenticated(account_id: str) -> tuple[BrowserContext, Page, bool]:
    context = await playwright_manager.create_context(account_id)
    session_loaded = await session_manager.load_session(context, account_id)
    page = await playwright_manager.new_page(context)

    if not session_loaded:
        log.info("Sesi tidak ditemukan. Silakan login secara manual di browser yang terbuka.")
        await page.goto(config.TIKTOK_LOGIN_URL, wait_until="networkidle", timeout=90000)

        print("\n" + "=" * 60)
        print("LOGIN MANUAL DIBUTUHKAN")
        print("1. Gunakan browser yang terbuka untuk login ke TikTok.")
        print("2. Setelah berhasil login dan halaman terbuka, kembali ke terminal.")
        print("3. Tekan Enter untuk melanjutkan dan menyimpan sesi.")
        print("=" * 60)
        input()

        await session_manager.save_session(context, account_id)
        log.info("Sesi baru tersimpan. Melanjutkan verifikasi login.")

    await page.goto("https://www.tiktok.com/foryou", wait_until="networkidle", timeout=600000)
    try:
        await page.wait_for_selector("a[href*='/@bantupedia.id']", timeout=150000)
        log.info("Login terverifikasi. Siap menjalankan aksi.")
        return context, page, True
    except Exception:
        log.error("Tidak dapat memverifikasi login. Hapus sesi dan coba lagi.")
        return context, page, False


async def run(actions: List[str], account_id: str, like_url: str, follow_url: str,
              comment_url: str, comment_text: str | None) -> None:
    await playwright_manager.start()
    try:
        context, page, authenticated = await _ensure_authenticated(account_id)
        if not authenticated:
            return

        for index, action in enumerate(actions):
            if action == "like":
                log.info("Menjalankan aksi: Like")
                await action_manager.auto_like(page, like_url)
            elif action == "follow":
                log.info("Menjalankan aksi: Follow")
                await action_manager.auto_follow(page, follow_url)
            elif action == "comment":
                log.info("Menjalankan aksi: Comment")
                comment_to_post = _choose_comment(comment_text)
                await action_manager.auto_comment(page, comment_url, comment_to_post)
            else:
                log.warning(f"Aksi tidak dikenal: {action}")

            if index < len(actions) - 1:
                await humanizer.sleep_random(5, 10)

    except Exception as exc:
        log.error(f"Terjadi kesalahan saat menjalankan runner: {exc}", exc_info=True)
    finally:
        await playwright_manager.close()
        log.info("Runner selesai.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Runner CLI untuk TikTok Bot Template."
    )
    parser.add_argument(
        "--account",
        default="demo_user",
        help="ID akun yang digunakan untuk menyimpan sesi.",
    )
    parser.add_argument(
        "--actions",
        nargs="+",
        choices=VALID_ACTIONS,
        default=VALID_ACTIONS,
        help="Daftar aksi yang akan dijalankan secara berurutan.",
    )
    parser.add_argument(
        "--like-url",
        default=config.EXAMPLE_POST_URL_TO_LIKE,
        help="URL postingan untuk aksi Like.",
    )
    parser.add_argument(
        "--follow-url",
        default=config.EXAMPLE_USER_URL_TO_FOLLOW,
        help="URL profil untuk aksi Follow.",
    )
    parser.add_argument(
        "--comment-url",
        default=config.EXAMPLE_POST_URL_TO_COMMENT,
        help="URL postingan untuk aksi Comment.",
    )
    parser.add_argument(
        "--comment-text",
        help="Komentar custom. Jika kosong akan dipilih secara acak.",
    )

    args = parser.parse_args()

    asyncio.run(
        run(
            actions=args.actions,
            account_id=args.account,
            like_url=args.like_url,
            follow_url=args.follow_url,
            comment_url=args.comment_url,
            comment_text=args.comment_text,
        )
    )


if __name__ == "__main__":
    main()
