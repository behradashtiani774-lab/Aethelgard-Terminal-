import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# ۱. تنظیمات سیستمی
st.set_page_config(page_title="Aethelgard Terminal", layout="wide")

# ۲. هویت بصری (هدر)
st.markdown("<h1 style='text-align: center; color: #00ffcc;'>🏛️ Aethelgard Intelligence Unit</h1>", unsafe_allow_html=True)

# ۳. سایدبار (مدیریت سرمایه)
st.sidebar.header("💼 Strategic Wallet")
symbol = st.sidebar.selectbox("Select Asset", ["BTC-USD", "NVDA", "AAPL", "TSLA", "ETH-USD"])

irt_balance = 300000 
usdt_rate = 70000     
usdt_balance = irt_balance / usdt_rate
st.sidebar.metric("Your Capital", f"{irt_balance:,} IRT", f"${usdt_balance:.2f} USDT")

# ۴. موتور دریافت و پردازش دیتا
def get_processed_data(symbol):
    # دریافت دیتای بیشتر برای دقت RSI
    df = yf.download(symbol, period="2d", interval="1m", progress=False)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    
    # محاسبه RSI
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # محاسبه میانگین متحرک
    df['SMA_20'] = df['Close'].rolling(window=20).mean()
    return df

try:
    data = get_processed_data(symbol)
    
    if not data.empty:
        current_price = float(data['Close'].iloc[-1])
        
        # ۵. نمایش قیمت با استایل مدرن
        # ۵. هدر سه ستونه: روند، قیمت، ضربان
        st.write("") # فاصله از بالا
        
        # محاسبات روند و ضربان
        sma_20 = data['SMA_20'].iloc[-1]
        rsi_val = data['RSI'].iloc[-1]
        trend = "UPWARD" if current_price > sma_20 else "DOWNWARD"
        trend_color = "#00ffcc" if trend == "UPWARD" else "#ff4b4b"
        
        # ایجاد کادر سه ستونه با HTML و CSS
        st.markdown(f"""
            <div style="background-color: #161b22; padding: 25px; border-radius: 15px; border: 1px solid #30363d; display: flex; justify-content: space-around; align-items: center; text-align: center;">
                <div style="flex: 1;">
                    <p style="color: #8b949e; margin: 0; font-size: 0.9rem;">TREND</p>
                    <h2 style="color: {trend_color}; margin: 0;">{trend}</h2>
                </div>
                <div style="flex: 1; border-left: 1px solid #30363d; border-right: 1px solid #30363d;">
                    <p style="color: #8b949e; margin: 0; font-size: 0.9rem;">{symbol} LIVE PRICE</p>
                    <h1 style="color: #ffffff; margin: 0; font-size: 2.5rem;">${current_price:,.2f}</h1>
                </div>
                <div style="flex: 1;">
                    <p style="color: #8b949e; margin: 0; font-size: 0.9rem;">MARKET HEARTBEAT</p>
                    <h2 style="color: #00ffcc; margin: 0;">{rsi_val:.1f}</h2>
                </div>
            </div>
        """, unsafe_allow_html=True)
        st.write("")

        # ۶. رسم نمودار قیمت (Candlestick)
        plot_data = data.tail(100)
        fig = go.Figure(data=[go.Candlestick(
            x=plot_data.index, open=plot_data['Open'], 
            high=plot_data['High'], low=plot_data['Low'], 
            close=plot_data['Close'], name="Market")])
        
        fig.update_layout(template="plotly_dark", height=400, margin=dict(l=0,r=0,t=0,b=0), 
                          xaxis_rangeslider_visible=False, xaxis=dict(type='category', nticks=15))
        st.plotly_chart(fig, use_container_width=True)

        # ۷. رسم نمودار RSI
        st.markdown("### 💓 Market Heartbeat (RSI)")
        rsi_data = plot_data['RSI'].dropna()
        fig_rsi = go.Figure()
        fig_rsi.add_trace(go.Scatter(x=rsi_data.index, y=rsi_data, line=dict(color='#00ffcc', width=2)))
        fig_rsi.add_hline(y=70, line_color="red", line_dash="dash")
        fig_rsi.add_hline(y=30, line_color="green", line_dash="dash")
        fig_rsi.update_layout(template="plotly_dark", height=180, margin=dict(l=0,r=0,t=0,b=0), yaxis=dict(range=[0, 100]))
        st.plotly_chart(fig_rsi, use_container_width=True)

        # ۸. راهنمای خرید و فروش (AI Recommendation)
        st.divider()
        sma_20 = data['SMA_20'].iloc[-1]
        rsi_val = rsi_data.iloc[-1]
        
        col_advice, col_logic = st.columns([1, 2])
        if current_price > sma_20 and rsi_val < 70:
            col_advice.success("🟢 RECOMMENDATION: BUY")
            col_logic.info(f"Price is above SMA20. RSI ({rsi_val:.1f}) shows growth potential.")
        elif rsi_val > 70:
            col_advice.warning("🟡 RECOMMENDATION: SELL")
            col_logic.info(f"Market is Overbought (RSI: {rsi_val:.1f}). Correction likely.")
        else:
            col_advice.error("🔴 RECOMMENDATION: AVOID")
            col_logic.info("Price is below SMA20 or momentum is bearish.")

    else:
        st.error("Waiting for market data...")

except Exception as e:
    st.error(f"System Alert: {e}")