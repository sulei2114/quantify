"""策略基础接口与信号定义。"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Iterable, Protocol

import pandas as pd


@dataclass(frozen=True)
class Signal:
    """交易信号实体。"""

    symbol: str
    timestamp: datetime
    direction: str  # buy / sell / hold
    weight: float = 1.0


class StrategyContext(Protocol):
    """策略上下文协议，可由回测引擎或实时系统实现。"""

    def get_position(self, symbol: str) -> float:  # pragma: no cover - 协议方法
        ...

    def record(self, key: str, value: float) -> None:  # pragma: no cover
        ...


class BaseStrategy(ABC):
    """策略基类，定义策略生命周期接口。"""

    name: str = "base"

    @abstractmethod
    def generate_signals(self, data: pd.DataFrame, context: StrategyContext) -> Iterable[Signal]:
        """根据行情数据生成交易信号。"""

    def on_start(self, context: StrategyContext) -> None:
        """策略开始运行时的钩子，可用于初始化状态。"""

    def on_finish(self, context: StrategyContext) -> None:
        """策略结束运行时的钩子，可用于清理资源。"""

