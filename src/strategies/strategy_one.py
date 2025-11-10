import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from src.core.signal_result import SignalResult
from dataclasses import dataclass
import talib as ta


@dataclass
class StrategyState:
    """策略状态类，用于追踪持仓信息和风控数据"""
    position: bool = False  # 是否持仓
    entry_price: float = 0.0  # 入场价格
    entry_time: pd.Timestamp = None  # 入场时间
    highest_price: float = 0.0  # 持仓期间最高价
    portfolio_high: float = 0.0  # 账户最高净值
    stop_loss_price: float = 0.0  # 当前止损价
    trading_suspended: bool = False  # 是否暂停交易
    suspend_until: pd.Timestamp = None  # 暂停交易截止时间

class StrategyOne:
    """
    策略一：日频多头趋势+动量策略
    
    特点：
    1. 趋势跟踪：使用双均线（5日和20日）确认趋势
    2. 动量确认：使用RSI(14)确认动量强度
    3. 风险控制：包含ATR止损、时间止损、大盘熔断、最大回撤暂停等机制
    """

    def __init__(self, params: Dict[str, Any]):
        """
        初始化策略
        
        Args:
            params: 策略参数字典，包含：
                - short_window: 短期均线周期（默认5日）
                - long_window: 长期均线周期（默认20日）
                - rsi_period: RSI计算周期（默认14日）
                - atr_period: ATR计算周期（默认14日）
                - atr_multiplier: ATR止损倍数（默认2）
                - max_hold_days: 最大持仓天数（默认10）
                - max_drawdown: 最大回撤阈值（默认0.15）
                - suspend_days: 触发回撤后暂停天数（默认5）
                - index_drop_threshold: 大盘熔断阈值（默认0.03）
        """
        # 技术指标参数
        self.short_window = params.get('short_window', 5)
        self.long_window = params.get('long_window', 20)
        self.rsi_period = params.get('rsi_period', 14)
        self.atr_period = params.get('atr_period', 14)
        
        # 风控参数
        self.atr_multiplier = params.get('atr_multiplier', 2)
        self.max_hold_days = params.get('max_hold_days', 10)
        self.max_drawdown = params.get('max_drawdown', 0.15)
        self.suspend_days = params.get('suspend_days', 5)
        self.index_drop_threshold = params.get('index_drop_threshold', 0.03)
        
        # 策略状态
        self.state = StrategyState()

    def _check_market_condition(self, index_data: pd.DataFrame) -> bool:
        """
        检查大盘条件是否允许交易
        
        Args:
            index_data: 指数数据，包含'close'列
            
        Returns:
            bool: 是否允许交易
        """
        if len(index_data) < 2:
            return True
            
        # 计算指数日涨跌幅
        index_return = (index_data['close'].iloc[-1] / index_data['close'].iloc[-2] - 1)
        
        # 如果指数跌幅超过阈值，触发熔断机制
        if index_return < -self.index_drop_threshold:
            self.state.trading_suspended = True
            self.state.suspend_until = pd.Timestamp.now() + pd.Timedelta(days=1)
            return False
            
        return True

    def _check_position_risk(self, data: pd.DataFrame) -> bool:
        """
        检查持仓风险，判断是否需要强制平仓
        
        Args:
            data: 交易数据
            
        Returns:
            bool: 是否需要平仓
        """
        if not self.state.position:
            return False
            
        current_price = data['close'].iloc[-1]
        
        # 1. 止损检查
        if current_price < self.state.stop_loss_price:
            return True
            
        # 2. 时间止损检查
        if (data.index[-1] - self.state.entry_time).days > self.max_hold_days:
            # 如果超过最大持仓天数且没有创新高，平仓
            if current_price <= self.state.highest_price:
                return True
                
        # 3. 更新持仓期间最高价
        self.state.highest_price = max(self.state.highest_price, current_price)
        
        # 4. 回撤检查
        current_drawdown = 1 - current_price / self.state.highest_price
        if current_drawdown > self.max_drawdown:
            self.state.trading_suspended = True
            self.state.suspend_until = data.index[-1] + pd.Timedelta(days=self.suspend_days)
            return True
            
        return False

    def generate_signals(self, data: pd.DataFrame, index_data: Optional[pd.DataFrame] = None) -> SignalResult:
        """
        生成交易信号
        
        Args:
            data: 交易数据，包含OHLCV数据
            index_data: 可选的指数数据，用于大盘熔断判断
            
        Returns:
            SignalResult: 包含交易信号的结果对象
        """
        # 检查数据有效性
        if len(data) < self.long_window:
            return SignalResult(pd.Series(0, index=data.index))
            
        # 计算技术指标
        close = data['close']
        high = data['high']
        low = data['low']
        
        short_ma = ta.SMA(close, timeperiod=self.short_window)
        long_ma = ta.SMA(close, timeperiod=self.long_window)
        rsi = ta.RSI(close, timeperiod=self.rsi_period)
        atr = ta.ATR(high, low, close, timeperiod=self.atr_period)
        
        # 初始化信号数组
        signals = pd.Series(0, index=data.index)
        
        # 对每个时间点生成信号
        for i in range(self.long_window, len(data)):
            # 跳过暂停交易期
            if self.state.trading_suspended:
                if data.index[i] >= self.state.suspend_until:
                    self.state.trading_suspended = False
                continue
                
            # 检查大盘条件
            if index_data is not None and not self._check_market_condition(index_data.iloc[:i+1]):
                continue
                
            current_price = close.iloc[i]
            
            # 如果已有持仓，检查是否需要平仓
            if self.state.position:
                if self._check_position_risk(data.iloc[:i+1]):
                    signals.iloc[i] = -1
                    self.state.position = False
                    continue
                    
            # 生成买入信号
            trend_up = (current_price > long_ma.iloc[i]) and (short_ma.iloc[i] > long_ma.iloc[i])
            momentum_ok = (rsi.iloc[i] > 50) and (rsi.iloc[i] < 70)
            
            if not self.state.position and trend_up and momentum_ok:
                signals.iloc[i] = 1
                self.state.position = True
                self.state.entry_price = current_price
                self.state.entry_time = data.index[i]
                self.state.highest_price = current_price
                self.state.stop_loss_price = current_price - self.atr_multiplier * atr.iloc[i]
                
            # 生成卖出信号（趋势破坏）
            elif self.state.position and not trend_up:
                signals.iloc[i] = -1
                self.state.position = False
        
        # 创建结果对象
        result = SignalResult()
        result.signals = signals
        result.metadata = {
            'short_ma': short_ma,
            'long_ma': long_ma,
            'rsi': rsi,
            'atr': atr,
            'stop_loss': pd.Series([self.state.stop_loss_price if self.state.position else np.nan for _ in range(len(data))],
                                 index=data.index)
        }
        
        return result

    def calculate_position_size(self, portfolio_value: float, current_price: float, atr: float) -> int:
        """
        计算仓位大小
        
        Args:
            portfolio_value: 总资金
            current_price: 当前价格
            atr: 当前ATR值
            
        Returns:
            int: 建议购买的股数
        """
        # 计算每笔交易的风险金额（总资金的1%）
        risk_per_trade = 0.01 * portfolio_value
        
        # 止损距离（2倍ATR）
        stop_loss_distance = self.atr_multiplier * atr
        
        # 计算可以买入的股数
        if stop_loss_distance <= 0:
            return 0
            
        position_size = risk_per_trade / stop_loss_distance
        shares = int(position_size / current_price)
        
        return shares

    def get_strategy_name(self) -> str:
        """
        获取策略名称
        
        Returns:
            策略名称
        """
        return "Strategy One - Trend Following with Momentum"

    def get_strategy_description(self) -> str:
        """
        获取策略描述
        
        Returns:
            策略描述
        """
        return """
        日频多头趋势+动量策略
        
        核心逻辑：
        1. 趋势确认：价格在20日均线之上，且5日均线上穿20日均线
        2. 动量过滤：RSI(14)在50-70之间，避免追高
        3. 仓位管理：基于ATR的动态头寸管理，单笔最大风险1%
        
        风控机制：
        1. ATR止损：入场后设置2倍ATR作为动态止损
        2. 时间止损：持仓超过10天未创新高则平仓
        3. 大盘熔断：指数日跌幅超过3%触发熔断
        4. 回撤暂停：单笔回撤超过15%暂停交易5天
        """
