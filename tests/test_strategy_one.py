import unittest
import pandas as pd
import numpy as np
import sys
import os

# 添加项目根目录和src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

from strategies.strategy_one import StrategyOne
# 修改导入路径，与strategy_one.py中保持一致
from src.core.signal_result import SignalResult


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
            'long_window': 10
        }
        
        # 创建策略实例
        self.strategy = StrategyOne(self.params)
        
        # 创建测试数据
        self.test_data = pd.DataFrame({
            'close': [100, 102, 101, 103, 105, 107, 106, 108, 110, 112, 
                     115, 113, 111, 114, 116, 118, 120, 122, 121, 123]
        })

    def test_initialization(self):
        """
        测试策略初始化
        """
        self.assertEqual(self.strategy.short_window, 5)
        self.assertEqual(self.strategy.long_window, 10)
        
        # 测试默认参数
        default_strategy = StrategyOne({})
        self.assertEqual(default_strategy.short_window, 5)
        self.assertEqual(default_strategy.long_window, 20)

    def test_calculate_moving_average(self):
        """
        测试移动平均线计算
        """
        series = pd.Series([1, 2, 3, 4, 5])
        ma = self.strategy._calculate_moving_average(series, 3)
        
        # 前两个值应该是NaN（因为窗口大小为3）
        self.assertTrue(np.isnan(ma.iloc[0]))
        self.assertTrue(np.isnan(ma.iloc[1]))
        
        # 第三个值应该是前三个数的平均值
        self.assertEqual(ma.iloc[2], 2.0)
        
        # 第四个值应该是第2,3,4个数的平均值
        self.assertEqual(ma.iloc[3], 3.0)

    def test_generate_signals(self):
        """
        测试信号生成
        """
        result = self.strategy.generate_signals(self.test_data)
        
        # 检查返回类型
        self.assertIsInstance(result, SignalResult)
        
        # 检查信号是否存在
        self.assertTrue(hasattr(result, 'signals'))
        
        # 检查元数据是否存在
        self.assertTrue(hasattr(result, 'metadata'))
        self.assertIn('short_ma', result.metadata)
        self.assertIn('long_ma', result.metadata)
        self.assertIn('short_window', result.metadata)
        self.assertIn('long_window', result.metadata)

    def test_get_strategy_name(self):
        """
        测试获取策略名称
        """
        name = self.strategy.get_strategy_name()
        self.assertEqual(name, "Strategy One - Moving Average Crossover")


if __name__ == '__main__':
    unittest.main()