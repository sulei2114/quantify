# 策略一（Strategy One）使用说明

## 概述

策略一是一个日频多头趋势+动量策略，结合了趋势跟踪和动量确认，并包含完善的风险控制机制。

## 策略特点

### 核心逻辑

1. **趋势确认**：使用双均线系统（默认5日和20日）确认趋势方向
   - 价格需要在长期均线之上
   - 短期均线需要在长期均线之上

2. **动量过滤**：使用RSI(14)确认动量强度
   - RSI需要在50-70之间，避免追高
   - 确保既有上涨动力，又不过度超买

3. **仓位管理**：基于ATR的动态头寸管理
   - 单笔最大风险控制在1%
   - 根据波动率动态调整仓位大小

### 风险控制机制

1. **ATR止损**：入场后设置2倍ATR作为动态止损
2. **时间止损**：持仓超过10天未创新高则平仓
3. **大盘熔断**：指数日跌幅超过3%触发熔断，暂停交易1天
4. **回撤暂停**：单笔回撤超过15%暂停交易5天

## 快速开始

### 安装依赖

```bash
pip install -e .
pip install TA-Lib pydantic-settings
```

### 基本使用

```python
from quantify.strategies import StrategyOne

# 创建策略实例
strategy = StrategyOne(
    short_window=5,      # 短期均线周期
    long_window=20,      # 长期均线周期
    rsi_period=14,       # RSI计算周期
    atr_multiplier=2.0,  # ATR止损倍数
)

# 准备数据（必须包含 open, high, low, close, volume）
import pandas as pd
data = pd.DataFrame({
    'open': [...],
    'high': [...],
    'low': [...],
    'close': [...],
    'volume': [...]
}, index=pd.date_range('2024-01-01', periods=100))
data.attrs['symbol'] = 'AAPL'

# 创建策略上下文
class SimpleContext:
    def __init__(self):
        self.positions = {}
        self.records = {}
    
    def get_position(self, symbol: str) -> float:
        return self.positions.get(symbol, 0.0)
    
    def record(self, key: str, value: float) -> None:
        if key not in self.records:
            self.records[key] = []
        self.records[key].append(value)

context = SimpleContext()

# 使用策略
strategy.on_start(context)
signals = list(strategy.generate_signals(data, context))
strategy.on_finish(context)

# 查看信号
for signal in signals:
    print(f"{signal.timestamp}: {signal.direction} {signal.symbol}")
```

### 运行示例

```bash
python examples/demo_strategy_one.py
```

## 参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `short_window` | int | 5 | 短期移动平均线周期 |
| `long_window` | int | 20 | 长期移动平均线周期 |
| `rsi_period` | int | 14 | RSI计算周期 |
| `atr_period` | int | 14 | ATR计算周期 |
| `atr_multiplier` | float | 2.0 | ATR止损倍数 |
| `max_hold_days` | int | 10 | 最大持仓天数 |
| `max_drawdown` | float | 0.15 | 最大回撤阈值（15%） |
| `suspend_days` | int | 5 | 触发回撤后暂停天数 |
| `index_drop_threshold` | float | 0.03 | 大盘熔断阈值（3%） |

## 信号说明

策略生成三种类型的信号：

- **buy**: 买入信号，当趋势和动量条件都满足时触发
- **sell**: 卖出信号，当趋势破坏或触发止损时触发
- **hold**: 持有信号，当前状态保持不变

## 技术指标

策略会记录以下技术指标到上下文：

- `rsi`: 相对强弱指标
- `short_ma`: 短期移动平均线
- `long_ma`: 长期移动平均线

## 注意事项

1. **数据要求**：输入数据必须包含 `open`, `high`, `low`, `close`, `volume` 五列
2. **指数数据**：可以通过 `set_index_data()` 方法设置大盘指数数据以启用熔断机制
3. **TA-Lib依赖**：策略使用TA-Lib库计算技术指标，需要确保正确安装
4. **状态管理**：策略维护内部状态，在回测时应为每个回测周期创建新的策略实例

## 测试

运行策略测试：

```bash
# 测试原始策略实现
python -m pytest tests/test_strategy_one.py -v

# 测试BaseStrategy适配器
python -m pytest tests/test_strategy_one_adapter.py -v

# 运行所有测试
python -m pytest tests/ -v
```

## 架构

策略采用适配器模式：

- `src/strategies/strategy_one.py`: 原始策略实现，包含完整的信号生成逻辑
- `src/quantify/strategies/strategy_one.py`: BaseStrategy适配器，将原始实现适配到quantify框架

这种设计允许策略既可以独立使用，也可以集成到quantify框架中。

## 许可证

MIT License
