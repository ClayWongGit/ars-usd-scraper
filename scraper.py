"""
抓取器核心模块
实现两个数据源的抓取逻辑
"""

import re
import time
import logging
from datetime import datetime, timedelta
from typing import Optional, Tuple
import requests
from bs4 import BeautifulSoup
from dateutil import parser

from constants import (
    VALORHOY_URL, HISTORICO_URL, DOLLAR_USA_TEXT, VENTA_TEXT, FECHA_TEXT,
    SOURCE_VALORHOY, SOURCE_HISTORICO, REQUEST_TIMEOUT, MAX_RETRIES,
    RETRY_DELAY_BASE, USER_AGENT, ARGENTINA_DATE_FORMAT
)

logger = logging.getLogger(__name__)


class BaseScraper:
    """抓取器基类"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': USER_AGENT,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'es-AR,es;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
    
    def _make_request(self, url: str, params: Optional[dict] = None) -> Optional[requests.Response]:
        """发送HTTP请求，支持重试和指数退避"""
        for attempt in range(MAX_RETRIES):
            try:
                response = self.session.get(
                    url, 
                    params=params, 
                    timeout=REQUEST_TIMEOUT
                )
                
                if response.status_code == 200:
                    return response
                elif response.status_code >= 500:
                    logger.warning(f"服务器错误 {response.status_code}，尝试重试 {attempt + 1}/{MAX_RETRIES}")
                else:
                    logger.error(f"HTTP错误 {response.status_code}: {response.text}")
                    return None
                    
            except requests.exceptions.Timeout:
                logger.warning(f"请求超时，尝试重试 {attempt + 1}/{MAX_RETRIES}")
            except requests.exceptions.RequestException as e:
                logger.warning(f"请求异常: {e}，尝试重试 {attempt + 1}/{MAX_RETRIES}")
            
            # 指数退避
            if attempt < MAX_RETRIES - 1:
                delay = RETRY_DELAY_BASE ** attempt
                logger.info(f"等待 {delay} 秒后重试...")
                time.sleep(delay)
        
        logger.error(f"请求失败，已重试 {MAX_RETRIES} 次")
        return None
    
    def _parse_rate_value(self, rate_text: str) -> Optional[float]:
        """解析汇率值，兼容不同格式"""
        if not rate_text:
            return None
        
        # 清理文本
        rate_text = rate_text.strip()
        
        # 移除千分位分隔符（阿根廷格式：1.292,5000）
        if ',' in rate_text and '.' in rate_text:
            # 阿根廷格式：1.292,5000 -> 1292.5000
            parts = rate_text.split(',')
            if len(parts) == 2:
                integer_part = parts[0].replace('.', '')
                decimal_part = parts[1]
                rate_text = f"{integer_part}.{decimal_part}"
        
        # 移除所有非数字和小数点字符
        rate_text = re.sub(r'[^\d.]', '', rate_text)
        
        try:
            rate = float(rate_text)
            return rate if rate > 0 else None
        except ValueError:
            logger.warning(f"无法解析汇率值: {rate_text}")
            return None


class ValorHoySource(BaseScraper):
    """ValorHoy 数据源抓取器"""
    
    def scrape(self) -> Optional[Tuple[str, float, str]]:
        """
        抓取 ValorHoy 页面数据
        
        Returns:
            Tuple[date, rate_sell, source] 或 None
        """
        logger.info("开始抓取 ValorHoy 数据源...")
        
        response = self._make_request(VALORHOY_URL)
        if not response:
            logger.error("ValorHoy 请求失败")
            return None
        
        try:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 查找日期 - 新的模式匹配
            date_element = soup.find(string=re.compile(r"Fecha:\s*\d{1,2}/\d{1,2}/\d{4}"))
            if not date_element:
                logger.error("未找到日期信息")
                return None
            
            # 提取日期 - 支持单数字日期/月份
            date_match = re.search(r'(\d{1,2}/\d{1,2}/\d{4})', date_element)
            if not date_match:
                logger.error("日期格式解析失败")
                return None
            
            argentina_date = date_match.group(1)
            # 转换为标准格式
            date_obj = datetime.strptime(argentina_date, "%d/%m/%Y")
            date = date_obj.strftime("%Y-%m-%d")
            
            # 查找表格中的美元行
            tables = soup.find_all('table')
            rate_sell = None
            
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    cell_texts = [cell.get_text().strip() for cell in cells]
                    
                    # 检查是否包含美元行
                    if len(cell_texts) >= 3 and DOLLAR_USA_TEXT in cell_texts:
                        # 找到美元行，获取卖出价（第三列，索引2）
                        try:
                            rate_text = cell_texts[2]  # Venta 列
                            rate_sell = self._parse_rate_value(rate_text)
                            break
                        except (IndexError, ValueError) as e:
                            logger.warning(f"解析美元行失败: {e}")
                            continue
                
                if rate_sell is not None:
                    break
            
            if rate_sell is None:
                logger.error("未找到卖出价")
                return None
            
            logger.info(f"ValorHoy 抓取成功: {date} = {rate_sell}")
            return date, rate_sell, SOURCE_VALORHOY
            
        except Exception as e:
            logger.error(f"ValorHoy 解析失败: {e}")
            return None


class HistoricoSource(BaseScraper):
    """Historico 数据源抓取器"""
    
    def scrape(self, target_date: str) -> Optional[Tuple[str, float, str]]:
        """
        抓取 Historico 页面数据
        
        Args:
            target_date: 目标日期 (YYYY-MM-DD)
            
        Returns:
            Tuple[date, rate_sell, source] 或 None
        """
        logger.info(f"开始抓取 Historico 数据源，目标日期: {target_date}")
        
        # 转换为阿根廷日期格式
        try:
            date_obj = datetime.strptime(target_date, "%Y-%m-%d")
            argentina_date = date_obj.strftime("%d/%m/%Y")
        except ValueError:
            logger.error(f"日期格式无效: {target_date}")
            return None
        
        params = {
            'fecha': argentina_date,
            'filtroDolar': '1',
            'id': 'monedas'
        }
        
        response = self._make_request(HISTORICO_URL, params)
        if not response:
            logger.error("Historico 请求失败")
            return None
        
        try:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 查找表格
            tables = soup.find_all('table')
            rate_sell = None
            
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    cell_texts = [cell.get_text().strip() for cell in cells]
                    
                    # 检查是否是美元行且包含目标日期
                    if len(cell_texts) >= 4 and DOLLAR_USA_TEXT in cell_texts:
                        # 检查日期列（第4列，索引3）
                        date_cell = cell_texts[3]
                        
                        # 匹配目标日期（支持不同格式）
                        # 生成所有可能的日期格式
                        day = date_obj.day
                        month = date_obj.month
                        year = date_obj.year
                        
                        possible_formats = [
                            f"{day:02d}/{month:02d}/{year}",  # 19/08/2024
                            f"{day}/{month}/{year}",          # 19/8/2024
                            f"{day:02d}/{month}/{year}",      # 19/8/2024
                            f"{day}/{month:02d}/{year}",      # 19/08/2024
                            target_date,                      # 2024-08-19
                            argentina_date                    # 原始输入格式
                        ]
                        
                        date_match = False
                        for date_format in possible_formats:
                            if date_format in date_cell:
                                date_match = True
                                break
                        
                        if date_match:
                            
                            try:
                                # 获取卖出价（第3列，索引2）
                                rate_text = cell_texts[2]  # Venta 列
                                rate_sell = self._parse_rate_value(rate_text)
                                if rate_sell is not None:
                                    logger.info(f"Historico 抓取成功: {target_date} = {rate_sell}")
                                    return target_date, rate_sell, SOURCE_HISTORICO
                            except (IndexError, ValueError) as e:
                                logger.warning(f"解析历史数据行失败: {e}")
                                continue
            
            logger.error(f"未找到目标日期 {target_date} 的数据行")
            return None
            
        except Exception as e:
            logger.error(f"Historico 解析失败: {e}")
            return None


class ScraperManager:
    """抓取器管理器"""
    
    def __init__(self):
        self.valorhoy_source = ValorHoySource()
        self.historico_source = HistoricoSource()
    
    def scrape_yesterday(self, fallback: bool = False) -> Optional[Tuple[str, float, str]]:
        """
        抓取昨天数据，优先使用 ValorHoySource
        
        Args:
            fallback: 是否在失败时使用 HistoricoSource
            
        Returns:
            Tuple[date, rate_sell, source] 或 None
        """
        # 计算昨天的日期
        yesterday = datetime.now() - timedelta(days=1)
        yesterday_str = yesterday.strftime("%Y-%m-%d")
        
        logger.info(f"尝试抓取昨天 ({yesterday_str}) 的数据...")
        
        # 优先使用 ValorHoySource
        result = self.valorhoy_source.scrape()
        if result:
            return result
        
        if fallback:
            logger.info("ValorHoy 失败，尝试使用 Historico 作为备选...")
            result = self.historico_source.scrape(yesterday_str)
            if result:
                return result
        
        logger.error("所有数据源都失败了")
        return None
    
    def scrape_date_range(self, start_date: str, end_date: str) -> list:
        """
        抓取指定日期范围的数据
        
        Args:
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            
        Returns:
            list: 成功抓取的数据列表
        """
        logger.info(f"开始抓取日期范围: {start_date} 到 {end_date}")
        
        start_obj = datetime.strptime(start_date, "%Y-%m-%d")
        end_obj = datetime.strptime(end_date, "%Y-%m-%d")
        
        results = []
        current_date = start_obj
        
        while current_date <= end_obj:
            current_date_str = current_date.strftime("%Y-%m-%d")
            
            try:
                result = self.historico_source.scrape(current_date_str)
                if result:
                    results.append(result)
                    logger.info(f"成功抓取 {current_date_str}: {result[1]}")
                else:
                    logger.warning(f"抓取 {current_date_str} 失败")
            except Exception as e:
                logger.error(f"抓取 {current_date_str} 时发生异常: {e}")
            
            current_date += timedelta(days=1)
            
            # 避免请求过于频繁
            time.sleep(0.5)
        
        logger.info(f"日期范围抓取完成，成功 {len(results)} 条")
        return results
