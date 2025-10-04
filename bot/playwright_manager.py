import asyncio
from typing import Optional

from playwright.async_api import (
    async_playwright,
    Browser,
    BrowserContext,
    Page,
    Playwright,
)
from playwright_stealth import Stealth

from bot.config import config
from bot.logger import log

# Gunakan satu instance Stealth untuk seluruh lifecycle browser
_stealth = Stealth()


class PlaywrightManager:
    """Mengelola instance Playwright, browser, dan konteks."""

    def __init__(self) -> None:
        self.p: Optional[Playwright] = None
        self.browser: Optional[Browser] = None

    async def start(self) -> None:
        """Memulai Playwright dan meluncurkan browser."""
        if self.p is not None:
            log.warning("Playwright sudah berjalan.")
            return

        log.info("Memulai Playwright...")
        self.p = await async_playwright().start()

        browser_options = {
            "headless": config.HEADLESS,
            "args": [
                "--disable-blink-features=AutomationControlled",
                "--start-maximized",
            ],
        }

        log.info(
            "Meluncurkan browser %s (headless: %s)",
            config.PLAYWRIGHT_BROWSER,
            config.HEADLESS,
        )

        browser_launcher = getattr(self.p, config.PLAYWRIGHT_BROWSER)
        self.browser = await browser_launcher.launch(**browser_options)

    async def create_context(
        self, account_id: str, proxy_url: Optional[str] = None
    ) -> BrowserContext:
        """Membuat konteks browser baru, bisa dengan proxy."""
        if not self.browser:
            raise ConnectionError("Browser belum diinisialisasi. Panggil start() terlebih dahulu.")

        context_options = {
            "user_agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/117.0.0.0 Safari/537.36"
            ),
            "viewport": {"width": 1920, "height": 1080},
            "no_viewport": True,
            "locale": config.LOCALE,
            "timezone_id": config.TIMEZONE_ID,
        }

        used_proxy = proxy_url or config.PROXY_URL
        if used_proxy:
            log.info("Menggunakan proxy untuk akun %s", account_id)
            context_options["proxy"] = {"server": used_proxy}

        log.info("Membuat konteks baru untuk akun: %s", account_id)
        context = await self.browser.new_context(**context_options)

        # Terapkan patch stealth pada level konteks agar halaman baru langsung terproteksi
        await _stealth.apply_stealth_async(context)
        return context

    async def new_page(self, context: BrowserContext) -> Page:
        """Membuka halaman baru dalam konteks yang diberikan dan menerapkan patch stealth."""
        log.info("Membuka halaman baru dan menerapkan patch stealth.")
        page = await context.new_page()
        await _stealth.apply_stealth_async(page)
        return page

    async def close(self) -> None:
        """Menutup browser dan menghentikan Playwright."""
        if self.browser:
            log.info("Menutup browser.")
            await self.browser.close()
            self.browser = None

        if self.p:
            log.info("Menghentikan Playwright.")
            await self.p.stop()
            self.p = None


# Instance tunggal untuk digunakan di seluruh aplikasi
playwright_manager = PlaywrightManager()
