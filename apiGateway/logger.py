# logger.py
import logging
import os
from datetime import datetime, timedelta, timezone
from logging.handlers import TimedRotatingFileHandler


class AppLogger:
    """結構化 Logger，支援 UTC+8 時區、自動建立 log 目錄、console 與 file handler"""

    LOG_DIR = "logs"
    UTC8 = timezone(timedelta(hours=8))

    def __init__(
        self, name: str = __name__, log_file: str = "app.log", level=logging.INFO
    ):
        self.name = name
        self.log_file = os.path.join(self.LOG_DIR, log_file)
        self.level = level

        # 確保 log 目錄存在
        os.makedirs(self.LOG_DIR, exist_ok=True)

        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        self.logger.propagate = False  # 避免重複輸出

        # 設定 formatter
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        )
        formatter.converter = self._utc8_converter

        # console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        # file handler，每日滾動
        file_handler = TimedRotatingFileHandler(
            self.log_file, when="midnight", interval=1, backupCount=7, encoding="utf-8"
        )
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    @staticmethod
    def _utc8_converter(*args):
        """返回 UTC+8 的 struct_time"""
        return datetime.now(AppLogger.UTC8).timetuple()

    def get_logger(self):
        return self.logger
