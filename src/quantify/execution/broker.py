"""模拟执行引擎，负责执行策略信号。"""

from dataclasses import dataclass
from typing import Iterable, List

from ..strategies import Signal


@dataclass
class Order:
    """订单实体，用于描述执行请求。"""

    symbol: str
    direction: str
    quantity: float
    price: float


class PaperBroker:
    """纸上交易执行器，按收盘价执行信号。"""

    def __init__(self, slippage: float = 0.0, commission: float = 0.0):
        self.slippage = slippage
        self.commission = commission

    def execute(self, signals: Iterable[Signal], last_price: float) -> List[Order]:
        """将策略信号转换为模拟订单。"""
        orders: List[Order] = []
        for signal in signals:
            if signal.direction == "hold" or signal.weight == 0.0:
                continue
            trade_price = last_price * (1 + self.slippage if signal.direction == "buy" else 1 - self.slippage)
            quantity = signal.weight
            orders.append(
                Order(
                    symbol=signal.symbol,
                    direction=signal.direction,
                    quantity=quantity,
                    price=trade_price + self.commission,
                )
            )
        return orders

