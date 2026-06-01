import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Taiwan Stock Dashboard", layout="wide")

st.title("Taiwan Stock Market Dashboard")

stock_id = st.text_input("Enter Stock ID", "2330.TW")

df = yf.download(stock_id, period="6mo")

# 修正多層欄位
if isinstance(df.columns, pd.MultiIndex):
    df.columns = df.columns.get_level_values(0)

# 計算均線
df["MA5"] = df["Close"].rolling(5).mean()
df["MA20"] = df["Close"].rolling(20).mean()
df["MA60"] = df["Close"].rolling(60).mean()
# RSI Calculation
delta = df["Close"].diff()

gain = delta.clip(lower=0)
loss = -delta.clip(upper=0)

avg_gain = gain.rolling(14).mean()
avg_loss = loss.rolling(14).mean()

rs = avg_gain / avg_loss

df["RSI"] = 100 - (100 / (1 + rs))
# 最新資料
latest_close = round(df["Close"].iloc[-1], 2)
previous_close = round(df["Close"].iloc[-2], 2)

price_change = round(latest_close - previous_close, 2)
percent_change = round((price_change / previous_close) * 100, 2)

latest_volume = int(df["Volume"].iloc[-1])

# KPI Cards
col1, col2, col3, col4 = st.columns(4)

col1.metric("Current Price", latest_close)

col2.metric(
    "Daily Change",
    f"{price_change} ({percent_change}%)"
)

col3.metric(
    "Volume",
    f"{latest_volume:,}"
)

# MA20 判斷
if latest_close > df["MA20"].iloc[-1]:
    signal = "Bullish"
else:
    signal = "Bearish"

col4.metric("Trend Signal", signal)
st.divider()

# AI Smart Insight
st.subheader("AI Smart Insight")

latest_ma20 = df["MA20"].iloc[-1]
avg_volume = df["Volume"].rolling(20).mean().iloc[-1]

insight = ""

if latest_close > latest_ma20 and latest_volume > avg_volume:
    insight = """
    Strong bullish momentum detected.
    
    Price remains above MA20 with increasing trading volume.
    Investors may continue monitoring upward trends.
    """

elif latest_close > latest_ma20:
    insight = """
    Mild bullish trend detected.
    
    Price is trading above MA20, indicating positive momentum.
    """

else:
    insight = """
    Bearish or weak momentum detected.
    
    Price is currently below MA20.
    Investors should monitor market conditions carefully.
    """

st.info(insight)
st.divider()

# 圖表
fig = go.Figure()

# 收盤價
fig.add_trace(go.Scatter(
    x=df.index,
    y=df["Close"],
    mode='lines',
    name='Close Price'
))

# MA5
fig.add_trace(go.Scatter(
    x=df.index,
    y=df["MA5"],
    mode='lines',
    name='MA5'
))

# MA20
fig.add_trace(go.Scatter(
    x=df.index,
    y=df["MA20"],
    mode='lines',
    name='MA20'
))

# MA60
fig.add_trace(go.Scatter(
    x=df.index,
    y=df["MA60"],
    mode='lines',
    name='MA60'
))

fig.update_layout(
    title=f"{stock_id} Stock Price",
    xaxis_title="Date",
    yaxis_title="Price",
    template="plotly_dark",
    height=600
)

st.plotly_chart(fig, use_container_width=True)
# RSI Chart
st.subheader("RSI Indicator")

rsi_fig = go.Figure()

rsi_fig.add_trace(go.Scatter(
    x=df.index,
    y=df["RSI"],
    mode='lines',
    name='RSI'
))

# 超買線
rsi_fig.add_hline(
    y=70,
    line_dash="dash",
    line_color="red"
)

# 超賣線
rsi_fig.add_hline(
    y=30,
    line_dash="dash",
    line_color="green"
)

rsi_fig.update_layout(
    title="RSI (14)",
    template="plotly_dark",
    height=300
)

st.plotly_chart(rsi_fig, use_container_width=True)
st.subheader("Raw Data")
st.dataframe(df)