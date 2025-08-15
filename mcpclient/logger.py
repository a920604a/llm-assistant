# logger.py
import logging

# 全局基本設定
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

def get_logger(name: str = __name__):
    return logging.getLogger(name)
