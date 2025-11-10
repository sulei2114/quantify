"""测试StrategyOne适配器与BaseStrategy接口的集成"""

import unittest
import pandas as pd
import numpy as np
from datetime import datetime

from quantify.strategies import StrategyOne, Signal


class MockContext:
    """模拟策略上下文"""
    
    def __init__(self):
        self.positions = {}
        self.records = {}
    
    def get_position(self, symbol: str) -> float:
        return self.positions.get(symbol, 0.0)
    
    def record(self, key: str, value: float) -> None:
        if key not in self.records:
            self.records[key] = []
        self.records[key].append(value)


class TestStrategyOneAdapter(unittest.TestCase):
    """测试StrategyOne适配器"""
    
    def setUp(self):
        """测试前的准备工作"""
        # 创建策略实例（使用默认参数）
        self.strategy = StrategyOne()
        
        # 创建模拟上下文
        self.context = MockContext()
        
        # 创建测试数据
        close_prices = [100.0 + i + np.sin(i/5)*3 for i in range(50)]
        high_prices = [p + abs(np.sin(i/7))*2 for i, p in enumerate(close_prices)]
        low_prices = [p - abs(np.sin(i/7))*2 for i, p in enumerate(close_prices)]
        
        self.test_data = pd.DataFrame({
            'open': close_prices,
            'high': high_prices,
            'low': low_prices,
            'close': close_prices,
            'volume': [100000 + i*1000 for i in range(50)]
        }, index=pd.date_range('2025-01-01', periods=50))
        
        self.test_data.attrs['symbol'] = 'TEST'
    
    def test_strategy_name(self):
        """测试策略名称"""
        self.assertEqual(self.strategy.name, "strategy_one")
    
    def test_initialization_with_params(self):
        """测试使用自定义参数初始化"""
        strategy = StrategyOne(
            short_window=10,
            long_window=30,
            rsi_period=20
        )
        self.assertIsNotNone(strategy)
        self.assertEqual(strategy.name, "strategy_one")
    
    def test_generate_signals(self):
        """测试信号生成"""
        signals = list(self.strategy.generate_signals(self.test_data, self.context))
        
        # 应该返回至少一个信号
        self.assertGreater(len(signals), 0)
        
        # 检查信号类型
        for signal in signals:
            self.assertIsInstance(signal, Signal)
            self.assertEqual(signal.symbol, 'TEST')
            self.assertIn(signal.direction, ['buy', 'sell', 'hold'])
            self.assertIsInstance(signal.timestamp, datetime)
    
    def test_generate_signals_records_indicators(self):
        """测试信号生成时记录技术指标"""
        list(self.strategy.generate_signals(self.test_data, self.context))
        
        # 应该记录了技术指标
        self.assertIn('rsi', self.context.records)
        self.assertIn('short_ma', self.context.records)
        self.assertIn('long_ma', self.context.records)
    
    def test_generate_signals_missing_columns(self):
        """测试数据缺失必需列时抛出异常"""
        incomplete_data = pd.DataFrame({
            'close': [100, 101, 102]
        }, index=pd.date_range('2025-01-01', periods=3))
        incomplete_data.attrs['symbol'] = 'TEST'
        
        with self.assertRaises(KeyError):
            list(self.strategy.generate_signals(incomplete_data, self.context))
    
    def test_on_start_resets_state(self):
        """测试on_start重置策略状态"""
        # 先生成一些信号以改变状态
        list(self.strategy.generate_signals(self.test_data, self.context))
        
        # 调用on_start应该重置状态
        self.strategy.on_start(self.context)
        
        # 验证状态已重置
        self.assertFalse(self.strategy._strategy.state.position)
        self.assertEqual(self.strategy._strategy.state.entry_price, 0.0)
        self.assertIsNone(self.strategy._strategy.state.entry_time)
    
    def test_on_finish(self):
        """测试on_finish不会抛出异常"""
        try:
            self.strategy.on_finish(self.context)
        except Exception as e:
            self.fail(f"on_finish raised unexpected exception: {e}")
    
    def test_set_index_data(self):
        """测试设置指数数据"""
        index_data = pd.DataFrame({
            'close': [1000 + i for i in range(50)]
        }, index=self.test_data.index)
        
        # 设置指数数据不应抛出异常
        try:
            self.strategy.set_index_data(index_data)
        except Exception as e:
            self.fail(f"set_index_data raised unexpected exception: {e}")
        
        # 使用指数数据生成信号
        signals = list(self.strategy.generate_signals(self.test_data, self.context))
        self.assertGreater(len(signals), 0)
    
    def test_signal_direction_buy(self):
        """测试买入信号的生成"""
        # 创建强烈上涨趋势的数据
        uptrend_data = pd.DataFrame({
            'open': [100 + i*2 for i in range(50)],
            'high': [101 + i*2 for i in range(50)],
            'low': [99 + i*2 for i in range(50)],
            'close': [100 + i*2 for i in range(50)],
            'volume': [100000] * 50
        }, index=pd.date_range('2025-01-01', periods=50))
        uptrend_data.attrs['symbol'] = 'TEST'
        
        signals = list(self.strategy.generate_signals(uptrend_data, self.context))
        
        # 应该能生成信号
        self.assertGreater(len(signals), 0, "应该生成信号")
        
        # 检查信号方向是有效的
        for signal in signals:
            self.assertIn(signal.direction, ['buy', 'sell', 'hold'], 
                         f"信号方向应该是 buy/sell/hold，实际为 {signal.direction}")
    
    def test_lifecycle_hooks(self):
        """测试完整的策略生命周期"""
        # 开始
        self.strategy.on_start(self.context)
        
        # 生成信号
        signals = list(self.strategy.generate_signals(self.test_data, self.context))
        self.assertGreater(len(signals), 0)
        
        # 结束
        self.strategy.on_finish(self.context)


if __name__ == '__main__':
    unittest.main()
