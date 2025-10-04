import pytest
import asyncio
from unittest.mock import patch, MagicMock

from bot.humanizer import Humanizer

@pytest.mark.asyncio
async def test_sleep_random():
    """
    Tes fungsi sleep_random untuk memastikan ia menunggu dalam rentang waktu yang diharapkan.
    """
    humanizer = Humanizer()
    min_s, max_s = 0.1, 0.2

    # Gunakan patch untuk menggantikan asyncio.sleep agar tes berjalan cepat
    with patch("asyncio.sleep", new_callable=MagicMock) as mock_sleep:
        # new_callable=MagicMock diperlukan untuk async context
        mock_sleep.return_value = asyncio.Future()
        mock_sleep.return_value.set_result(None)

        await humanizer.sleep_random(min_s, max_s, jitter=False)

        # Pastikan asyncio.sleep dipanggil sekali
        mock_sleep.assert_called_once()

        # Dapatkan argumen yang dipanggil ke sleep
        sleep_duration = mock_sleep.call_args[0][0]

        # Verifikasi durasi berada dalam rentang yang benar
        assert min_s <= sleep_duration <= max_s

@pytest.mark.asyncio
async def test_sleep_random_with_jitter():
    """
    Tes fungsi sleep_random dengan jitter.
    """
    humanizer = Humanizer()
    min_s, max_s = 0.1, 0.2

    with patch("asyncio.sleep", new_callable=MagicMock) as mock_sleep:
        mock_sleep.return_value = asyncio.Future()
        mock_sleep.return_value.set_result(None)

        await humanizer.sleep_random(min_s, max_s, jitter=True)

        mock_sleep.assert_called_once()
        sleep_duration = mock_sleep.call_args[0][0]

        # Jitter menambahkan antara 0.05 dan 0.2
        assert min_s + 0.05 <= sleep_duration <= max_s + 0.2

@pytest.mark.asyncio
async def test_typing_like_human():
    """
    Tes fungsi typing_like_human untuk memastikan ia mengetik karakter per karakter.
    """
    humanizer = Humanizer()
    mock_page = MagicMock()
    mock_page.keyboard = MagicMock()
    mock_page.wait_for_selector = AsyncMock()
    mock_page.keyboard.press = MagicMock()

    selector = "#input"
    text_to_type = "hello"

    # Mock asyncio.sleep agar tidak ada jeda nyata
    with patch("asyncio.sleep", return_value=None):
        await humanizer.typing_like_human(mock_page, selector, text_to_type, min_delay=0, max_delay=0)

    # Verifikasi wait_for_selector dan click dipanggil
    mock_page.wait_for_selector.assert_called_once_with(selector, state="visible")
    mock_page.wait_for_selector.return_value.click.assert_called_once()

    # Verifikasi page.keyboard.press dipanggil untuk setiap karakter
    assert mock_page.keyboard.press.call_count == len(text_to_type)

    # Verifikasi setiap karakter diketik dengan benar
    calls = mock_page.keyboard.press.call_args_list
    typed_chars = [call[0][0] for call in calls]
    assert "".join(typed_chars) == text_to_type