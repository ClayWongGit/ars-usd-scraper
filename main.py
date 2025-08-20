"""
CLI 主程序
使用 Typer 实现命令行界面
"""

import logging
import sys
from datetime import datetime, timedelta
from typing import Optional
import typer

from scraper import ScraperManager
from storage import RateStorage
from constants import SOURCE_VALORHOY, SOURCE_HISTORICO

# 创建 Typer 应用
app = typer.Typer(help="BNA 阿根廷兑美元汇率抓取器")

# 配置日志
def setup_logging(debug: bool = False):
    """配置日志级别"""
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

@app.command()
def yesterday(
    fallback: bool = typer.Option(
        False, 
        "--fallback", 
        help="在 ValorHoy 失败时使用 Historico 作为备选"
    ),
    debug: bool = typer.Option(False, "--debug", help="启用调试模式"),
    dry_run: bool = typer.Option(False, "--dry-run", help="仅显示，不保存数据")
):
    """抓取昨天的汇率数据"""
    setup_logging(debug)
    logger = logging.getLogger(__name__)
    
    logger.info("开始抓取昨天数据...")
    
    # 初始化组件
    scraper = ScraperManager()
    storage = RateStorage()
    
    # 抓取数据
    result = scraper.scrape_yesterday(fallback=fallback)
    
    if not result:
        logger.error("抓取失败")
        raise typer.Exit(1)
    
    date, rate_sell, source = result
    logger.info(f"抓取成功: {date} = {rate_sell} ({source})")
    
    if dry_run:
        logger.info("DRY RUN 模式，不保存数据")
        return
    
    # 保存数据
    if storage.add_rate(date, rate_sell, source):
        logger.info("数据保存成功")
    else:
        logger.error("数据保存失败")
        raise typer.Exit(1)

@app.command()
def backfill(
    start_date: str = typer.Argument(..., help="开始日期 (YYYY-MM-DD)"),
    end_date: str = typer.Argument(..., help="结束日期 (YYYY-MM-DD)"),
    debug: bool = typer.Option(False, "--debug", help="启用调试模式"),
    dry_run: bool = typer.Option(False, "--dry-run", help="仅显示，不保存数据")
):
    """回补指定日期范围的汇率数据"""
    setup_logging(debug)
    logger = logging.getLogger(__name__)
    
    # 验证日期格式
    try:
        start_obj = datetime.strptime(start_date, "%Y-%m-%d")
        end_obj = datetime.strptime(end_date, "%Y-%m-%d")
        
        if start_obj > end_obj:
            logger.error("开始日期不能晚于结束日期")
            raise typer.Exit(1)
            
    except ValueError:
        logger.error("日期格式无效，请使用 YYYY-MM-DD 格式")
        raise typer.Exit(1)
    
    logger.info(f"开始回补日期范围: {start_date} 到 {end_date}")
    
    # 初始化组件
    scraper = ScraperManager()
    storage = RateStorage()
    
    # 抓取数据
    results = scraper.scrape_date_range(start_date, end_date)
    
    if not results:
        logger.warning("没有抓取到任何数据")
        return
    
    logger.info(f"成功抓取 {len(results)} 条数据")
    
    if dry_run:
        logger.info("DRY RUN 模式，不保存数据")
        for date, rate_sell, source in results:
            logger.info(f"  {date}: {rate_sell} ({source})")
        return
    
    # 保存数据
    success_count = 0
    for date, rate_sell, source in results:
        if storage.add_rate(date, rate_sell, source):
            success_count += 1
        else:
            logger.warning(f"保存 {date} 数据失败")
    
    logger.info(f"数据保存完成，成功 {success_count}/{len(results)} 条")

@app.command()
def status(
    debug: bool = typer.Option(False, "--debug", help="启用调试模式")
):
    """显示当前数据状态"""
    setup_logging(debug)
    logger = logging.getLogger(__name__)
    
    storage = RateStorage()
    stats = storage.get_stats()
    
    if not stats:
        logger.info("暂无数据")
        return
    
    logger.info("数据状态:")
    logger.info(f"  总记录数: {stats['total_records']}")
    
    if stats['date_range']:
        logger.info(f"  日期范围: {stats['date_range']['start']} 到 {stats['date_range']['end']}")
    
    if stats['sources']:
        logger.info("  数据源分布:")
        for source, count in stats['sources'].items():
            logger.info(f"    {source}: {count} 条")
    
    # 显示最近的数据
    recent_data = storage.get_recent_rates(5)
    if recent_data:
        logger.info("  最近数据:")
        for record in recent_data:
            logger.info(f"    {record['date']}: {record['rate_sell']} ({record['source']})")

if __name__ == "__main__":
    app()
