"""
Streamlit Web 界面
提供友好的用户界面来管理汇率数据
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import logging

from scraper import ScraperManager
from storage import RateStorage

# 配置页面
st.set_page_config(
    page_title="ARS to USD Scraper",
    page_icon="💱",
    layout="wide"
)

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    st.title("💱 BNA 阿根廷兑美元汇率抓取器")
    st.markdown("---")
    
    # 初始化组件
    if 'scraper' not in st.session_state:
        st.session_state.scraper = ScraperManager()
    if 'storage' not in st.session_state:
        st.session_state.storage = RateStorage()
    
    # 侧边栏
    with st.sidebar:
        st.header("📅 数据回补")
        
        # 日期选择
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=30)
        
        start_date_input = st.date_input(
            "开始日期",
            value=start_date,
            max_value=end_date
        )
        
        end_date_input = st.date_input(
            "结束日期",
            value=end_date,
            max_value=end_date
        )
        
        # 回补按钮
        if st.button("🚀 开始回补", type="primary"):
            if start_date_input > end_date_input:
                st.error("开始日期不能晚于结束日期")
            else:
                run_backfill(start_date_input, end_date_input)
    
    # 主界面
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("📊 数据概览")
        display_stats()
    
    with col2:
        st.header("⚡ 快速操作")
        
        if st.button("📈 抓取昨天数据"):
            run_yesterday_scrape()
        
        if st.button("🔄 刷新状态"):
            st.rerun()
    
    # 数据表格
    display_recent_data()

def run_backfill(start_date, end_date):
    """执行数据回补"""
    start_str = start_date.strftime("%Y-%m-%d")
    end_str = end_date.strftime("%Y-%m-%d")
    
    st.info(f"开始回补数据: {start_str} 到 {end_str}")
    
    # 创建进度条
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # 计算总天数
        total_days = (end_date - start_date).days + 1
        current_day = 0
        
        # 执行抓取
        results = st.session_state.scraper.scrape_date_range(start_str, end_str)
        
        if not results:
            st.warning("没有抓取到任何数据")
            return
        
        # 保存数据
        success_count = 0
        for date, rate_sell, source in results:
            if st.session_state.storage.add_rate(date, rate_sell, source):
                success_count += 1
            
            current_day += 1
            progress = current_day / total_days
            progress_bar.progress(progress)
            status_text.text(f"处理中... {current_day}/{total_days}")
        
        progress_bar.progress(1.0)
        status_text.text("完成!")
        
        st.success(f"数据回补完成！成功 {success_count}/{len(results)} 条")
        
        # 自动刷新
        st.rerun()
        
    except Exception as e:
        st.error(f"回补过程中发生错误: {str(e)}")
        logger.error(f"回补错误: {e}")

def run_yesterday_scrape():
    """抓取昨天数据"""
    st.info("开始抓取昨天数据...")
    
    try:
        result = st.session_state.scraper.scrape_yesterday(fallback=True)
        
        if result:
            date, rate_sell, source = result
            
            if st.session_state.storage.add_rate(date, rate_sell, source):
                st.success(f"成功抓取并保存: {date} = {rate_sell} ({source})")
                st.rerun()
            else:
                st.error("数据保存失败")
        else:
            st.error("抓取失败")
            
    except Exception as e:
        st.error(f"抓取过程中发生错误: {str(e)}")
        logger.error(f"抓取错误: {e}")

def display_stats():
    """显示数据统计信息"""
    try:
        stats = st.session_state.storage.get_stats()
        
        if not stats or stats['total_records'] == 0:
            st.info("暂无数据")
            return
        
        # 统计卡片
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("总记录数", stats['total_records'])
        
        with col2:
            if stats['date_range']:
                date_range = f"{stats['date_range']['start']} 到 {stats['date_range']['end']}"
                st.metric("日期范围", date_range)
        
        with col3:
            if stats['sources']:
                total_sources = len(stats['sources'])
                st.metric("数据源数量", total_sources)
        
        # 数据源分布
        if stats['sources']:
            st.subheader("📈 数据源分布")
            source_df = pd.DataFrame([
                {"数据源": source, "记录数": count}
                for source, count in stats['sources'].items()
            ])
            st.bar_chart(source_df.set_index("数据源"))
        
    except Exception as e:
        st.error(f"获取统计信息失败: {str(e)}")
        logger.error(f"统计信息错误: {e}")

def display_recent_data():
    """显示所有数据表格"""
    try:
        # 获取所有数据用于下载
        all_data = st.session_state.storage.get_all_rates()
        
        if not all_data:
            st.info("暂无数据")
            return
        
        # 转换为DataFrame
        df_all = pd.DataFrame(all_data)
        
        # 格式化fetched_at列
        if 'fetched_at' in df_all.columns:
            df_all['fetched_at'] = pd.to_datetime(df_all['fetched_at']).dt.strftime('%Y-%m-%d %H:%M:%S')
        
        # 按日期排序（最新的在前）
        if 'date' in df_all.columns:
            df_all = df_all.sort_values('date', ascending=False)
        
        # 显示数据表格（限制显示前50条以避免界面过于拥挤）
        display_limit = min(50, len(df_all))
        df_display = df_all.head(display_limit)
        
        st.subheader(f"📋 数据表格 (显示最近{display_limit}条，共{len(df_all)}条)")
        
        st.dataframe(
            df_display,
            use_container_width=True,
            hide_index=True
        )
        
        if len(df_all) > display_limit:
            st.info(f"表格仅显示最近{display_limit}条记录，下载CSV可获取全部{len(df_all)}条数据")
        
        # 下载按钮 - 包含所有数据
        csv = df_all.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label=f"📥 下载完整CSV (共{len(df_all)}条记录)",
            data=csv,
            file_name=f"exchange_rates_full_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
        
    except Exception as e:
        st.error(f"获取最近数据失败: {str(e)}")
        logger.error(f"最近数据错误: {e}")

if __name__ == "__main__":
    main()
