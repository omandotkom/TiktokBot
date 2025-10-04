import logging
import sys
from logging.handlers import RotatingFileHandler

def setup_logger():
    """
    Mengkonfigurasi logger untuk output ke konsol dan file.
    """
    # Tentukan format log
    log_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Dapatkan root logger
    logger = logging.getLogger("TikTokBot")
    logger.setLevel(logging.INFO)

    # Buat console handler dan set levelnya
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(log_formatter)
    logger.addHandler(console_handler)

    # Buat file handler dengan rotasi file
    # File log akan disimpan di 'bot.log' dengan ukuran maksimal 5MB
    # dan akan menyimpan hingga 3 file log lama.
    file_handler = RotatingFileHandler(
        "bot.log", maxBytes=5 * 1024 * 1024, backupCount=3, encoding='utf-8'
    )
    file_handler.setFormatter(log_formatter)
    logger.addHandler(file_handler)

    return logger

# Buat instance logger untuk digunakan di seluruh aplikasi
log = setup_logger()