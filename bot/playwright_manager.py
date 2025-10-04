import asyncio
from typing import Optional
from playwright.async_api import async_playwright, Browser, BrowserContext, Page, Playwright

from bot.config import config
from bot.logger import log

class PlaywrightManager:
    """
    Mengelola instance Playwright, browser, dan konteks.
    """
    def __init__(self):
        self.p: Optional[Playwright] = None
        self.browser: Optional[Browser] = None

    async def start(self) -> None:
        """
        Memulai Playwright dan meluncurkan browser.
        """
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

        log.info(f"Meluncurkan browser {config.PLAYWRIGHT_BROWSER} (headless: {config.HEADLESS})")

        browser_launcher = getattr(self.p, config.PLAYWRIGHT_BROWSER)
        self.browser = await browser_launcher.launch(**browser_options)

    async def create_context(self, account_id: str, proxy_url: Optional[str] = None) -> BrowserContext:
        """
        Membuat konteks browser baru, bisa dengan proxy.

        Args:
            account_id: ID unik untuk akun, digunakan untuk session management.
            proxy_url: URL proxy opsional (mis. "http://user:pass@host:port").

        Returns:
            BrowserContext baru.
        """
        if not self.browser:
            raise ConnectionError("Browser belum diinisialisasi. Panggil start() terlebih dahulu.")

        context_options = {
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
            "viewport": {"width": 1920, "height": 1080},
            "no_viewport": True,
        }

        # Tambahkan proxy jika disediakan
        used_proxy = proxy_url or config.PROXY_URL
        if used_proxy:
            log.info(f"Menggunakan proxy untuk akun {account_id}")
            context_options["proxy"] = {"server": used_proxy}

        log.info(f"Membuat konteks baru untuk akun: {account_id}")
        context = await self.browser.new_context(**context_options)

        # Menambahkan skrip inisialisasi untuk menghindari deteksi bot
        await context.add_init_script("""
            if (navigator.webdriver) {
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => false,
                });
            }
        """)

        return context

    async def new_page(self, context: BrowserContext) -> Page:
        """
        Membuka halaman baru dalam konteks yang diberikan.

        Args:
            context: Konteks browser.

        Returns:
            Page baru.
        """
        log.info("Membuka halaman baru.")
        return await context.new_page()

    async def close(self) -> None:
        """
        Menutup browser dan menghentikan Playwright.
        """
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