"""针对配置模块的基础测试。"""

from quantify.config import Settings


def test_settings_defaults() -> None:
    """确保配置默认值可以正确实例化。"""
    settings = Settings()
    assert settings.environment == "dev"
    assert settings.backtest.initial_capital == 1_000_000

