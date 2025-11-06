import pandas as pd
import numpy as np
from typing import Dict, List, Any
from src.core.signal_result import SignalResult


class StrategyOne:
    """
    策略一：基于移动平均线的交易策略
    """

    def __init__(self, params: Dict[str, Any]):
        """
        初始化策略
        
        Args:
            params: 策略参数字典，应包含:
                - short_window: 短期移动平均窗口
                - long_window: 长期移动平均窗口
        """
        self.short_window = params.get('short_window', 5)
        self.long_window = params.get('long_window', 20)

    def generate_signals(self, data: pd.DataFrame) -> SignalResult:
        """
        基于移动平均线生成交易信号
        
        Args:
            data: 包含价格数据的DataFrame，至少应包含'close'列
            
        Returns:
            SignalResult: 包含交易信号的结果对象
        """
        # 计算短期和长期移动平均线
        short_ma = self._calculate_moving_average(data['close'], self.short_window)
        long_ma = self._calculate_moving_average(data['close'], self.long_window)
        
        # 初始化信号数组
        signals = pd.Series(0, index=data.index)
        
        # 生成买入信号：短期均线上穿长期均线
        signals[(short_ma > long_ma) & (short_ma.shift(1) <= long_ma.shift(1))] = 1
        
        # 生成卖出信号：短期均线下穿长期均线
        signals[(short_ma < long_ma) & (short_ma.shift(1) >= long_ma.shift(1))] = -1
        
        # 创建结果对象
        result = SignalResult()
        result.signals = signals
        result.metadata = {
            'short_ma': short_ma,
            'long_ma': long_ma,
            'short_window': self.short_window,
            'long_window': self.long_window
        }
        
        return result

    def _calculate_moving_average(self, series: pd.Series, window: int) -> pd.Series:
        """
        计算简单移动平均线
        
        Args:
            series: 价格序列
            window: 窗口大小
            
        Returns:
            移动平均线序列
        """
        return series.rolling(window=window).mean()

    def get_strategy_name(self) -> str:
        """
        获取策略名称
        
        Returns:
            策略名称
        """
        return "Strategy One - Moving Average Crossover"