import streamlit as st
import pandas as pd
import plotly.express as px
import datetime

# 1. 網頁基本設定
st.set_page_config(page_title="台中港交通流量分析系統", layout="wide")

st.title("🚢 港口擁擠預測與交通流量分析系統")
st.markdown("本系統由**交通流量分析小組**開發，整合航道船舶流量與統計數據。")

# 2. 側邊欄控制面板
with st.sidebar:
    st.header("⚙️ 系統控制")
    selected_port = st.selectbox("選擇分析港口", ["台中港", "高雄港", "基隆港"])
    predict_hours = st.slider("預測未來時間 (小時)", 6, 48, 24)
    
    st.markdown("---")
    st.markdown("### 交通流量分析小組")
    st.caption("負責內容：AIS 數據處理、流量與擁擠度分析")

# 3. 交通流量模擬數據
current_traffic = {
    "vessel_count": 45,
    "wait_count": 8,
    "congestion_index": "中度擁擠"
}

# 4. 即時指標看板
st.subheader(f"📊 {selected_port} 即時監控指標")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(label="港區內船舶總數", value=f"{current_traffic['vessel_count']} 艘")
with col2:
    st.metric(label="錨地等待船隻 (佇列)", value=f"{current_traffic['wait_count']} 艘", delta="+2 (過去1小時)", delta_color="inverse")
with col3:
    st.metric(label="今日累積進港船隻", value="12 艘")
with col4:
    st.metric(label="港口擁擠狀態評級", value=current_traffic['congestion_index'])

st.divider()

# 5. 地圖與統計圖表
col_map, col_chart = st.columns([1, 1])

with col_map:
    st.subheader("📍 航道動態觀測地圖 (模擬 AIS 點位)")
    port_coords = {
        "台中港": {"lat": [24.26, 24.27, 24.25, 24.28], "lon": [120.50, 120.51, 120.49, 120.48]},
        "高雄港": {"lat": [22.61, 22.62, 22.60, 22.59], "lon": [120.27, 120.28, 120.26, 120.25]},
        "基隆港": {"lat": [25.13, 25.14, 25.12, 25.15], "lon": [121.74, 121.75, 121.73, 121.72]}
    }
    map_data = pd.DataFrame(port_coords[selected_port])
    st.map(map_data)
    st.caption("註：地圖上的點代表船舶目前在航道與外海錨地的位置。")

with col_chart:
    st.subheader("📈 歷史交通流量變化趨勢 (過去 12 小時)")
    time_slots = [datetime.datetime.now() - datetime.timedelta(hours=i) for i in range(12)]
    df_trend = pd.DataFrame({
        "時間": time_slots[::-1],
        "船舶數量 (艘)": [25, 28, 30, 35, 42, 45, 43, 38, 32, 30, 34, 45]
    })
    fig = px.line(df_trend, x="時間", y="船舶數量 (艘)", title="港區航道船舶動態流量")
    st.plotly_chart(fig, use_container_width=True)