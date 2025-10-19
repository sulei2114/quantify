# 量化交易项目

> 所有代码注释与文档默认使用中文。

## 项目简介

本仓库提供一个 Python 量化交易研究与回测框架的基础骨架，涵盖配置管理、数据加载、策略开发、回测执行、下单撮合等核心模块，便于在此基础上进行扩展迭代。

## 代码结构

```text
quantify/
├── pyproject.toml          # 项目依赖与打包配置
├── requirements.txt        # 常用第三方依赖
├── src/quantify            # 核心源码
│   ├── config              # 配置定义
│   ├── data                # 数据加载器
│   ├── features            # 特征工程
│   ├── strategies          # 策略实现
│   ├── backtest            # 回测引擎
│   ├── execution           # 执行撮合
│   └── utils               # 通用工具
├── scripts                 # 脚本入口
└── tests                   # 单元测试
```

## 快速开始

1. 创建虚拟环境并安装依赖：

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows 请使用 .venv\\Scripts\\activate
   pip install -r requirements.txt
   ```

2. 在 `data/raw` 目录准备示例数据（如 `demo_symbol.csv`），包含 `date,open,high,low,close,volume` 字段。

3. 运行示例回测脚本：

   ```bash
   python scripts/run_backtest.py
   ```

## 开发指南

- 新增策略：继承 `src/quantify/strategies/base.py` 中的 `BaseStrategy` 并实现 `generate_signals`。
- 新增数据源：继承 `src/quantify/data/base.py` 中的 `AbstractDataLoader`，实现 `load` 与必要的校验逻辑。
- 若需扩展配置，可在 `src/quantify/config/settings.py` 中添加字段，并通过 `.env` 文件覆盖默认值。

## 测试

使用 `pytest` 运行单元测试：

```bash
pytest
```
