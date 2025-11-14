# -*- coding: utf-8 -*-
"""
Created on Thu Nov  6 11:41:57 2025

@author: USER
"""

# pokestock_app.py
import kivy
kivy.require('2.0.0')
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Ellipse, Rotate
import yfinance as yf
import pygame
import random
import threading
import time

# 初始化 Pygame mixer for sound
pygame.mixer.init()

# 寶可夢-股票映射 (擴展到更多)
POKE_STOCKS = {
    'Pikachu': 'TSLA',  # Electric -> Tesla
    'Eevee': 'SPY',     # Versatile -> S&P 500 ETF
    'Charizard': 'AAPL' # Fire -> Apple innovation
}

class CaptureScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical')
        
        # 背景: 彩虹漸層 (Kivy shader 可擴展)
        with self.layout.canvas.before:
            Color(0.2, 0.6, 1, 1)  # Blue sky
            self.layout.rect = Ellipse(pos=self.layout.pos, size=self.layout.size)
        
        # 顯示野生股票
        self.wild_label = Label(text='野生股票出現！', font_size=24, size_hint=(1, 0.3))
        self.layout.add_widget(self.wild_label)
        
        # 捕捉按鈕 (滑動觸發更好，但簡化用按)
        capture_btn = Button(text='丟 Poké Ball 捕捉！', size_hint=(1, 0.4))
        capture_btn.bind(on_press=self.capture_stock)
        self.layout.add_widget(capture_btn)
        
        self.add_widget(self.layout)
    
    def capture_stock(self, instance):
        # 隨機選股票
        poke, stock = random.choice(list(POKE_STOCKS.items()))
        self.wild_label.text = f'捕捉 {poke} ({stock})！'
        
        # 拉真實數據 (threading 避免卡頓)
        threading.Thread(target=self.fetch_and_animate, args=(stock, poke)).start()
    
    def fetch_and_animate(self, stock, poke):
        try:
            data = yf.Ticker(stock).history(period='1d')
            change = (data['Close'][-1] - data['Open'][0]) / data['Open'][0] * 100
            status = '漲' if change > 0 else '跌'
            Clock.schedule_once(lambda dt: self.update_ui(poke, status, change), 0)
        except:
            Clock.schedule_once(lambda dt: self.update_ui(poke, '平盤', 0), 0)
    
    def update_ui(self, poke, status, change):
        self.wild_label.text += f'\n{status} {change:.2f}%！'
        
        # 動畫: Poké Ball 旋轉飛入
        ball = Image(source='pokeball.png', size_hint=(0.2, 0.2), pos_hint={'center_x': 0.5, 'y': 0.5})  # 下載 pokeball.png
        self.layout.add_widget(ball)
        anim = Animation(size=(0.5, 0.5), duration=0.5) + Animation(opacity=0, duration=0.3)
        anim.start(ball)
        
        # 音效: 捕捉成功 (下載 pikachu_cry.ogg)
        if status == '漲':
            pygame.mixer.music.load('victory_fanfare.ogg')  # 下載 BGM
            pygame.mixer.music.play()
        else:
            pygame.mixer.music.load('fail_sound.ogg')
            pygame.mixer.music.play()
        
        # 成功加到組合 (簡化，實際存 DB)
        self.manager.get_screen('portfolio').add_poke(poke, change)

class PortfolioScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical')
        self.portfolio_label = Label(text='你的寶可夢投資組合\n總市值: $0', font_size=20)
        self.layout.add_widget(self.portfolio_label)
        self.pokes = {}  # {poke: change}
        self.add_widget(self.layout)
    
    def add_poke(self, poke, change):
        self.pokes[poke] = change
        total = sum(self.pokes.values())  # 簡化計算
        self.portfolio_label.text = f'你的寶可夢投資組合\n總市值: ${total:.2f}\n新捕捉: {poke} ({change:.2f}%)'
        
        # 動畫: 寶可夢彈跳出現 (用 Image)
        img = Image(source=f'{poke.lower()}.png', size_hint=(0.3, 0.3))  # 下載圖像 e.g., pikachu.png
        self.layout.add_widget(img)
        anim = Animation(y=50, duration=0.5) + Animation(y=0, duration=0.5)
        anim.repeat = True
        anim.start(img)
        
        # 音效: 寶可夢叫聲
        pygame.mixer.music.load(f'{poke}_cry.ogg')
        pygame.mixer.music.play()

class PokeInvestApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(CaptureScreen(name='capture'))
        sm.add_widget(PortfolioScreen(name='portfolio'))
        return sm

if __name__ == '__main__':
    Window.size = (400, 600)  # Mobile-like
    PokeInvestApp().run()