"""轻量级回测引擎实现，连接数据、策略与配置。"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import pandas as pd

from ..config import Settings
from ..data import DataLoader
from ..strategies import BaseStrategy, Signal


@dataclass
class BacktestResult:
    """回测结果容器。"""

    symbol: str
    signals: List[Signal] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    raw_data: Optional[pd.DataFrame] = None


class _SimpleContext:
    """基础策略上下文实现，提供最小依赖。"""

    def __init__(self) -> None:
        self._positions: Dict[str, float] = {}
        self._records: Dict[str, float] = {}

    def get_position(self, symbol: str) -> float:
        return self._positions.get(symbol, 0.0)

    def set_position(self, symbol: str, size: float) -> None:
        self._positions[symbol] = size

    def record(self, key: str, value: float) -> None:
        self._records[key] = value

    @property
    def records(self) -> Dict[str, float]:
        return self._records


class BacktestEngine:
    """回测引擎，将策略信号组合成结果输出。"""

    def __init__(self, settings: Settings, data_loader: DataLoader, strategy: BaseStrategy):
        self._settings = settings
        self._data_loader = data_loader
        self._strategy = strategy
        self._context = _SimpleContext()

    def run(self, symbol: str, **kwargs) -> BacktestResult:
        """执行单标的回测流程。"""
        raw_data = self._data_loader.load(symbol, **kwargs)
        if not isinstance(raw_data.index, pd.DatetimeIndex):
            raise TypeError("数据索引必须为 DatetimeIndex 以便对齐时间序列")

        raw_data.attrs["symbol"] = symbol

        self._strategy.on_start(self._context)
        signals = list(self._strategy.generate_signals(raw_data, self._context))
        self._strategy.on_finish(self._context)

        # 简化处理：这里只返回策略信号，真实项目可扩展仓位、资金曲线等计算
        metrics = {
            "environment": self._settings.environment,
            "signal_count": len(signals),
            **self._context.records,
        }
        return BacktestResult(symbol=symbol, signals=signals, metrics=metrics, raw_data=raw_data)
