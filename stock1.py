# -*- coding: utf-8 -*-
"""
最終版：台美股多功能儀表板
支援：中文標題、K線、新聞、RSI、MACD、熱圖、CSV 匯出
"""

import streamlit as st
import yfinance as yf
import matplotlib.pyplot as plt
import mplfinance as mpf
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np
import seaborn as sns
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import threading

# ========================================
# 1. 中文字型設定（解決方框問題）
# ========================================
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei', 'SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['figure.dpi'] = 100

# 強制 matplotlib 使用中文字型
from matplotlib import font_manager
font_manager.fontManager.addfont('C:/Windows/Fonts/msjh.ttc')  # Windows
# Linux/macOS: 改成 '/System/Library/Fonts/AppleGothic.ttf' 或下載微軟正黑體

# ========================================
# 2. Streamlit 設定
# ========================================
st.set_page_config(page_title="台美股多功能儀表板", layout="wide")
st.title("台美股多功能比較儀表板")

# ========================================
# 3. 台股中文名稱字典（可擴充）
# ========================================
TW_STOCK_NAMES = {
    "2330.TW": "台積電 (2330)", "2317.TW": "鴻海 (2317)", "2454.TW": "聯發科 (2454)",
    "2303.TW": "聯電 (2303)", "2308.TW": "台達電 (2308)", "1303.TW": "南亞 (1303)",
    "2412.TW": "中華電信 (2412)", "2881.TW": "富邦金 (2881)", "1216.TW": "統一 (1216)",
    "1301.TW": "台塑 (1301)", "2882.TW": "國泰金 (2882)", "2886.TW": "兆豐金 (2886)",
    "1101.TW": "台泥 (1101)", "2002.TW": "中鋼 (2002)", "2891.TW": "中信金 (2891)",
    "2884.TW": "玉山金 (2884)", "2885.TW": "元大金 (2885)", "2887.TW": "台新金 (2887)",
    "3481.TW": "群創 (3481)", "2408.TW": "南亞科 (2408)", "2382.TW": "廣達 (2382)",
    "2357.TW": "華碩 (2357)", "2376.TW": "技嘉 (2376)", "3034.TW": "聯詠 (3034)",
    "3711.TW": "日月光投控 (3711)", "6669.TW": "緯穎 (6669)", "2377.TW": "微星 (2377)",
    "3231.TW": "緯創 (3231)", "4938.TW": "和碩 (4938)", "2356.TW": "英業達 (2356)"
}

US_STOCKS = ["AAPL", "MSFT", "GOOG", "TSLA", "NVDA", "AMZN", "META", "NFLX", "AMD", "INTC",
             "JPM", "V", "MA", "PYPL", "DIS", "BA", "CAT", "GE", "KO", "PFE"]

ETFS = ["SPY", "QQQ", "VTI", "VOO", "IWM", "GLD", "SLV", "TLT", "ARKK", "XLK"]

CRYPTOS = ["BTC-USD", "ETH-USD", "BNB-USD", "SOL-USD", "ADA-USD", "XRP-USD", "DOGE-USD", "DOT-USD"]

# ========================================
# 4. 快取資料
# ========================================
@st.cache_data(ttl=300)
def load_data(symbols, start, end):
    return yf.download(symbols, start=start, end=end, progress=False, auto_adjust=False)

# ========================================
# 5. 顯示名稱
# ========================================
def get_name(s):
    return TW_STOCK_NAMES.get(s, s.replace(".TW", "").replace("-USD", "")) + f" ({s})"

# ========================================
# 6. Selenium 台股新聞（穩定版）
# ========================================
@st.cache_data(ttl=300)
def scrape_tw_news(ticker):
    if not ticker.endswith(".TW"):
        return []
    code = ticker.replace(".TW", "")
    url = f"https://tw.stock.yahoo.com/quote/{code}/news"
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--user-agent=Mozilla/5.0')
    driver = webdriver.Chrome(options=options)
    news = []
    try:
        driver.get(url)
        time.sleep(3)
        wait = WebDriverWait(driver, 15)
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'ul[data-test="news-list"] li')))
        items = driver.find_elements(By.CSS_SELECTOR, 'ul[data-test="news-list"] li')[:10]
        for item in items:
            try:
                h3 = item.find_element(By.TAG_NAME, 'h3')
                title = h3.text
                link = h3.find_element(By.TAG_NAME, 'a').get_attribute('href')
                summary = item.find_element(By.TAG_NAME, 'p').text
                t = item.find_element(By.TAG_NAME, 'time').text
                news.append({"時間": t, "標題": title, "摘要": summary, "連結": link})
            except:
                continue
    except Exception as e:
        st.error(f"新聞載入失敗: {e}")
    finally:
        driver.quit()
    return news

# ========================================
# 7. 技術指標
# ========================================
def add_rsi_macd(df):
    close = df['Close']
    delta = close.diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    exp1 = close.ewm(span=12).mean()
    exp2 = close.ewm(span=26).mean()
    df['MACD'] = exp1 - exp2
    df['Signal'] = df['MACD'].ewm(span=9).mean()
    return df

# ========================================
# 8. 側邊欄
# ========================================
st.sidebar.header("設定")
category = st.sidebar.selectbox("類別", ["台股", "美股", "ETF", "加密貨幣"])

if category == "台股":
    opts = list(TW_STOCK_NAMES.keys())
    defaults = opts[:5]
elif category == "美股":
    opts = US_STOCKS
    defaults = opts[:3]
elif category == "ETF":
    opts = ETFS
    defaults = opts[:3]
else:
    opts = CRYPTOS
    defaults = opts[:2]

symbols = st.sidebar.multiselect("選擇股票", opts, default=defaults, format_func=lambda x: get_name(x).split(" (")[0])
start = st.sidebar.date_input("開始", pd.to_datetime("2020-01-01"))
end = st.sidebar.date_input("結束", pd.to_datetime("today"))

chart = st.sidebar.radio("圖表類型", [
    "收盤價", "移動平均", "成交量", "報酬率", 
    "K線圖", "RSI", "MACD", "相關性熱圖", "新聞"
])

if st.sidebar.button("手動更新"):
    st.cache_data.clear()
    st.rerun()

# ========================================
# 9. 主流程
# ========================================
if not symbols:
    st.warning("請選擇股票")
else:
    data = load_data(symbols, start, end)
    if data.empty:
        st.error("無資料")
    else:
        # CSV
        st.sidebar.download_button("下載 CSV", data.to_csv().encode(), f"data_{datetime.now():%Y%m%d}.csv", "text/csv")

        close = data['Close'] if isinstance(data.columns, pd.MultiIndex) else data.filter(like='Close')
        volume = data['Volume'] if isinstance(data.columns, pd.MultiIndex) else data.filter(like='Volume')

        # 圖表
        if chart == "收盤價":
            st.subheader("收盤價走勢")
            fig, ax = plt.subplots(figsize=(14, 7))
            for s in close.columns:
                ax.plot(close[s], label=get_name(s).split(" (")[0], linewidth=2)
            ax.set_title("多檔股票收盤價比較", fontsize=16)
            ax.set_xlabel("日期")
            ax.set_ylabel("價格")
            ax.legend()
            ax.grid(True, alpha=0.3)
            st.pyplot(fig)
            plt.close(fig)

        elif chart == "移動平均":
            st.subheader("移動平均線")
            fig, ax =plt.subplots(figsize=(14, 7))
            for s in close.columns:
                name = get_name(s).split(" (")[0]
                ax.plot(close[s], label=f"{name} 收盤")
                ax.plot(close[s].rolling(30).mean(), '--', label=f"{name} 30日MA")
                ax.plot(close[s].rolling(90).mean(), ':', label=f"{name} 90日MA")
            ax.set_title("收盤價與移動平均", fontsize=16)
            ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            ax.grid(True, alpha=0.3)
            st.pyplot(fig)
            plt.close(fig)

        elif chart == "成交量":
            st.subheader("成交量")
            fig, ax = plt.subplots(figsize=(14, 7))
            for s in volume.columns:
                ax.bar(volume.index, volume[s], label=get_name(s).split(" (")[0], alpha=0.7)
            ax.set_title("成交量比較", fontsize=16)
            ax.legend()
            ax.grid(True, alpha=0.3)
            st.pyplot(fig)
            plt.close(fig)

        elif chart == "報酬率":
            st.subheader("總報酬率")
            ret = (close.iloc[-1] / close.iloc[0] - 1) * 100
            df = pd.DataFrame({"股票": [get_name(s).split(" (")[0] for s in ret.index], "報酬率": ret.values.round(2)})
            fig = px.bar(df, x="股票", y="報酬率", color="股票", text="報酬率")
            fig.update_traces(texttemplate='%{text}%')
            st.plotly_chart(fig, use_container_width=True)

        elif chart == "K線圖":
            t = symbols[0]
            st.subheader(f"{get_name(t)} K線圖")
            raw = yf.download(t, start=start, end=end, progress=False, auto_adjust=False)
            if not raw.empty:
                df = raw[['Open','High','Low','Close','Volume']].copy().astype(float).dropna()
                if not df.empty:
                    fig, _ = mpf.plot(df, type='candle', mav=(30,90), style='yahoo',
                                      title=f"{get_name(t)} K線圖", returnfig=True, volume=True)
                    st.pyplot(fig)
                    plt.close(fig)

        elif chart == "RSI":
            t = symbols[0]
            st.subheader(f"{get_name(t)} RSI")
            raw = yf.download(t, start=start, end=end, progress=False)
            df = add_rsi_macd(raw.copy())
            fig, ax = plt.subplots(figsize=(14, 5))
            ax.plot(df['RSI'], label='RSI', color='purple')
            ax.axhline(70, color='r', linestyle='--', alpha=0.5)
            ax.axhline(30, color='g', linestyle='--', alpha=0.5)
            ax.set_title(f"{get_name(t)} RSI 指標")
            ax.legend()
            st.pyplot(fig)
            plt.close(fig)

        elif chart == "MACD":
            t = symbols[0]
            st.subheader(f"{get_name(t)} MACD")
            raw = yf.download(t, start=start, end=end, progress=False)
            df = add_rsi_macd(raw.copy())
            fig, ax = plt.subplots(figsize=(14, 5))
            ax.plot(df['MACD'], label='MACD', color='blue')
            ax.plot(df['Signal'], label='Signal', color='orange')
            ax.set_title(f"{get_name(t)} MACD 指標")
            ax.legend()
            st.pyplot(fig)
            plt.close(fig)

        elif chart == "相關性熱圖":
            st.subheader("股票相關性熱圖")
            corr = close.pct_change().corr()
            fig, ax = plt.subplots(figsize=(10, 8))
            sns.heatmap(corr, annot=True, cmap='coolwarm', ax=ax,
                        xticklabels=[get_name(s).split(" (")[0] for s in corr.columns],
                        yticklabels=[get_name(s).split(" (")[0] for s in corr.index])
            ax.set_title("股票價格相關性")
            st.pyplot(fig)
            plt.close(fig)

        elif chart == "新聞":
            t = symbols[0]
            st.subheader(f"{get_name(t)} 新聞")
            if t.endswith(".TW"):
                news = scrape_tw_news(t)
                if news:
                    for n in news:
                        with st.expander(n['標題']):
                            st.caption(n['時間'])
                            st.write(n['摘要'])
                            st.markdown(f"[閱讀全文]({n['連結']})")
                else:
                    st.info("無新聞")
            else:
                st.info("僅支援台股新聞")

        if st.checkbox("顯示原始資料"):
            st.write(data.tail(10))