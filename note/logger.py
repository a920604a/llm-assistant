# logger.py
import logging
import os

LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "app.log")

# 確保 log 目錄存在
os.makedirs(LOG_DIR, exist_ok=True)

# 設定 formatter
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")

# 建立 handlers
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
file_handler.setFormatter(formatter)

# 全局 logger 基本設定
logging.basicConfig(
    level=logging.INFO,
    handlers=[console_handler, file_handler],  # 同時輸出到 console + file
)


def get_logger(name: str = __name__):
    return logging.getLogger(name)
