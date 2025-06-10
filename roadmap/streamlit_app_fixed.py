import streamlit as st
import pandas as pd
import folium
from folium import plugins
import numpy as np
from streamlit.components.v1 import html
import plotly.express as px
import plotly.graph_objects as go

# 设置页面配置
st.set_page_config(
    page_title="黑龙江门店数据分析平台",
    page_icon="🏪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .filter-container {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #e0e0e0;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """加载Excel数据"""
    try:
        df = pd.read_excel("黑龙江数据V20250609.xlsx")
        return df
    except Exception as e:
        st.error(f"数据加载失败: {e}")
        return None

def create_folium_map(df_filtered):
    """创建Folium地图"""
    if df_filtered.empty:
        return None
    
    try:
        # 计算地图中心点
        center_lat = df_filtered['纬度'].mean()
        center_lon = df_filtered['经度'].mean()
        
        # 创建地图（使用默认图层）
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=8,
            tiles="OpenStreetMap"
        )
        
        # 添加稳定可靠的地图图层
        folium.TileLayer('cartodbpositron', name='CartoDB Positron').add_to(m)
        
        # 添加全屏插件
        folium.plugins.Fullscreen(
            position="topright",
            title="Expand me",
            title_cancel="Exit me",
            force_separate_button=True,
        ).add_to(m)
        
        # 定义渠道颜色
        channel_colors = {
            'MM': 'red',
            'Grocery': 'blue', 
            'CVS': 'green',
            'HSM': 'orange'
        }
        
        # 为每个渠道创建FeatureGroup
        channel_groups = {}
        for channel in df_filtered['一级渠道'].unique():
            channel_groups[channel] = folium.FeatureGroup(name=f"{channel} 渠道", show=True)
        
        # 按渠道分组添加门店标记
        for channel, group in df_filtered.groupby('一级渠道'):
            if channel in channel_groups:
                feature_group = channel_groups[channel]
                color = channel_colors.get(channel, 'gray')
                
                for idx, row in group.iterrows():
                    # 检查是否有宝洁SEQ
                    has_pg_seq = pd.notna(row['宝洁SEQ']) and str(row['宝洁SEQ']).strip() != ''
                    
                    # 创建弹窗内容
                    popup_content = f"""
                    <div style="width: 300px;">
                        <h4>{row['门店名称']} {'🚩' if has_pg_seq else ''}</h4>
                        <p><strong>门店编码:</strong> {row['门店编码']}</p>
                        <p><strong>地址:</strong> {row['地址']}</p>
                        <p><strong>城市:</strong> {row['市']} - {row['区县']}</p>
                        <p><strong>渠道:</strong> {row['一级渠道']}</p>
                        <p><strong>城市级别:</strong> {row['城市级别']}级</p>
                        <p><strong>卖力值:</strong> {row['卖力值']}</p>
                        {f"<p><strong>连锁系统:</strong> {row['所属连锁系统']}</p>" if pd.notna(row['所属连锁系统']) else ""}
                        {f"<p><strong>宝洁SEQ:</strong> {row['宝洁SEQ']} 🚩</p>" if has_pg_seq else ""}
                    </div>
                    """
                    
                    # 缩小圆点，根据卖力值决定图标大小
                    radius = max(2, min(6, row['卖力值'] / 15))
                    
                    # 添加门店圆点标记
                    folium.CircleMarker(
                        location=[row['纬度'], row['经度']],
                        radius=radius,
                        popup=folium.Popup(popup_content, max_width=300),
                        tooltip=f"{row['门店名称']} - {row['一级渠道']} {'🚩' if has_pg_seq else ''}",
                        color=color,
                        fill=True,
                        fillColor=color,
                        fillOpacity=0.7,
                        weight=1
                    ).add_to(feature_group)
                    
                    # 如果有宝洁SEQ，添加更大的小旗子标记
                    if has_pg_seq:
                        folium.Marker(
                            location=[row['纬度'], row['经度']],
                            icon=folium.DivIcon(
                                html='<div style="font-size: 18px; text-shadow: 1px 1px 2px rgba(0,0,0,0.5);">🚩</div>',
                                icon_size=(24, 24),
                                icon_anchor=(12, 24)
                            ),
                            tooltip=f"宝洁覆盖: {row['门店名称']}"
                        ).add_to(feature_group)
                
                # 将FeatureGroup添加到地图
                m.add_child(feature_group)
        
        # 添加热力图图层（可选）
        if len(df_filtered) > 10:
            heat_data = [[row['纬度'], row['经度'], row['卖力值']] for idx, row in df_filtered.iterrows()]
            heat_group = folium.FeatureGroup(name="卖力值热力图", show=False)
            plugins.HeatMap(heat_data).add_to(heat_group)
            m.add_child(heat_group)
        
        # 添加LayerControl
        folium.LayerControl(position='topright').add_to(m)
        
        return m
        
    except Exception as e:
        st.error(f"地图创建失败: {e}")
        return None

def main():
    # 页面标题
    st.markdown('<h1 class="main-header">🏪 黑龙江门店数据分析平台</h1>', unsafe_allow_html=True)
    
    # 加载数据
    df = load_data()
    if df is None:
        st.stop()
    
    # 侧边栏筛选器
    st.sidebar.markdown("## 📊 数据筛选")
    
    with st.sidebar:
        st.markdown('<div class="filter-container">', unsafe_allow_html=True)
        
        # 城市筛选
        cities = ['全部'] + sorted(df['市'].unique().tolist())
        selected_city = st.selectbox("选择城市", cities)
        
        # 渠道筛选
        channels = ['全部'] + sorted(df['一级渠道'].unique().tolist())
        selected_channel = st.selectbox("选择渠道", channels)
        
        # 城市级别筛选
        city_levels = ['全部'] + sorted(df['城市级别'].unique().tolist())
        selected_level = st.selectbox("城市级别", city_levels)
        
        # 卖力值范围筛选
        min_value = float(df['卖力值'].min())
        max_value = float(df['卖力值'].max())
        value_range = st.slider(
            "卖力值范围", 
            min_value=min_value, 
            max_value=max_value, 
            value=(min_value, max_value),
            step=0.1
        )
        
        st.info("💡 地图图层和渠道类型都可以通过地图右上角的图层控制面板进行选择和开关")
        st.info("🔍 点击地图右上角的全屏按钮可以让地图全屏显示，方便详细查看")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # 应用筛选条件
    df_filtered = df.copy()
    
    if selected_city != '全部':
        df_filtered = df_filtered[df_filtered['市'] == selected_city]
    
    if selected_channel != '全部':
        df_filtered = df_filtered[df_filtered['一级渠道'] == selected_channel]
    
    if selected_level != '全部':
        df_filtered = df_filtered[df_filtered['城市级别'] == selected_level]
    
    df_filtered = df_filtered[
        (df_filtered['卖力值'] >= value_range[0]) & 
        (df_filtered['卖力值'] <= value_range[1])
    ]
    
    # 主要指标展示
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="📍 门店总数",
            value=f"{len(df_filtered):,}",
            delta=f"占总数 {len(df_filtered)/len(df)*100:.1f}%"
        )
    
    with col2:
        avg_score = df_filtered['卖力值'].mean() if len(df_filtered) > 0 else 0
        st.metric(
            label="📈 平均卖力值",
            value=f"{avg_score:.2f}",
            delta=f"vs 总体 {df['卖力值'].mean():.2f}"
        )
    
    with col3:
        unique_cities = df_filtered['市'].nunique()
        st.metric(
            label="🏙️ 覆盖城市",
            value=f"{unique_cities}",
            delta=f"总共 {df['市'].nunique()} 城市"
        )
    
    with col4:
        unique_districts = df_filtered['区县'].nunique()
        st.metric(
            label="🏘️ 覆盖区县",
            value=f"{unique_districts}",
            delta=f"总共 {df['区县'].nunique()} 区县"
        )
    
    # 地图全屏展示
    st.markdown("### 🗺️ 门店地理分布")
    
    if len(df_filtered) > 0:
        # 创建地图
        folium_map = create_folium_map(df_filtered)
        
        if folium_map:
            # 将地图保存为HTML并嵌入，增加高度
            map_html = folium_map._repr_html_()
            st.components.v1.html(map_html, height=800)
            
            # 统计有宝洁SEQ的门店数量
            pg_seq_count = df_filtered['宝洁SEQ'].notna().sum()
            
            # 显示当前筛选结果和使用说明
            col_info1, col_info2 = st.columns(2)
            with col_info1:
                st.info(f"🔍 当前数据包含 {len(df_filtered):,} 家门店")
            with col_info2:
                st.info(f"🚩 其中 {pg_seq_count:,} 家门店已有宝洁SEQ覆盖")
            
            st.success("🎯 使用地图右上角的图层控制面板可以切换地图样式和开关不同渠道类型的显示")
        else:
            st.warning("无法创建地图，请检查筛选条件")
    else:
        st.warning("根据当前筛选条件，没有找到匹配的门店数据")
    
    # 数据统计图表 - 三列布局
    st.markdown("### 📊 数据统计")
    
    if len(df_filtered) > 0:
        chart_col1, chart_col2, chart_col3 = st.columns(3)
        
        with chart_col1:
            # 渠道分布饼图
            st.markdown("#### 渠道分布")
            channel_counts = df_filtered['一级渠道'].value_counts()
            fig_pie = px.pie(
                values=channel_counts.values,
                names=channel_counts.index,
                title="渠道分布"
            )
            fig_pie.update_layout(height=400)
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with chart_col2:
            # 城市级别分布
            st.markdown("#### 城市级别分布")
            level_counts = df_filtered['城市级别'].value_counts().sort_index()
            fig_bar = px.bar(
                x=level_counts.index,
                y=level_counts.values,
                title="城市级别分布",
                labels={'x': '城市级别', 'y': '门店数量'}
            )
            fig_bar.update_layout(height=400)
            st.plotly_chart(fig_bar, use_container_width=True)
        
        with chart_col3:
            # 卖力值分布直方图
            st.markdown("#### 卖力值分布")
            fig_hist = px.histogram(
                df_filtered,
                x='卖力值',
                nbins=20,
                title="卖力值分布",
                labels={'x': '卖力值', 'y': '门店数量'}
            )
            fig_hist.update_layout(height=400)
            st.plotly_chart(fig_hist, use_container_width=True)
    
    # 详细数据表格
    st.markdown("### 📋 详细数据")
    
    if len(df_filtered) > 0:
        # 选择要显示的列
        display_columns = [
            '门店编码', '门店名称', '市', '区县', '地址', 
            '一级渠道', '城市级别', '卖力值', '所属连锁系统'
        ]
        
        # 数据表格
        st.dataframe(
            df_filtered[display_columns].head(100),
            use_container_width=True,
            height=400
        )
        
        if len(df_filtered) > 100:
            st.info(f"表格仅显示前100条记录，总共有 {len(df_filtered):,} 条记录")
        
        # 下载按钮
        csv = df_filtered.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label="📥 下载筛选后的数据 (CSV)",
            data=csv,
            file_name=f"门店数据_{selected_city}_{selected_channel}.csv",
            mime="text/csv"
        )
    
    # 页脚信息
    st.markdown("---")
    st.markdown(
        """
        <div style="text-align: center; color: #666; padding: 1rem;">
            📊 黑龙江门店数据分析平台 | 数据更新时间: 2025-06-09
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main() 