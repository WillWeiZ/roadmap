import streamlit as st
import pandas as pd
import folium
from streamlit.components.v1 import html

def test_map():
    st.title("地图测试")
    
    # 读取数据
    df = pd.read_excel("黑龙江数据V20250609.xlsx")
    
    if len(df) > 0:
        # 计算地图中心点
        center_lat = df['纬度'].mean()
        center_lon = df['经度'].mean()
        
        st.write(f"数据行数: {len(df)}")
        st.write(f"地图中心: {center_lat:.2f}, {center_lon:.2f}")
        
        # 创建简单地图
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=8,
            tiles="OpenStreetMap"
        )
        
        # 只添加前100个门店避免过载
        for idx, row in df.head(100).iterrows():
            folium.CircleMarker(
                location=[row['纬度'], row['经度']],
                radius=5,
                popup=row['门店名称'],
                color='red',
                fill=True,
                fillColor='red',
                fillOpacity=0.7
            ).add_to(m)
        
        # 显示地图
        map_html = m._repr_html_()
        st.components.v1.html(map_html, height=600)
        
        st.success("地图加载成功！")
    else:
        st.error("数据加载失败")

if __name__ == "__main__":
    test_map() 