"""
示例配置文件
复制此文件为 config.py 并根据需要修改
"""

# 网络请求配置
REQUEST_TIMEOUT = 10  # 请求超时时间（秒）
MAX_RETRIES = 3      # 最大重试次数
RETRY_DELAY_BASE = 2 # 指数退避基数

# 数据源配置
VALORHOY_URL = "https://www.bna.com.ar/Cotizador/MonedasHistorico"
HISTORICO_URL = "https://www.bna.com.ar/Cotizador/HistoricoPrincipales"

# 页面解析关键词
DOLLAR_USA_TEXT = "Dolar U.S.A"
VENTA_TEXT = "Venta"
FECHA_TEXT = "Fecha:"

# 数据源标识
SOURCE_VALORHOY = "bna_divisas_valorhoy"
SOURCE_HISTORICO = "bna_divisas_historico"

# 自定义 User-Agent
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# 数据验证
MIN_RATE = 0.0  # 最小汇率值

# 文件路径
DATA_DIR = "data"
RATES_CSV = "data/rates.csv"

# 日期格式
DATE_FORMAT = "%Y-%m-%d"
ARGENTINA_DATE_FORMAT = "%d/%m/%Y"

# 日志配置
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Streamlit 配置
STREAMLIT_THEME = "light"
STREAMLIT_PAGE_ICON = "💱"
STREAMLIT_LAYOUT = "wide"
