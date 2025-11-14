import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import requests
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

class ProfessionalFinancialScraper:
    """專業金融數據爬蟲"""
    def __init__(self):
        self.periods = {
            'daily': '1d',
            'weekly': '5d',
            'monthly': '1mo',
            'quarterly': '3mo',
            'halfyear': '6mo',
            'yearly': '1y'
        }
        # 台股熱門標的
        self.tw_stocks = [
            '2330.TW', '2317.TW', '2454.TW', '2382.TW', '2881.TW',
            '2603.TW', '2303.TW', '2308.TW', '2412.TW', '2891.TW'
        ]
        # 美股熱門標的
        self.us_stocks = [
            'NVDA', 'AAPL', 'MSFT', 'GOOGL', 'AMZN',
            'TSLA', 'META', 'AVGO', 'LLY', 'V'
        ]
        # 台灣ETF
        self.tw_etfs = ['0050.TW', '0056.TW', '00878.TW', '00919.TW', '00881.TW']
        # 美國ETF
        self.us_etfs = ['SPY', 'QQQ', 'VTI', 'IWM', 'DIA']
        # 加密貨幣
        self.cryptos = ['BTC-USD', 'ETH-USD', 'BNB-USD', 'SOL-USD', 'XRP-USD']
    
    def get_stock_data(self, symbol, period='1mo'):
        """獲取股票數據"""
        try:
            stock = yf.Ticker(symbol)
            hist = stock.history(period=period)
            info = stock.info
            if hist.empty:
                return None
            current_price = hist['Close'].iloc[-1]
            prev_price = hist['Close'].iloc[0]
            change = current_price - prev_price
            change_pct = (change / prev_price) * 100
            volume = hist['Volume'].sum()
            return {
                'symbol': symbol,
                'name': info.get('longName', symbol),
                'price': round(float(current_price), 2),
                'change': round(float(change), 2),
                'change_percent': round(float(change_pct), 2),
                'volume': int(volume),
                'high': round(float(hist['High'].max()), 2),
                'low': round(float(hist['Low'].min()), 2),
                'avg_volume': int(hist['Volume'].mean()),
                'sector': info.get('sector', 'N/A'),
                'market_cap': info.get('marketCap', 0)
            }
        except Exception as e:
            print(f"Error fetching {symbol}: {e}")
            return None
    
    def get_top_performers(self, symbols, period='1mo', top_n=5):
        """獲取期間表現最佳的標的"""
        data = []
        for symbol in symbols:
            stock_data = self.get_stock_data(symbol, period)
            if stock_data:
                data.append(stock_data)
        # 按漲跌幅排序
        sorted_data = sorted(data, key=lambda x: x['change_percent'], reverse=True)
        return sorted_data[:top_n]
    
    def scrape_all_periods(self):
        """爬取所有時間維度的數據"""
        result = {
            'timestamp': datetime.now().isoformat(),
            'tw_stocks': {}, 'us_stocks': {}, 'tw_etfs': {}, 'us_etfs': {}, 'cryptos': {}
        }
        for period_name, period_code in self.periods.items():
            print(f"\n爬取 {period_name} 數據...")
            result['tw_stocks'][period_name] = self.get_top_performers(self.tw_stocks, period_code, 5)
            result['us_stocks'][period_name] = self.get_top_performers(self.us_stocks, period_code, 5)
            result['tw_etfs'][period_name] = self.get_top_performers(self.tw_etfs, period_code, 5)
            result['us_etfs'][period_name] = self.get_top_performers(self.us_etfs, period_code, 5)
            result['cryptos'][period_name] = self.get_top_performers(self.cryptos, period_code, 5)
        return result
    
    def analyze_with_ml(self, data):
        """使用機器學習分析推薦"""
        recommendations = {
            'tw_stocks': [], 'us_stocks': [], 'tw_etfs': [], 'us_etfs': [], 'cryptos': []
        }
        for category in recommendations.keys():
            monthly_data = data.get(category, {}).get('monthly', [])
            if not monthly_data:
                continue
            for item in monthly_data:
                score = 0
                # 漲跌幅評分 (40%)
                if item['change_percent'] > 20: score += 40
                elif item['change_percent'] > 10: score += 30
                elif item['change_percent'] > 5: score += 20
                elif item['change_percent'] > 0: score += 10
                # 成交量評分 (30%)
                if item['volume'] > item['avg_volume'] * 1.5: score += 30
                elif item['volume'] > item['avg_volume']: score += 20
                else: score += 10
                # 波動性評分 (30%)
                price_range = ((item['high'] - item['low']) / item['low']) * 100
                if price_range < 10: score += 30
                elif price_range < 20: score += 20
                else: score += 10
                item['ml_score'] = score
                # 生成推薦理由
                reasons = []
                if item['change_percent'] > 10: reasons.append(f"強勁漲幅 {item['change_percent']:.1f}%")
                if item['volume'] > item['avg_volume'] * 1.2: reasons.append("成交量活躍")
                if price_range < 15: reasons.append("波動穩定")
                item['recommendation_reasons'] = reasons
                # 推薦等級
                if score >= 80: item['recommendation'] = '強烈推薦'
                elif score >= 60: item['recommendation'] = '推薦'
                elif score >= 40: item['recommendation'] = '中性'
                else: item['recommendation'] = '觀望'
            sorted_items = sorted(monthly_data, key=lambda x: x.get('ml_score', 0), reverse=True)
            recommendations[category] = sorted_items[:3]
        return recommendations
    
    def save_data(self, data, filename='market_data_professional.json'):
        """保存數據"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"\n數據已保存至: {filename}")

# 使用範例
if __name__ == "__main__":
    scraper = ProfessionalFinancialScraper()
    print("="*70)
    print("開始爬取專業級金融數據...")
    print("="*70)
    all_data = scraper.scrape_all_periods()
    print("\n執行機器學習分析...")
    recommendations = scraper.analyze_with_ml(all_data)
    all_data['ml_recommendations'] = recommendations
    scraper.save_data(all_data)
    print("\n爬取完成！")
    print(f"台股數據：{len(all_data['tw_stocks'])}個時間維度")
    print(f"美股數據：{len(all_data['us_stocks'])}個時間維度")
    print(f"ETF數據：{len(all_data['tw_etfs']) + len(all_data['us_etfs'])}個時間維度")
    print(f"加密貨幣數據：{len(all_data['cryptos'])}個時間維度")
