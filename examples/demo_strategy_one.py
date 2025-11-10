#!/usr/bin/env python
"""演示如何使用策略一（Strategy One）的示例脚本"""

import pandas as pd
import numpy as np
from quantify.strategies import StrategyOne


class SimpleContext:
    """简单的策略上下文实现"""
    
    def __init__(self):
        self.positions = {}
        self.records = {}
    
    def get_position(self, symbol: str) -> float:
        return self.positions.get(symbol, 0.0)
    
    def record(self, key: str, value: float) -> None:
        if key not in self.records:
            self.records[key] = []
        self.records[key].append(value)


def create_sample_data(days: int = 100) -> pd.DataFrame:
    """创建示例市场数据"""
    # 生成模拟价格数据
    base_price = 100.0
    close_prices = []
    
    for i in range(days):
        # 添加趋势和随机波动
        trend = i * 0.5
        noise = np.random.randn() * 2
        price = base_price + trend + noise
        close_prices.append(max(price, 10))  # 确保价格为正
    
    # 生成高低价
    high_prices = [p * (1 + abs(np.random.randn()) * 0.01) for p in close_prices]
    low_prices = [p * (1 - abs(np.random.randn()) * 0.01) for p in close_prices]
    
    # 创建DataFrame
    data = pd.DataFrame({
        'open': close_prices,
        'high': high_prices,
        'low': low_prices,
        'close': close_prices,
        'volume': [100000 + np.random.randint(-10000, 10000) for _ in range(days)]
    }, index=pd.date_range('2024-01-01', periods=days))
    
    data.attrs['symbol'] = 'DEMO'
    return data


def main():
    """主函数：演示策略使用"""
    print("=" * 60)
    print("策略一（Strategy One）使用示例")
    print("=" * 60)
    print()
    
    # 1. 创建策略实例
    print("1. 创建策略实例（使用默认参数）")
    strategy = StrategyOne(
        short_window=5,      # 短期均线
        long_window=20,      # 长期均线
        rsi_period=14,       # RSI周期
        atr_multiplier=2.0,  # ATR止损倍数
    )
    print(f"   策略名称: {strategy.name}")
    print()
    
    # 2. 准备数据
    print("2. 生成示例市场数据（100天）")
    data = create_sample_data(days=100)
    print(f"   数据形状: {data.shape}")
    print(f"   数据列: {list(data.columns)}")
    print()
    
    # 3. 创建上下文
    print("3. 创建策略上下文")
    context = SimpleContext()
    print()
    
    # 4. 初始化策略
    print("4. 初始化策略（调用 on_start）")
    strategy.on_start(context)
    print("   策略已初始化")
    print()
    
    # 5. 生成信号
    print("5. 生成交易信号")
    signals = list(strategy.generate_signals(data, context))
    print(f"   生成 {len(signals)} 个信号")
    
    if signals:
        latest_signal = signals[-1]
        print(f"   最新信号:")
        print(f"     - 标的: {latest_signal.symbol}")
        print(f"     - 时间: {latest_signal.timestamp}")
        print(f"     - 方向: {latest_signal.direction}")
        print(f"     - 权重: {latest_signal.weight}")
    print()
    
    # 6. 查看记录的技术指标
    print("6. 查看记录的技术指标")
    for key, values in context.records.items():
        if values:
            print(f"   {key}: {values[-1]:.2f}")
    print()
    
    # 7. 结束策略
    print("7. 清理策略（调用 on_finish）")
    strategy.on_finish(context)
    print("   策略已清理")
    print()
    
    print("=" * 60)
    print("示例完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
