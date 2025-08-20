"""
常量定义文件
集中管理所有硬编码的选择器、关键词和配置
"""

# 数据源相关
VALORHOY_URL = "https://www.bna.com.ar/Cotizador/MonedasHistorico"
HISTORICO_URL = "https://www.bna.com.ar/Cotizador/HistoricoPrincipales"

# 页面解析关键词
DOLLAR_USA_TEXT = "Dolar U.S.A"
VENTA_TEXT = "Venta"
FECHA_TEXT = "Fecha:"

# 数据源标识
SOURCE_VALORHOY = "bna_divisas_valorhoy"
SOURCE_HISTORICO = "bna_divisas_historico"

# 网络请求配置
REQUEST_TIMEOUT = 10
MAX_RETRIES = 3
RETRY_DELAY_BASE = 2  # 指数退避基数

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
