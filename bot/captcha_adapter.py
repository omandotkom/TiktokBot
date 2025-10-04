import abc
import requests
from typing import Optional

from bot.config import config
from bot.logger import log

class CaptchaSolver(abc.ABC):
    """
    Interface (Abstract Base Class) untuk semua captcha solver.
    """
    @abc.abstractmethod
    def solve(self, captcha_image_url: str) -> Optional[str]:
        """
        Metode untuk menyelesaikan captcha.

        Args:
            captcha_image_url: URL dari gambar captcha yang perlu diselesaikan.

        Returns:
            Teks hasil solusi captcha, atau None jika gagal.
        """
        pass

class DummyCaptchaSolver(CaptchaSolver):
    """
    Solver dummy yang tidak melakukan apa-apa.
    Berguna untuk development atau jika tidak ada captcha yang perlu diselesaikan.
    """
    def solve(self, captcha_image_url: str) -> Optional[str]:
        log.warning("Menggunakan DummyCaptchaSolver. Captcha tidak akan diselesaikan.")
        log.info(f"URL Gambar Captcha: {captcha_image_url}")
        # TODO: Implementasi manual atau fallback di sini jika diperlukan.
        # Misalnya, minta input dari pengguna di konsol.
        # solution = input("Masukkan solusi captcha secara manual: ")
        # return solution
        return None

class TwoCaptchaAdapter(CaptchaSolver):
    """
    Adapter untuk layanan 2Captcha.
    Ini adalah contoh implementasi dan memerlukan penyesuaian.
    """
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("API Key untuk 2Captcha tidak boleh kosong.")
        self.api_key = api_key
        self.submit_url = "http://2captcha.com/in.php"
        self.retrieve_url = "http://2captcha.com/res.php"

    def solve(self, captcha_image_url: str) -> Optional[str]:
        """
        Mengirim captcha ke 2Captcha dan menunggu hasilnya.

        # TODO: Ini adalah contoh implementasi. Developer perlu mengembangkannya
        # agar lebih robust, termasuk penanganan error dan polling yang lebih baik.
        """
        log.info("Mencoba menyelesaikan captcha menggunakan 2Captcha...")

        # Langkah 1: Kirim permintaan untuk menyelesaikan captcha
        files = {'file': requests.get(captcha_image_url, stream=True).raw}
        params = {
            'key': self.api_key,
            'method': 'post',
            'json': 1
        }
        try:
            response = requests.post(self.submit_url, params=params, files=files, timeout=30)
            response.raise_for_status()
            result = response.json()

            if result.get('status') != 1:
                log.error(f"2Captcha Gagal: {result.get('request')}")
                return None

            request_id = result['request']
            log.info(f"Captcha berhasil dikirim ke 2Captcha. ID Permintaan: {request_id}")

            # Langkah 2: Polling untuk mendapatkan hasil
            # TODO: Implementasikan polling loop yang lebih baik dengan timeout
            import time
            time.sleep(10) # Tunggu beberapa saat sebelum polling pertama

            retrieve_params = {
                'key': self.api_key,
                'action': 'get',
                'id': request_id,
                'json': 1
            }
            for _ in range(20): # Coba hingga 20 kali (total ~2 menit)
                res_response = requests.get(self.retrieve_url, params=retrieve_params, timeout=30)
                res_response.raise_for_status()
                res_result = res_response.json()

                if res_result.get('status') == 1:
                    log.info("Captcha berhasil diselesaikan oleh 2Captcha.")
                    return res_result.get('request')
                elif res_result.get('request') == 'CAPCHA_NOT_READY':
                    log.info("Solusi captcha belum siap, menunggu...")
                    time.sleep(5)
                else:
                    log.error(f"Gagal mendapatkan solusi dari 2Captcha: {res_result.get('request')}")
                    return None

            log.warning("Timeout saat menunggu solusi captcha dari 2Captcha.")
            return None

        except requests.RequestException as e:
            log.error(f"Error saat berkomunikasi dengan 2Captcha: {e}")
            return None

def get_captcha_solver() -> CaptchaSolver:
    """
    Factory function untuk mendapatkan instance solver yang sesuai.
    """
    if config.CAPTCHA_API_KEY:
        log.info("Menggunakan solver 2Captcha.")
        # TODO: Ganti dengan adapter yang sesuai jika Anda menggunakan layanan lain.
        return TwoCaptchaAdapter(api_key=config.CAPTCHA_API_KEY)

    log.warning("API Key Captcha tidak ditemukan. Menggunakan solver dummy.")
    return DummyCaptchaSolver()