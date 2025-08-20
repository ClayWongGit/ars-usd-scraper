"""
CSV 存储模块
负责数据的存储、验证和去重
"""

import os
import csv
import logging
from datetime import datetime
from typing import List, Tuple, Optional
import pandas as pd

from constants import DATA_DIR, RATES_CSV, MIN_RATE

logger = logging.getLogger(__name__)


class RateStorage:
    """汇率数据存储管理类"""
    
    def __init__(self):
        self._ensure_data_dir()
        self._ensure_csv_exists()
    
    def _ensure_data_dir(self):
        """确保数据目录存在"""
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)
            logger.info(f"创建数据目录: {DATA_DIR}")
    
    def _ensure_csv_exists(self):
        """确保CSV文件存在，如果不存在则创建"""
        if not os.path.exists(RATES_CSV):
            self._create_csv()
            logger.info(f"创建CSV文件: {RATES_CSV}")
    
    def _create_csv(self):
        """创建CSV文件并写入表头"""
        headers = ['date', 'rate_sell', 'source', 'fetched_at']
        with open(RATES_CSV, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
    
    def add_rate(self, date: str, rate_sell: float, source: str) -> bool:
        """
        添加汇率数据
        
        Args:
            date: 日期 (YYYY-MM-DD)
            rate_sell: 卖出价
            source: 数据源
            
        Returns:
            bool: 是否成功添加
        """
        # 验证数据
        if rate_sell <= MIN_RATE:
            logger.warning(f"汇率值无效: {rate_sell} <= {MIN_RATE}, 拒绝写入")
            return False
        
        if not self._is_valid_date(date):
            logger.warning(f"日期格式无效: {date}")
            return False
        
        # 检查是否已存在相同日期的数据
        if self._date_exists(date):
            logger.info(f"日期 {date} 已存在，将更新")
            self._remove_date(date)
        
        # 写入新数据
        fetched_at = datetime.now().isoformat()
        try:
            with open(RATES_CSV, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([date, rate_sell, source, fetched_at])
            logger.info(f"成功添加汇率数据: {date} = {rate_sell} ({source})")
            return True
        except Exception as e:
            logger.error(f"写入CSV失败: {e}")
            return False
    
    def _is_valid_date(self, date: str) -> bool:
        """验证日期格式"""
        try:
            datetime.strptime(date, "%Y-%m-%d")
            return True
        except ValueError:
            return False
    
    def _date_exists(self, date: str) -> bool:
        """检查日期是否已存在"""
        try:
            df = pd.read_csv(RATES_CSV)
            return date in df['date'].values
        except Exception:
            return False
    
    def _remove_date(self, date: str):
        """移除指定日期的数据"""
        try:
            df = pd.read_csv(RATES_CSV)
            df = df[df['date'] != date]
            df.to_csv(RATES_CSV, index=False)
        except Exception as e:
            logger.error(f"移除日期 {date} 失败: {e}")
    
    def get_recent_rates(self, limit: int = 10) -> List[Tuple]:
        """获取最近的汇率数据"""
        try:
            df = pd.read_csv(RATES_CSV)
            if df.empty:
                return []
            
            # 按fetched_at排序，获取最新的数据
            df['fetched_at'] = pd.to_datetime(df['fetched_at'])
            df = df.sort_values('fetched_at', ascending=False)
            
            recent_data = df.head(limit)
            return recent_data.to_dict('records')
        except Exception as e:
            logger.error(f"读取最近汇率数据失败: {e}")
            return []
    
    def get_all_rates(self) -> List[Tuple]:
        """获取所有汇率数据"""
        try:
            df = pd.read_csv(RATES_CSV)
            if df.empty:
                return []
            
            # 按日期排序，最新的在前
            df = df.sort_values('date', ascending=False)
            
            return df.to_dict('records')
        except Exception as e:
            logger.error(f"读取所有汇率数据失败: {e}")
            return []
    
    def get_date_range(self, start_date: str, end_date: str) -> List[Tuple]:
        """获取指定日期范围内的汇率数据"""
        try:
            df = pd.read_csv(RATES_CSV)
            if df.empty:
                return []
            
            # 过滤日期范围
            mask = (df['date'] >= start_date) & (df['date'] <= end_date)
            filtered_df = df.loc[mask]
            
            return filtered_df.to_dict('records')
        except Exception as e:
            logger.error(f"读取日期范围数据失败: {e}")
            return []
    
    def get_stats(self) -> dict:
        """获取存储统计信息"""
        try:
            df = pd.read_csv(RATES_CSV)
            if df.empty:
                return {
                    'total_records': 0,
                    'date_range': None,
                    'sources': {}
                }
            
            stats = {
                'total_records': len(df),
                'date_range': {
                    'start': df['date'].min(),
                    'end': df['date'].max()
                },
                'sources': df['source'].value_counts().to_dict()
            }
            return stats
        except Exception as e:
            logger.error(f"获取统计信息失败: {e}")
            return {}
