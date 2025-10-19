"""数据加载器基础接口定义。"""

from abc import ABC, abstractmethod
from typing import Protocol

import pandas as pd


class DataLoader(Protocol):
    """数据加载器协议，所有数据读取类应实现 `load` 方法。"""

    def load(self, symbol: str, **kwargs) -> pd.DataFrame:  # pragma: no cover - 接口定义
        """加载单个标的的历史数据。"""
        ...


class AbstractDataLoader(ABC):
    """抽象数据加载器，提供通用校验逻辑。"""

    @abstractmethod
    def load(self, symbol: str, **kwargs) -> pd.DataFrame:
        """抽象方法，子类负责返回满足项目要求的数据格式。"""

    def validate(self, data: pd.DataFrame) -> pd.DataFrame:
        """基础校验：统一列名与排序。"""
        required_columns = {"open", "high", "low", "close", "volume"}
        if not required_columns.issubset(set(map(str.lower, data.columns))):
            raise ValueError("数据必须至少包含 open/high/low/close/volume 列")
        return data.sort_index()

