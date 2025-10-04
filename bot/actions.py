from playwright.async_api import Page, TimeoutError as PlaywrightTimeoutError

from bot.humanizer import humanizer
from bot.logger import log

class ActionManager:
    """
    Mengelola semua tindakan otomatis di TikTok.
    """

    async def auto_like(self, page: Page, post_url: str) -> bool:
        """
        Secara otomatis menyukai (like) sebuah postingan TikTok.

        Args:
            page: Halaman Playwright.
            post_url: URL dari postingan yang akan disukai.

        Returns:
            True jika berhasil menyukai, False jika gagal atau sudah disukai.
        """
        log.info(f"Mencoba menyukai postingan: {post_url}")
        try:
            await page.goto(post_url, wait_until="networkidle", timeout=60000)
            await humanizer.sleep_random(2, 4)
            await humanizer.scroll_like_human(page, scrolls=1)

            # Selector untuk tombol like. Mungkin perlu diperbarui jika TikTok mengubah UI.
            # Ini mencari SVG dengan path yang khas untuk ikon hati.
            like_button_selector = "span[data-e2e='like-icon']"

            like_button = await page.wait_for_selector(like_button_selector, state="visible", timeout=10000)

            # Cek apakah postingan sudah di-like.
            # Jika sudah di-like, tombolnya (atau parent-nya) biasanya memiliki atribut tertentu.
            # Ini adalah contoh, mungkin perlu inspeksi lebih lanjut.
            is_liked = await like_button.evaluate("""
                (element) => {
                    // TikTok bisa menandai dengan warna (mis. 'rgb(254, 44, 85)') atau atribut lain
                    const parentButton = element.closest('button');
                    const svg = parentButton.querySelector('svg');
                    return svg && svg.getAttribute('fill') === 'currentColor';
                }
            """)

            if is_liked:
                log.info(f"Postingan sudah disukai sebelumnya: {post_url}")
                return False

            log.info("Tombol 'Like' ditemukan. Melakukan hover dan klik.")
            await humanizer.move_mouse_simulated(page, like_button)
            await humanizer.sleep_random(0.5, 1.0)
            await like_button.click()
            await humanizer.sleep_random(1, 2)

            log.info(f"Berhasil menyukai postingan: {post_url}")
            return True

        except PlaywrightTimeoutError:
            log.error(f"Gagal menemukan tombol 'Like' pada {post_url}. Mungkin URL tidak valid atau halaman lambat.")
            return False
        except Exception as e:
            log.error(f"Terjadi error tak terduga saat mencoba menyukai postingan: {e}")
            return False

    async def auto_follow(self, page: Page, user_url: str) -> bool:
        """
        Secara otomatis mengikuti (follow) seorang pengguna TikTok.
        """
        log.info(f"Mencoba mengikuti pengguna: {user_url}")
        try:
            await page.goto(user_url, wait_until="networkidle", timeout=60000)
            await humanizer.sleep_random(2, 4)

            # Selector untuk tombol follow.
            follow_button_selector = "button[data-e2e='follow-button']"

            follow_button = await page.wait_for_selector(follow_button_selector, state="visible", timeout=10000)

            button_text = await follow_button.inner_text()
            if button_text.lower() != "follow":
                log.info(f"Pengguna sudah diikuti atau status tombol tidak dikenali: {user_url} (Teks: {button_text})")
                return False

            log.info("Tombol 'Follow' ditemukan. Melakukan hover dan klik.")
            await humanizer.move_mouse_simulated(page, follow_button)
            await humanizer.sleep_random(0.5, 1.0)
            await follow_button.click()
            await humanizer.sleep_random(1, 2)

            log.info(f"Berhasil mengikuti pengguna: {user_url}")
            return True

        except PlaywrightTimeoutError:
            log.error(f"Gagal menemukan tombol 'Follow' pada {user_url}.")
            return False
        except Exception as e:
            log.error(f"Terjadi error tak terduga saat mengikuti pengguna: {e}")
            return False

    async def auto_comment(self, page: Page, post_url: str, comment_text: str) -> bool:
        """
        Secara otomatis memberikan komentar pada sebuah postingan.
        """
        log.info(f"Mencoba berkomentar di postingan: {post_url}")
        try:
            await page.goto(post_url, wait_until="networkidle", timeout=60000)
            await humanizer.sleep_random(3, 5)
            await humanizer.scroll_like_human(page, scrolls=2)

            # Selector untuk area input komentar.
            comment_input_selector = "div[data-e2e='comment-input']"

            comment_area = await page.wait_for_selector(comment_input_selector, state="visible", timeout=15000)

            log.info("Area komentar ditemukan. Mengetik komentar.")
            await humanizer.move_mouse_simulated(page, comment_area)
            await comment_area.click()
            await humanizer.sleep_random(0.5, 1.0)

            # Menggunakan humanizer untuk mengetik
            await humanizer.typing_like_human(page, comment_input_selector, comment_text)

            # Selector untuk tombol post comment
            post_button_selector = "button[data-e2e='comment-post-button']"
            post_button = await page.wait_for_selector(post_button_selector, state="visible")

            if not await post_button.is_enabled():
                log.warning("Tombol 'Post' tidak aktif. Mungkin komentar kosong atau ada masalah lain.")
                return False

            await humanizer.sleep_random(0.5, 1.0)
            await post_button.click()
            await humanizer.sleep_random(2, 3)

            log.info(f"Berhasil mengirim komentar: '{comment_text}'")
            return True

        except PlaywrightTimeoutError:
            log.error(f"Gagal menemukan area komentar atau tombol post di {post_url}.")
            return False
        except Exception as e:
            log.error(f"Terjadi error tak terduga saat berkomentar: {e}")
            return False


# Instance tunggal untuk digunakan di seluruh aplikasi
action_manager = ActionManager()