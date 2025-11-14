import matplotlib.pyplot as plt
import yfinance as yf
from matplotlib import font_manager


# 設定中文字型（依你系統字型調整）
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']  # 微軟正黑體
plt.rcParams['axes.unicode_minus'] = False  # 讓負號正常顯示
# 設定股票代碼與時間範圍
stocks = ['AAPL', 'MSFT', 'GOOG']
start_date = '2020-01-01'
end_date = '2024-01-01'

# 下載多檔股票的完整資料
data = yf.download(stocks, start=start_date, end=end_date)

# 檢查有哪些欄位
print(data.columns)

# 取出「收盤價」資料
close_prices = data.xs('Close', axis=1, level=0)

# 繪製多檔股票走勢
plt.figure(figsize=(12,7))
for ticker in close_prices.columns:
    plt.plot(close_prices[ticker], label=ticker)
plt.title('AAPL vs MSFT vs GOOG 收盤價比較')
plt.xlabel('日期')
plt.ylabel('價格 (美元)')
plt.legend()
plt.grid(True)
plt.show()

# 加入移動平均線 (AAPL)
plt.figure(figsize=(12,7))
aapl = close_prices['AAPL']
plt.plot(aapl, label='AAPL Close', color='blue')
plt.plot(aapl.rolling(30).mean(), label='30日移動平均', linestyle='--', color='orange')
plt.plot(aapl.rolling(90).mean(), label='90日移動平均', linestyle='--', color='green')
plt.title('AAPL 收盤價與移動平均線')
plt.xlabel('日期')
plt.ylabel('價格 (美元)')
plt.legend()
plt.grid(True)
plt.show()

#%%
print("欄位結構：", data.columns)
#%%
import matplotlib.pyplot as plt
import yfinance as yf
import pandas as pd
import numpy as np
import mplfinance as mpf

# === 字型設定（避免中文亂碼與方格） ===
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']  # 微軟正黑體
plt.rcParams['axes.unicode_minus'] = False
plt.style.use('seaborn-v0_8-whitegrid')

# === 下載股票資料 ===
stocks = ['AAPL', 'MSFT', 'GOOG']
start_date = '2020-01-01'
end_date = '2024-01-01'
data = yf.download(stocks, start=start_date, end=end_date)
close_prices = data.xs('Close', axis=1, level=0)
volume = data.xs('Volume', axis=1, level=0)

# === 1️⃣ 多檔股票收盤價比較 ===
plt.figure(figsize=(12,7))
for ticker in close_prices.columns:
    plt.plot(close_prices[ticker], label=ticker)
plt.title('多檔科技股收盤價比較 (2020–2024)')
plt.xlabel('日期')
plt.ylabel('價格 (美元)')
plt.legend()
plt.grid(False)
plt.show()

# === 2️⃣ AAPL 移動平均線與交叉訊號 ===
aapl = close_prices['AAPL']
short_ma = aapl.rolling(30).mean()
long_ma = aapl.rolling(90).mean()

# 找出交叉點
golden_cross = (short_ma > long_ma) & (short_ma.shift(1) <= long_ma.shift(1))
death_cross = (short_ma < long_ma) & (short_ma.shift(1) >= long_ma.shift(1))

plt.figure(figsize=(12,7))
plt.plot(aapl, label='AAPL 收盤價', color='blue')
plt.plot(short_ma, label='30日均線', linestyle='--', color='orange')
plt.plot(long_ma, label='90日均線', linestyle='--', color='green')
plt.scatter(aapl.index[golden_cross], aapl[golden_cross], color='red', marker='^', s=100, label='黃金交叉')
plt.scatter(aapl.index[death_cross], aapl[death_cross], color='black', marker='v', s=100, label='死亡交叉')
plt.title('AAPL 收盤價與移動平均線（含買賣訊號）')
plt.xlabel('日期')
plt.ylabel('價格 (美元)')
plt.legend()
plt.grid(False)
plt.show()

# === 3️⃣ 成交量長條圖 ===
plt.figure(figsize=(12,5))
plt.bar(volume.index, volume['AAPL'], color='skyblue')
plt.title('AAPL 成交量趨勢')
plt.xlabel('日期')
plt.ylabel('成交股數')
plt.grid(False)
plt.show()

# === 4️⃣ K 線圖 ===
aapl_data = yf.download('AAPL', start=start_date, end=end_date)
mpf.plot(aapl_data, type='candle', mav=(30,90), title='AAPL K 線圖 (30/90日均線)', style='yahoo')

# === 5️⃣ 報酬率與統計摘要 ===
returns = (close_prices.iloc[-1] / close_prices.iloc[0] - 1) * 100
summary = pd.DataFrame({
    '報酬率 (%)': returns.round(2),
    '平均價格': close_prices.mean().round(2),
    '最高價': close_prices.max().round(2),
    '最低價': close_prices.min().round(2)
})
print("\n📊 股票統計摘要 (2020–2024):")
print(summary)
#%%
import streamlit as st
import yfinance as yf
import matplotlib.pyplot as plt
import mplfinance as mpf
import pandas as pd
import plotly.express as px

# === 中文字型設定 ===
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']  # 微軟正黑體
plt.rcParams['axes.unicode_minus'] = False

# === Streamlit 頁面設定 ===
st.set_page_config(page_title="互動式股票分析儀表板", layout="wide")
st.title("📊 極簡風互動式股票分析儀表板")

# === 側邊欄設定 ===
st.sidebar.header("🔧 設定選項")
symbols = st.sidebar.multiselect(
    "選擇股票代號",
    ["AAPL", "MSFT", "GOOG", "TSLA", "AMZN", "NVDA", "META"],
    default=["AAPL"]
)

start_date = st.sidebar.date_input("開始日期", pd.to_datetime("2020-01-01"))
end_date = st.sidebar.date_input("結束日期", pd.to_datetime("2024-01-01"))
chart_type = st.sidebar.radio("選擇圖表類型", ["收盤價", "移動平均", "成交量", "K線圖", "報酬率比較"])

# === 下載資料 ===
if symbols:
    data = yf.download(symbols, start=start_date, end=end_date)

    if chart_type == "收盤價":
        st.subheader("📈 收盤價走勢圖")
        close = data.xs("Close", axis=1, level=0)
        fig, ax = plt.subplots(figsize=(12,6))
        for ticker in close.columns:
            ax.plot(close[ticker], label=ticker)
        ax.legend()
        ax.set_title("股票收盤價走勢", fontsize=14)
        ax.set_xlabel("日期")
        ax.set_ylabel("價格 (美元)")
        ax.grid(False)
        ax.box(False)
        st.pyplot(fig)

    elif chart_type == "移動平均":
        st.subheader("📉 AAPL 移動平均線")
        aapl = data["Close"]["AAPL"]
        fig, ax = plt.subplots(figsize=(12,6))
        ax.plot(aapl, color='royalblue', label="AAPL 收盤價")
        ax.plot(aapl.rolling(30).mean(), color='orange', linestyle='--', label="30日均線")
        ax.plot(aapl.rolling(90).mean(), color='green', linestyle='--', label="90日均線")
        ax.legend()
        ax.set_title("AAPL 收盤價與移動平均", fontsize=14)
        ax.grid(False)
        ax.box(False)
        st.pyplot(fig)

    elif chart_type == "成交量":
        st.subheader("📊 成交量變化圖")
        vol = data.xs("Volume", axis=1, level=0)
        fig, ax = plt.subplots(figsize=(12,6))
        for ticker in vol.columns:
            ax.bar(vol.index, vol[ticker], label=ticker, color='skyblue', width=1.0, alpha=0.7)
        ax.set_title("成交量變化", fontsize=14)
        ax.set_xlabel("日期")
        ax.set_ylabel("成交量")
        ax.legend()
        ax.grid(False)
        ax.box(False)
        st.pyplot(fig)

    elif chart_type == "K線圖":
        st.subheader("🕯️ K 線圖（AAPL）")
        aapl_data = yf.download("AAPL", start=start_date, end=end_date)
        mpf.plot(aapl_data, type='candle', mav=(30,90), style='yahoo', title="AAPL K 線圖")
        st.pyplot(plt)

    elif chart_type == "報酬率比較":
        st.subheader("💰 股票報酬率比較")
        close = data.xs("Close", axis=1, level=0)
        returns = (close.iloc[-1] / close.iloc[0] - 1) * 100
        result = pd.DataFrame({"股票": returns.index, "報酬率 (%)": returns.values})
        fig = px.bar(result, x="股票", y="報酬率 (%)", color="股票", title="總報酬率比較")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(result.style.highlight_max(subset=["報酬率 (%)"], color="lightgreen"))

else:
    st.warning("請至少選擇一檔股票！")
