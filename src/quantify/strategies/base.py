from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Iterator, Optional
import pandas as pd

@dataclass
class Signal:
    """策略生成的交易信号。"""
    symbol: str
    action: str  # "BUY", "SELL"
    price: Optional[float] = None
    volume: Optional[float] = None
    reason: str = ""

class StrategyContext(ABC):
    """策略运行上下文接口。"""
    @abstractmethod
    def get_position(self, symbol: str) -> float:
        pass

    @abstractmethod
    def set_position(self, symbol: str, size: float) -> None:
        pass

    @abstractmethod
    def record(self, key: str, value: float) -> None:
        pass

class BaseStrategy(ABC):
    """策略基类。"""

    def on_start(self, context: StrategyContext) -> None:
        """策略开始运行时调用。"""
        pass

    @abstractmethod
    def generate_signals(self, data: pd.DataFrame, context: StrategyContext) -> Iterator[Signal]:
        """根据数据生成交易信号。"""
        pass

    def on_finish(self, context: StrategyContext) -> None:
        """策略结束运行时调用。"""
        pass
