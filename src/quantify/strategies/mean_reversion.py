"""均值回归策略示例。"""

from datetime import datetime
from typing import Iterable, List

import pandas as pd

from .base import BaseStrategy, Signal, StrategyContext


class MeanReversionStrategy(BaseStrategy):
    """简单均值回归策略示例，可作为自定义策略的模板。"""

    name = "mean_reversion"

    def __init__(self, lookback: int = 20, zscore_threshold: float = 1.5):
        self.lookback = lookback
        self.zscore_threshold = zscore_threshold

    def generate_signals(self, data: pd.DataFrame, context: StrategyContext) -> Iterable[Signal]:
        """基于价格相对均线的偏离程度生成交易信号。"""
        if "close" not in data.columns:
            raise KeyError("数据必须包含收盘价列 close")

        closes = data["close"]
        rolling_mean = closes.rolling(self.lookback, min_periods=1).mean()
        rolling_std = closes.rolling(self.lookback, min_periods=1).std(ddof=0)
        zscore = (closes - rolling_mean) / rolling_std.replace(0, pd.NA)

        signals: List[Signal] = []
        latest_timestamp: datetime = data.index[-1]
        latest_z = zscore.iloc[-1]

        if latest_z is pd.NA:
            return signals

        symbol = data.attrs.get("symbol", "UNKNOWN")

        if latest_z > self.zscore_threshold:
            signals.append(Signal(symbol=symbol, timestamp=latest_timestamp, direction="sell"))
        elif latest_z < -self.zscore_threshold:
            signals.append(Signal(symbol=symbol, timestamp=latest_timestamp, direction="buy"))
        else:
            signals.append(Signal(symbol=symbol, timestamp=latest_timestamp, direction="hold", weight=0.0))

        context.record("zscore", float(latest_z))
        return signals
