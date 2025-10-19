"""统一的日志工具，简化日志配置。"""

import logging
from typing import Optional


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """返回带有标准格式的日志记录器。"""
    logger = logging.getLogger(name if name else "quantify")
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger

