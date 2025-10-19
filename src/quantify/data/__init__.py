"""数据读取模块集合。"""

from .base import DataLoader
from .local import LocalCSVLoader

__all__ = ["DataLoader", "LocalCSVLoader"]

