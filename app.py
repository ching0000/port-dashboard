import streamlit as st
import pandas as pd
import plotly.express as px
import datetime
import requests

# 1. 網頁基本設定
st.set_page_config(page_title="印度港口交通與天氣預測系統", layout="wide")

st.title("🚢 Indian Port Congestion & Weather Forecasting System")
st.markdown("本系統整合印度主要港口的船舶流量，並透過**即時與未來 3 天天氣預測**來評估港口塞船風險。")

# 2. 側邊欄控制面板
with st.sidebar:
    st.header("⚙️ Port Control Panel")
    selected_port = st.selectbox(
        "Select Port (選擇印度港口)", 
        ["Mumbai (孟買港)", "Chennai (清奈港)", "Kolkata (加爾各答港)", "Kandla (坎德拉港)"]
    )
    st.markdown("---")
    st.markdown("### 交通流量分析小組")
    st.caption("Project: Indian Port Weather & Congestion Predictor")

# 3. 印度港口經緯度對照表
port_mapping = {
    "Mumbai (孟買港)": {"lat": 18.95, "lon": 72.82, "fullname": "Mumbai"},
    "Chennai (清奈港)": {"lat": 13.09, "lon": 80.30, "fullname": "Chennai"},
    "Kolkata (加爾開各答港)": {"lat": 22.54, "lon": 88.31, "fullname": "Kolkata"},
    "Kandla (坎德拉港)": {"lat": 23.01, "lon": 70.22, "fullname": "Kandla"}
}
coords = port_mapping[selected_port]

# 4. 串接 API 抓取即時天氣 + 未來 3 天預測
@st.cache_data(ttl=600)
def fetch_weather_and_forecast(lat, lon):
    # 同時請求即時天氣 (current_weather) 與每日天氣預測 (daily=temperature_2m_max,windspeed_10m_max,rain_sum)
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&daily=temperature_2m_max,windspeed_10m_max,rain_sum&timezone=auto"
    try:
        res = requests.get(url).json()
        current = res["current_weather"]
        daily = res["daily"]
        return {
            "current_temp": current['temperature'],
            "current_wind": current['windspeed'],
            "forecast_df": pd.DataFrame({
                "日期 (Date)": daily["time"][:3],
                "最高氣溫 (°C)": daily["temperature_2m_max"][:3],
                "最大風速 (km/h)": daily["windspeed_10m_max"][:3],
                "累積降雨量 (mm)": daily["rain_sum"][:3]
            })
        }
    except:
        # API 斷線時的備用模擬數據
        today = datetime.date.today()
        return {
            "current_temp": 28.5,
            "current_wind": 14.2,
            "forecast_df": pd.DataFrame({
                "日期 (Date)": [str(today), str(today + datetime.timedelta(days=1)), str(today + datetime.timedelta(days=2))],
                "最高氣溫 (°C)": [29.0, 30.2, 27.8],
                "最大風速 (km/h)": [15.0, 22.4, 35.1],
                "累積降雨量 (mm)": [0.0, 5.2, 45.0]
            })
        }

weather_data = fetch_weather_and_forecast(coords["lat"], coords["lon"])

# 5. 塞船風險評估邏輯 (根據當前風速與預測最大風速)
current_wind = weather_data["current_temp"] # 抓取風速數字
max_forecast_wind = weather_data["forecast_df"]["最大風速 (km/h)"].max()

if max_forecast_wind > 30 or weather_data["forecast_df"]["累積降雨量 (mm)"].max() > 30:
    risk_level = "🚨 HIGH RISK (高風險塞船預警)"
    risk_color = "error"
    risk_desc = "注意：未來 3 天內預測有強風或豪雨，可能導致引水人無法出海帶船，港區塞船風險極高！"
else:
    risk_level = "✅ LOW RISK (低風險營運正常)"
    risk_color = "success"
    risk_desc = "天氣預報良好，風速與降雨量皆在正常安全範圍內，港口營運順暢。"

# 6. 網頁看板呈現
st.subheader(f"📊 Live Indicators & Risk Assessment: {selected_port}")

# 顯示風險警報標籤
if risk_color == "error":
    st.error(f"**港口狀態：{risk_level}** \n\n {risk_desc}")
else:
    st.success(f"**港口狀態：{risk_level}** \n\n {risk_desc}")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(label="Vessels in Port (當前港內船隻)", value="64 Ships")
with col2:
    st.metric(label="Waiting Queue (錨地佇列)", value="11 Ships")
with col3:
    st.metric(label="Live Temp (即時氣溫)", value=f"{weather_data['current_temp']} °C")
with col4:
    st.metric(label="Live Wind Speed (即時風速)", value=f"{weather_data['current_wind']} km/h")

st.divider()

# 7. 地圖與預報圖表
col_map, col_chart = st.columns([1, 1])

with col_map:
    st.subheader("📍 Port Location Map (港區地理位置)")
    map_data = pd.DataFrame({"lat": [coords["lat"]], "lon": [coords["lon"]]})
    st.map(map_data)
    
    # 呈現未來 3 天的天氣預報表格
    st.markdown("### 📅 3-Day Weather Forecast (未來 3 天天氣預報)")
    st.dataframe(weather_data["forecast_df"], use_container_width=True)

with col_chart:
    st.subheader("📈 3-Day Wind Speed Forecast (未來風速預測趨勢)")
    # 將未來風速畫成柱狀圖，方便一眼看出哪一天風太大會塞船
    fig = px.bar(
        weather_data["forecast_df"], 
        x="日期 (Date)", 
        y="最大風速 (km/h)", 
        title="趨勢預測：風速超過 30 km/h 將影響貨輪進出港",
        color="最大風速 (km/h)",
        color_continuous_scale="Reds"
    )
    st.plotly_chart(fig, use_container_width=True)