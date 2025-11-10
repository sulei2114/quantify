"""策略一：日频多头趋势+动量策略的BaseStrategy适配器。"""

from datetime import datetime
from typing import Iterable, List, Optional
import sys
import os

import pandas as pd

# 导入原始策略实现
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))
from strategies.strategy_one import StrategyOne as OriginalStrategyOne

from .base import BaseStrategy, Signal, StrategyContext


class StrategyOne(BaseStrategy):
    """
    策略一适配器：将原始StrategyOne适配到BaseStrategy接口
    
    这是一个日频多头趋势+动量策略，特点包括：
    1. 趋势跟踪：使用双均线（5日和20日）确认趋势
    2. 动量确认：使用RSI(14)确认动量强度
    3. 风险控制：包含ATR止损、时间止损、大盘熔断、最大回撤暂停等机制
    """

    name = "strategy_one"

    def __init__(
        self,
        short_window: int = 5,
        long_window: int = 20,
        rsi_period: int = 14,
        atr_period: int = 14,
        atr_multiplier: float = 2.0,
        max_hold_days: int = 10,
        max_drawdown: float = 0.15,
        suspend_days: int = 5,
        index_drop_threshold: float = 0.03,
    ):
        """
        初始化策略一
        
        Args:
            short_window: 短期均线周期（默认5日）
            long_window: 长期均线周期（默认20日）
            rsi_period: RSI计算周期（默认14日）
            atr_period: ATR计算周期（默认14日）
            atr_multiplier: ATR止损倍数（默认2）
            max_hold_days: 最大持仓天数（默认10）
            max_drawdown: 最大回撤阈值（默认0.15）
            suspend_days: 触发回撤后暂停天数（默认5）
            index_drop_threshold: 大盘熔断阈值（默认0.03）
        """
        params = {
            'short_window': short_window,
            'long_window': long_window,
            'rsi_period': rsi_period,
            'atr_period': atr_period,
            'atr_multiplier': atr_multiplier,
            'max_hold_days': max_hold_days,
            'max_drawdown': max_drawdown,
            'suspend_days': suspend_days,
            'index_drop_threshold': index_drop_threshold,
        }
        self._strategy = OriginalStrategyOne(params)
        self._current_position = 0.0
        self._index_data: Optional[pd.DataFrame] = None

    def set_index_data(self, index_data: pd.DataFrame) -> None:
        """
        设置大盘指数数据，用于熔断机制
        
        Args:
            index_data: 指数数据，必须包含'close'列
        """
        self._index_data = index_data

    def generate_signals(
        self, data: pd.DataFrame, context: StrategyContext
    ) -> Iterable[Signal]:
        """
        根据行情数据生成交易信号
        
        Args:
            data: 包含OHLCV数据的DataFrame
            context: 策略上下文
            
        Returns:
            交易信号迭代器
        """
        # 检查必需的列
        required_columns = ['open', 'high', 'low', 'close', 'volume']
        for col in required_columns:
            if col not in data.columns:
                raise KeyError(f"数据必须包含 {col} 列")

        # 获取symbol
        symbol = data.attrs.get("symbol", "UNKNOWN")
        
        # 使用原始策略生成信号
        result = self._strategy.generate_signals(data, self._index_data)
        
        # 转换信号格式
        signals: List[Signal] = []
        
        # 获取最后一个时间点的信号
        if len(result.signals) > 0:
            latest_timestamp: datetime = data.index[-1]
            latest_signal = result.signals.iloc[-1]
            
            # 获取当前持仓
            current_position = context.get_position(symbol)
            
            if latest_signal == 1:  # 买入信号
                direction = "buy"
                weight = 1.0
            elif latest_signal == -1:  # 卖出信号
                direction = "sell"
                weight = 0.0
            else:  # 持有
                direction = "hold"
                weight = current_position
            
            signals.append(
                Signal(
                    symbol=symbol,
                    timestamp=latest_timestamp,
                    direction=direction,
                    weight=weight
                )
            )
            
            # 记录技术指标到上下文
            if 'rsi' in result.metadata:
                rsi_value = result.metadata['rsi'].iloc[-1]
                if not pd.isna(rsi_value):
                    context.record("rsi", float(rsi_value))
            
            if 'short_ma' in result.metadata:
                short_ma = result.metadata['short_ma'].iloc[-1]
                if not pd.isna(short_ma):
                    context.record("short_ma", float(short_ma))
                    
            if 'long_ma' in result.metadata:
                long_ma = result.metadata['long_ma'].iloc[-1]
                if not pd.isna(long_ma):
                    context.record("long_ma", float(long_ma))
        
        return signals

    def on_start(self, context: StrategyContext) -> None:
        """策略开始运行时的钩子"""
        # 重置策略状态
        self._strategy.state.position = False
        self._strategy.state.entry_price = 0.0
        self._strategy.state.entry_time = None
        self._strategy.state.highest_price = 0.0
        self._strategy.state.portfolio_high = 0.0
        self._strategy.state.stop_loss_price = 0.0
        self._strategy.state.trading_suspended = False
        self._strategy.state.suspend_until = None

    def on_finish(self, context: StrategyContext) -> None:
        """策略结束运行时的钩子"""
        # 清理资源
        pass
