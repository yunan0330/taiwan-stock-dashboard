import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Taiwan Stock Dashboard", layout="wide")

st.title("Taiwan Stock Market Dashboard")

st.markdown("""
### Real-Time Financial Analytics Platform

This dashboard provides:
- Real-time stock price analysis
- Technical indicators (MA & RSI)
- AI-generated market insights
- Trading volume analytics
""")

stock_id = st.text_input("Enter Stock ID", "AAPL")

df = yf.download(stock_id, period="6mo", progress=False)

if df.empty:
    st.error("No data found. Please check the stock ID, for example: 2330.TW or AAPL.")
    st.stop()

# Fix yfinance MultiIndex columns
if isinstance(df.columns, pd.MultiIndex):
    df.columns = df.columns.get_level_values(0)

# Remove missing values
df = df.dropna(subset=["Open", "High", "Low", "Close", "Volume"])

if len(df) < 60:
    st.warning("Data length is short. Some indicators may not be fully available.")

# Moving averages
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

# Latest data
latest_close = round(float(df["Close"].iloc[-1]), 2)
previous_close = round(float(df["Close"].iloc[-2]), 2)

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

latest_ma20 = df["MA20"].dropna().iloc[-1]

if latest_close > latest_ma20:
    signal = "Bullish"
else:
    signal = "Bearish"

col4.metric("Trend Signal", signal)

st.divider()

# AI Smart Insight
st.subheader("AI Smart Insight")

avg_volume = df["Volume"].rolling(20).mean().dropna().iloc[-1]

if latest_close > latest_ma20 and latest_volume > avg_volume:
    insight = """
Strong bullish momentum detected.

Price remains above MA20 with increasing trading volume. Investors may continue monitoring upward trends.
"""
elif latest_close > latest_ma20:
    insight = """
Mild bullish trend detected.

Price is trading above MA20, indicating positive momentum.
"""
else:
    insight = """
Bearish or weak momentum detected.

Price is currently below MA20. Investors should monitor market conditions carefully.
"""

st.info(insight)


# RSI Signal
rsi_series = df["RSI"].dropna()

if not rsi_series.empty:
    latest_rsi = round(float(rsi_series.iloc[-1]), 2)

    if latest_rsi > 70:
        st.warning(f"RSI: {latest_rsi} → Overbought Condition")
    elif latest_rsi < 30:
        st.success(f"RSI: {latest_rsi} → Oversold Condition")
    else:
        st.info(f"RSI: {latest_rsi} → Neutral Momentum")
else:
    st.warning("RSI is not available because there is not enough data.")

st.subheader("Investment Signal")

if latest_close> latest_ma20 and latest_rsi < 70:
    st.success("BUY CANDIDATE")

elif latest_rsi > 70:
    st.warning("POTENTIAL OVERBOUGHT")

else:
    st.info("HOLD / WATCH")
st.divider()

# Main Price Chart
st.subheader("Stock Price and Moving Averages")

fig = go.Figure()

fig.add_trace(go.Candlestick(
    x=df.index,
    open=df["Open"],
    high=df["High"],
    low=df["Low"],
    close=df["Close"],
    name="Candlestick"
))

fig.add_trace(go.Scatter(
    x=df.index,
    y=df["MA5"],
    mode="lines",
    name="MA5"
))

fig.add_trace(go.Scatter(
    x=df.index,
    y=df["MA20"],
    mode="lines",
    name="MA20"
))

fig.add_trace(go.Scatter(
    x=df.index,
    y=df["MA60"],
    mode="lines",
    name="MA60"
))

fig.update_layout(
    title=f"{stock_id} Stock Price",
    xaxis_title="Date",
    yaxis_title="Price",
    height=700,
    xaxis_rangeslider_visible=False
)

st.plotly_chart(fig, use_container_width=True)

# Volume Chart
st.subheader("Trading Volume")

volume_fig = go.Figure()

volume_fig.add_trace(go.Bar(
    x=df.index,
    y=df["Volume"],
    name="Volume"
))

volume_fig.update_layout(
    title="Daily Trading Volume",
    height=300
)

st.plotly_chart(volume_fig, use_container_width=True)

# RSI Chart
st.subheader("RSI Indicator")

rsi_fig = go.Figure()

rsi_fig.add_trace(go.Scatter(
    x=df.index,
    y=df["RSI"],
    mode="lines",
    name="RSI"
))

rsi_fig.add_hline(y=70, line_dash="dash")
rsi_fig.add_hline(y=30, line_dash="dash")

rsi_fig.update_layout(
    title="RSI (14)",
    height=300
)

st.plotly_chart(rsi_fig, use_container_width=True)

# Raw Data
st.subheader("Raw Data")
st.dataframe(df)