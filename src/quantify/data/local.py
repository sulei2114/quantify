"""本地 CSV 数据加载器实现。"""

from pathlib import Path
from typing import Optional

import pandas as pd

from .base import AbstractDataLoader


class LocalCSVLoader(AbstractDataLoader):
    """从本地 CSV 文件读取行情数据。"""

    def __init__(self, data_dir: Path, encoding: str = "utf-8", parse_dates: Optional[str] = None):
        self._data_dir = data_dir
        self._encoding = encoding
        self._parse_dates = parse_dates or "date"

    def load(self, symbol: str, **kwargs) -> pd.DataFrame:
        """根据证券代码加载数据文件，并执行基础清洗。"""
        file_path = Path(kwargs.get("file")) if kwargs.get("file") else self._data_dir / f"{symbol}.csv"
        if not file_path.exists():
            raise FileNotFoundError(f"找不到本地数据文件: {file_path}")
        data = pd.read_csv(file_path, encoding=self._encoding, parse_dates=[self._parse_dates])
        data = data.set_index(self._parse_dates)
        return self.validate(data)

