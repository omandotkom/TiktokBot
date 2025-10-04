import asyncio
import random
import math
from playwright.async_api import Page, ElementHandle

from bot.logger import log

class Humanizer:
    """
    Menyediakan metode untuk membuat interaksi bot lebih mirip manusia.
    """

    async def sleep_random(self, min_s: float, max_s: float, jitter: bool = True) -> None:
        """
        Tidur (sleep) untuk durasi acak antara min dan max detik.

        Args:
            min_s: Durasi tidur minimal dalam detik.
            max_s: Durasi tidur maksimal dalam detik.
            jitter: Jika True, tambahkan variasi kecil pada waktu tidur.
        """
        base_delay = random.uniform(min_s, max_s)
        if jitter:
            base_delay += random.uniform(0.05, 0.2)

        log.debug(f"Sleeping for {base_delay:.2f} seconds.")
        await asyncio.sleep(base_delay)

    async def typing_like_human(self, page: Page, selector: str, text: str, min_delay: float = 0.05, max_delay: float = 0.15) -> None:
        """
        Mengetik teks ke dalam elemen input karakter per karakter dengan delay acak.

        Args:
            page: Halaman Playwright.
            selector: Selector CSS untuk elemen input.
            text: Teks yang akan diketik.
            min_delay: Delay minimal antar ketukan tombol.
            max_delay: Delay maksimal antar ketukan tombol.
        """
        log.info(f"Mengetik teks '{text[:20]}...' ke selector '{selector}'")
        element = await page.wait_for_selector(selector, state="visible")
        await element.click()
        await self.sleep_random(0.2, 0.5)

        for char in text:
            await page.keyboard.press(char, delay=random.uniform(min_delay, max_delay) * 1000)

        await self.sleep_random(0.3, 0.6)

    async def move_mouse_simulated(self, page: Page, element: ElementHandle) -> None:
        """
        Mensimulasikan gerakan mouse ke tengah elemen target.
        Ini adalah implementasi sederhana; bisa diperluas dengan kurva Bezier.

        Args:
            page: Halaman Playwright.
            element: ElementHandle tujuan.
        """
        try:
            box = await element.bounding_box()
            if not box:
                log.warning("Tidak bisa mendapatkan bounding box elemen untuk gerakan mouse.")
                await element.hover() # Fallback ke hover standar
                return

            start_pos = await page.mouse.position

            # Jika mouse belum pernah digerakkan, posisinya (0,0)
            if start_pos['x'] == 0 and start_pos['y'] == 0:
                # Pindahkan mouse ke posisi awal yang acak di viewport
                viewport = page.viewport_size
                if viewport:
                    start_x = random.uniform(0, viewport['width'] / 4)
                    start_y = random.uniform(0, viewport['height'] / 4)
                    await page.mouse.move(start_x, start_y)
                    start_pos = {'x': start_x, 'y': start_y}

            target_x = box['x'] + box['width'] / 2 + random.uniform(-box['width']/4, box['width']/4)
            target_y = box['y'] + box['height'] / 2 + random.uniform(-box['height']/4, box['height']/4)

            steps = random.randint(10, 20)
            log.debug(f"Menggerakkan mouse ke ({target_x:.0f}, {target_y:.0f}) dalam {steps} langkah.")

            for i in range(steps):
                intermediate_x = start_pos['x'] + (target_x - start_pos['x']) * (i + 1) / steps
                intermediate_y = start_pos['y'] + (target_y - start_pos['y']) * (i + 1) / steps
                await page.mouse.move(intermediate_x, intermediate_y)
                await asyncio.sleep(random.uniform(0.01, 0.03))

            await element.hover() # Pastikan akhirnya hover tepat di elemen
        except Exception as e:
            log.error(f"Gagal mensimulasikan gerakan mouse: {e}")
            await element.hover() # Fallback

    async def scroll_like_human(self, page: Page, scrolls: int = 3, min_dist: int = 200, max_dist: int = 400) -> None:
        """
        Mensimulasikan scrolling halaman seperti manusia.

        Args:
            page: Halaman Playwright.
            scrolls: Jumlah scroll yang akan dilakukan.
            min_dist: Jarak scroll minimal dalam pixel.
            max_dist: Jarak scroll maksimal dalam pixel.
        """
        log.info(f"Melakukan {scrolls} kali scroll halaman.")
        for _ in range(scrolls):
            scroll_distance = random.randint(min_dist, max_dist)
            direction = random.choice([1, -1]) # 1 untuk ke bawah, -1 untuk ke atas

            # 80% kemungkinan scroll ke bawah
            if random.random() > 0.8:
                direction = -1

            log.debug(f"Scrolling {'bawah' if direction == 1 else 'atas'} sejauh {scroll_distance}px")
            await page.mouse.wheel(0, scroll_distance * direction)
            await self.sleep_random(0.5, 1.5)

# Instance tunggal untuk digunakan di seluruh aplikasi
humanizer = Humanizer()