# ARS to USD Scraper

BNA 阿根廷兑美元（divisas）卖出价抓取器

## 功能特性

- 支持两个数据源：ValorHoySource 和 HistoricoSource
- CSV 数据存储，支持去重和验证
- Typer CLI 命令行工具
- Streamlit Web 界面
- GitHub Actions 自动抓取

## 安装

```bash
pip install -r requirements.txt
```

## 使用方法

### CLI 工具

```bash
# 抓取昨天数据
python main.py yesterday

# 回补历史数据
python main.py backfill 2024-01-01 2024-01-31

# 调试模式
python main.py yesterday --debug --dry-run
```

### Web 界面

```bash
streamlit run ui.py
```

## 项目结构

```
ar_usd_scraper/
├── main.py              # CLI 主程序
├── ui.py                # Streamlit 界面
├── scraper.py           # 抓取器核心逻辑
├── storage.py           # CSV 存储模块
├── constants.py         # 常量定义
├── data/                # 数据存储目录
├── tests/               # 测试文件
└── .github/workflows/   # GitHub Actions
```
