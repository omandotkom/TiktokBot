import json
import os
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from bot.session_manager import SessionManager
from bot.config import config

@pytest.fixture
def temp_session_dir(tmp_path):
    """Fixture untuk membuat direktori sesi sementara."""
    original_dir = config.SESSION_DIR
    temp_dir = tmp_path / "sessions"
    temp_dir.mkdir()
    config.SESSION_DIR = str(temp_dir)
    yield str(temp_dir)
    # Kembalikan ke direktori asli setelah tes selesai
    config.SESSION_DIR = original_dir


@pytest.mark.asyncio
async def test_save_session(temp_session_dir):
    """Tes fungsi penyimpanan sesi."""
    sm = SessionManager()
    account_id = "test_user_save"

    # Mock data sesi
    mock_cookies = [{"name": "sessionid", "value": "12345"}]
    mock_local_storage = {"theme": "dark"}

    # Mock konteks Playwright
    mock_context = AsyncMock()
    mock_context.cookies.return_value = mock_cookies

    # Mock halaman dan evaluasi local storage
    mock_page = AsyncMock()
    mock_page.evaluate.return_value = json.dumps(mock_local_storage)
    mock_context.pages = [mock_page]

    await sm.save_session(mock_context, account_id)

    # Verifikasi file telah dibuat
    session_file = os.path.join(temp_session_dir, f"{account_id}.json")
    assert os.path.exists(session_file)

    # Verifikasi konten file
    with open(session_file, "r") as f:
        data = json.load(f)
        assert data["cookies"] == mock_cookies
        assert data["localStorage"] == mock_local_storage

@pytest.mark.asyncio
async def test_load_session_file_not_found():
    """Tes pemuatan sesi ketika file tidak ada."""
    sm = SessionManager()
    mock_context = AsyncMock()

    # Panggil load_session untuk akun yang tidak ada
    loaded = await sm.load_session(mock_context, "non_existent_user")

    # Seharusnya mengembalikan False dan tidak memanggil metode konteks
    assert not loaded
    mock_context.add_cookies.assert_not_called()
    mock_context.add_init_script.assert_not_called()

@pytest.mark.asyncio
async def test_load_session_success(temp_session_dir):
    """Tes pemuatan sesi yang berhasil."""
    sm = SessionManager()
    account_id = "test_user_load"
    session_file = os.path.join(temp_session_dir, f"{account_id}.json")

    # Buat file sesi palsu
    mock_data = {
        "cookies": [{"name": "csrftoken", "value": "abc"}],
        "localStorage": {"onboarding": "true"}
    }
    with open(session_file, "w") as f:
        json.dump(mock_data, f)

    mock_context = AsyncMock()

    loaded = await sm.load_session(mock_context, account_id)

    assert loaded
    # Verifikasi bahwa metode untuk menambahkan data ke konteks dipanggil
    mock_context.add_cookies.assert_called_once_with(mock_data["cookies"])
    mock_context.add_init_script.assert_called_once()

    # Periksa skrip yang dihasilkan
    call_args = mock_context.add_init_script.call_args[0]
    script = call_args[0]
    assert "localStorage.setItem(`onboarding`, `true`);" in script