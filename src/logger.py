import logging
import os
import sys

# إنشاء مجلد للـ logs إن لم يكن موجوداً
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE_PATH = os.path.join(LOG_DIR, "app.log")

# ضبط صيغة الـ Log
LOG_FORMAT = "[%(asctime)s] %(levelname)s - %(name)s - %(message)s"

logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT,
    handlers=[
        logging.FileHandler(LOG_FILE_PATH, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)


def get_logger(name: str) -> logging.Logger:
    """إرجاع كائن Logger مخصص باسم الموديول"""
    return logging.getLogger(name)