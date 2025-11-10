"""项目配置定义，使用 Pydantic 管理参数。"""

from pathlib import Path
from typing import Literal, Optional

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class DataSourceConfig(BaseModel):
    """数据源配置，定义数据源类型与路径。"""

    source_type: Literal["csv", "parquet", "database", "api"] = Field(
        default="csv", description="数据源类型"
    )
    path: Optional[Path] = Field(default=None, description="本地文件路径")
    connection_uri: Optional[str] = Field(default=None, description="数据库或 API 连接 URI")


class BacktestConfig(BaseModel):
    """回测配置，控制回测的核心参数。"""

    start: str = Field(default="2020-01-01", description="回测起始日期")
    end: str = Field(default="2023-12-31", description="回测结束日期")
    initial_capital: float = Field(default=1_000_000, description="初始资金")
    benchmark: str = Field(default="SPY", description="基准证券代码")


class Settings(BaseSettings):
    """全局配置入口，支持环境变量覆盖默认值。"""

    environment: Literal["dev", "prod", "test"] = Field(default="dev", description="运行环境")
    data: DataSourceConfig = Field(default_factory=DataSourceConfig, description="数据源设置")
    backtest: BacktestConfig = Field(
        default_factory=BacktestConfig,
        description="回测核心参数",
    )
    cache_dir: Path = Field(default=Path("./.cache"), description="缓存目录")

    class Config:
        env_prefix = "quantify_"
        env_file = ".env"

