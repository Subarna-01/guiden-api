import logging
import sys
from typing import Optional

class Logger:
    _instance: Optional["Logger"] = None
    logger: logging.Logger

    def __new__(cls) -> "Logger":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.init_logger("app", "app.log")
        return cls._instance

    def init_logger(self, name: str, log_file: str) -> None:
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG) 

        if not self.logger.handlers:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.INFO)
            console_format = logging.Formatter(
                "[%(asctime)s] %(levelname)s - %(message)s", "%Y-%m-%d %H:%M:%S"
            )
            console_handler.setFormatter(console_format)
            self.logger.addHandler(console_handler)

            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.DEBUG)
            file_format = logging.Formatter(
                "[%(asctime)s] %(levelname)s - %(name)s - %(message)s",
                "%Y-%m-%d %H:%M:%S",
            )
            file_handler.setFormatter(file_format)
            self.logger.addHandler(file_handler)

    def get_logger(self) -> logging.Logger:
        return self.logger
    
logger = Logger().get_logger()