# 项目结构说明

```
ar_usd_scraper/
├── 📁 .github/
│   └── 📁 workflows/
│       └── 📄 daily.yml                    # GitHub Actions 自动抓取工作流
├── 📁 data/
│   └── 📄 .gitkeep                        # 数据目录占位文件
├── 📁 tests/
│   └── 📄 test_scraper.py                 # 抓取器单元测试
├── 📄 .gitignore                          # Git 忽略文件
├── 📄 README.md                           # 项目说明文档
├── 📄 requirements.txt                    # Python 依赖包
├── 📄 constants.py                        # 常量定义
├── 📄 storage.py                          # CSV 存储模块
├── 📄 scraper.py                          # 抓取器核心逻辑
├── 📄 main.py                             # Typer CLI 主程序
├── 📄 ui.py                               # Streamlit Web 界面
├── 📄 run_tests.py                        # 测试运行脚本
├── 📄 pytest.ini                          # pytest 配置
├── 📄 config.example.py                   # 示例配置文件
└── 📄 PROJECT_STRUCTURE.md                # 本文件
```

## 核心模块说明

### 🔧 抓取器模块 (`scraper.py`)
- **BaseScraper**: 基础抓取器类，提供网络请求和汇率解析功能
- **ValorHoySource**: 抓取 ValorHoy 页面数据
- **HistoricoSource**: 抓取 Historico 页面数据
- **ScraperManager**: 抓取器管理器，协调不同数据源

### 💾 存储模块 (`storage.py`)
- **RateStorage**: CSV 数据存储管理，支持去重和验证
- 自动创建数据目录和文件
- 数据完整性检查

### 🖥️ 用户界面
- **CLI 界面** (`main.py`): 使用 Typer 实现命令行工具
- **Web 界面** (`ui.py`): 使用 Streamlit 实现可视化界面

### 🤖 自动化
- **GitHub Actions** (`.github/workflows/daily.yml`): 每日自动抓取和提交

## 使用方法

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. CLI 使用
```bash
# 抓取昨天数据
python main.py yesterday

# 回补历史数据
python main.py backfill 2024-01-01 2024-01-31

# 查看状态
python main.py status
```

### 3. Web 界面
```bash
streamlit run ui.py
```

### 4. 运行测试
```bash
python run_tests.py
# 或
pytest tests/ -v
```

## 数据格式

CSV 文件结构 (`data/rates.csv`):
```csv
date,rate_sell,source,fetched_at
2024-12-15,1292.5,bna_divisas_valorhoy,2024-12-15T10:30:00
2024-12-14,1290.0,bna_divisas_historico,2024-12-15T10:35:00
```

## 配置说明

所有硬编码的配置都集中在 `constants.py` 文件中，包括：
- 数据源 URL
- 页面解析关键词
- 网络请求参数
- 文件路径等

## 注意事项

1. **网络请求**: 实现了重试机制和指数退避，避免对目标网站造成压力
2. **数据验证**: 汇率值必须 > 0，否则拒绝写入
3. **去重机制**: 按日期去重，保留最新的 `fetched_at` 记录
4. **错误处理**: 完善的异常处理和日志记录
5. **测试覆盖**: 使用 mock 对象测试网络请求，确保代码质量
