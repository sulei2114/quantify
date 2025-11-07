import unittest
import pandas as pd
import numpy as np
import sys
import os

# 添加项目根目录和src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

from strategies.strategy_one import StrategyOne, StrategyState
from src.core.signal_result import SignalResult
import talib as ta


class TestStrategyOne(unittest.TestCase):
    """
    StrategyOne策略的单元测试类
    """

    def setUp(self):
        """
        测试前的准备工作
        """
        # 创建测试参数
        self.params = {
            'short_window': 5,
            'long_window': 20,
            'rsi_period': 14,
            'atr_period': 14,
            'atr_multiplier': 2,
            'max_hold_days': 10,
            'max_drawdown': 0.15,
            'suspend_days': 5,
            'index_drop_threshold': 0.03
        }
        
        # 创建策略实例
        self.strategy = StrategyOne(self.params)
        
        # 创建模拟价格数据
        close_prices = [100.0 + i + np.sin(i/5)*3 for i in range(50)]
        high_prices = [p + abs(np.sin(i/7))*2 for i, p in enumerate(close_prices)]
        low_prices = [p - abs(np.sin(i/7))*2 for i, p in enumerate(close_prices)]
        
        # 创建测试数据
        self.test_data = pd.DataFrame({
            'open': close_prices,
            'high': high_prices,
            'low': low_prices,
            'close': close_prices,
            'volume': [100000 + i*1000 for i in range(50)]
        }, index=pd.date_range('2025-01-01', periods=50))
        
        # 创建指数数据
        self.index_data = pd.DataFrame({
            'close': [1000 + i + np.sin(i/10)*20 for i in range(50)]
        }, index=self.test_data.index)

    def test_initialization(self):
        """测试策略初始化"""
        # 测试指定参数
        self.assertEqual(self.strategy.short_window, 5)
        self.assertEqual(self.strategy.long_window, 20)
        self.assertEqual(self.strategy.rsi_period, 14)
        self.assertEqual(self.strategy.atr_period, 14)
        self.assertEqual(self.strategy.atr_multiplier, 2)
        self.assertEqual(self.strategy.max_hold_days, 10)
        self.assertEqual(self.strategy.max_drawdown, 0.15)
        
        # 测试默认参数
        default_strategy = StrategyOne({})
        self.assertEqual(default_strategy.short_window, 5)
        self.assertEqual(default_strategy.long_window, 20)
        
        # 测试策略状态初始化
        self.assertIsInstance(self.strategy.state, StrategyState)
        self.assertFalse(self.strategy.state.position)
        self.assertEqual(self.strategy.state.entry_price, 0.0)
        
    def test_market_condition(self):
        """测试大盘条件检查"""
        # 创建正常市场数据
        normal_market = pd.DataFrame({
            'close': [1000, 1010]  # 上涨1%
        })
        self.assertTrue(self.strategy._check_market_condition(normal_market))
        
        # 创建熔断市场数据
        crash_market = pd.DataFrame({
            'close': [1000, 960]  # 下跌4%
        })
        self.assertFalse(self.strategy._check_market_condition(crash_market))
        self.assertTrue(self.strategy.state.trading_suspended)
        
    def test_position_risk(self):
        """测试持仓风险检查"""
        # 设置初始状态
        self.strategy.state.position = True
        self.strategy.state.entry_price = 100
        self.strategy.state.entry_time = pd.Timestamp('2025-01-01')
        self.strategy.state.stop_loss_price = 95
        self.strategy.state.highest_price = 100
        
        # 测试止损触发
        data_stop_loss = pd.DataFrame({
            'close': [94]
        }, index=[pd.Timestamp('2025-01-02')])
        self.assertTrue(self.strategy._check_position_risk(data_stop_loss))
        
        # 测试时间止损
        data_time_stop = pd.DataFrame({
            'close': [99]
        }, index=[pd.Timestamp('2025-01-15')])  # 超过10天但价格低于最高点
        self.assertTrue(self.strategy._check_position_risk(data_time_stop))
        
    def test_generate_signals(self):
        """测试信号生成"""
        result = self.strategy.generate_signals(self.test_data, self.index_data)
        
        # 检查基本属性
        self.assertIsInstance(result, SignalResult)
        self.assertTrue(hasattr(result, 'signals'))
        self.assertTrue(hasattr(result, 'metadata'))
        
        # 检查技术指标
        self.assertIn('short_ma', result.metadata)
        self.assertIn('long_ma', result.metadata)
        self.assertIn('rsi', result.metadata)
        self.assertIn('atr', result.metadata)
        self.assertIn('stop_loss', result.metadata)
        
        # 验证信号值是否合法
        self.assertTrue(all(s in [-1, 0, 1] for s in result.signals))
        
    def test_calculate_position_size(self):
        """测试仓位计算"""
        portfolio_value = 1000000  # 100万资金
        current_price = 100
        atr = 2.0
        
        # 计算建议仓位
        shares = self.strategy.calculate_position_size(
            portfolio_value=portfolio_value,
            current_price=current_price,
            atr=atr
        )
        
        # 验证计算逻辑
        risk_amount = portfolio_value * 0.01  # 1%风险
        stop_loss_distance = 2 * atr  # 2倍ATR
        expected_shares = int(risk_amount / stop_loss_distance / current_price)
        
        self.assertEqual(shares, expected_shares)
        
        # 测试ATR为0的情况
        shares_zero_atr = self.strategy.calculate_position_size(
            portfolio_value=portfolio_value,
            current_price=current_price,
            atr=0
        )
        self.assertEqual(shares_zero_atr, 0)
        
    def test_get_strategy_name(self):
        """测试策略名称和描述"""
        name = self.strategy.get_strategy_name()
        self.assertEqual(name, "Strategy One - Trend Following with Momentum")
        
        description = self.strategy.get_strategy_description()
        self.assertIn("趋势确认", description)
        self.assertIn("动量过滤", description)
        self.assertIn("仓位管理", description)


if __name__ == '__main__':
    unittest.main()
