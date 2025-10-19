"""常用指标与特征构建实现。"""

from dataclasses import dataclass

import pandas as pd


@dataclass
class MovingAverageFactor:
    """简单移动均线因子示例。"""

    window: int = 20
    price_column: str = "close"
    factor_name: str = "ma"

    def transform(self, data: pd.DataFrame) -> pd.Series:
        """计算移动均线，并返回因子序列。"""
        if self.price_column not in data.columns:
            raise KeyError(f"数据缺少价格列: {self.price_column}")
        factor = data[self.price_column].rolling(self.window, min_periods=1).mean()
        factor.name = f"{self.factor_name}_{self.window}"
        return factor

