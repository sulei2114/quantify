"""回测脚本入口，演示如何连接各个模块。"""

from pathlib import Path

from quantify.backtest import BacktestEngine
from quantify.config import Settings
from quantify.data import LocalCSVLoader
from quantify.strategies import MeanReversionStrategy
from quantify.utils import get_logger


def main() -> None:
    """构建并运行一次示例回测。"""
    logger = get_logger(__name__)
    settings = Settings()

    data_dir = Path("./data/raw")
    data_loader = LocalCSVLoader(data_dir=data_dir)
    strategy = MeanReversionStrategy()

    engine = BacktestEngine(settings=settings, data_loader=data_loader, strategy=strategy)
    try:
        result = engine.run("demo_symbol")
    except FileNotFoundError:
        logger.warning("未找到示例数据文件，请在 data/raw 目录准备 demo_symbol.csv")
        return

    logger.info("回测完成，信号数量: %d", len(result.signals))
    logger.info("回测指标: %s", result.metrics)


if __name__ == "__main__":
    main()

