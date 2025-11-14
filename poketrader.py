import random
import time
import threading

# --- 寶可夢屬性克制表 (簡化版) ---
# 格式: '攻擊屬性': {'對某屬性': 傷害倍率}
TYPE_CHART = {
    'Fire': {'Grass': 2.0, 'Water': 0.5, 'Fire': 1.0, 'Electric': 1.0, 'Normal': 1.0},
    'Water': {'Fire': 2.0, 'Grass': 0.5, 'Water': 1.0, 'Electric': 0.5, 'Normal': 1.0},
    'Grass': {'Water': 2.0, 'Fire': 0.5, 'Grass': 1.0, 'Electric': 1.0, 'Normal': 1.0},
    'Electric': {'Water': 2.0, 'Grass': 1.0, 'Fire': 1.0, 'Electric': 1.0, 'Normal': 1.0},
    'Normal': {'Fire': 1.0, 'Water': 1.0, 'Grass': 1.0, 'Electric': 1.0, 'Normal': 1.0},
}

class Pokemon:
    """
    代表一隻「上市」的寶可夢。
    """
    def __init__(self, name, p_type, base_price, base_power):
        self.name = name
        self.p_type = p_type
        self.base_price = float(base_price)
        self.current_price = float(base_price)
        self.base_power = base_power
        self.wins = 0
        self.losses = 0
        self.last_battle_result = "N/A" # 用於顯示在 Ticker 上

    def get_win_rate(self):
        """計算勝率，避免除以零"""
        total_battles = self.wins + self.losses
        if total_battles == 0:
            return 0.5 # 初始勝率
        return self.wins / total_battles

    def update_price(self):
        """
        核心價格更新邏輯。
        價格由「基礎價格」和「近期表現（勝率）」共同決定。
        這是一個非常簡化的模型，你可以讓它更複雜。
        """
        # 勝率影響因子 (0.5 勝率時為 1.0)
        win_factor = (self.get_win_rate() * 1.8) + 0.1 # 將勝率 0-1 映射到 0.1-1.9
        
        # 加上一點隨機性，模擬市場情緒
        random_factor = random.uniform(0.98, 1.02)
        
        new_price = self.base_price * win_factor * random_factor
        
        # 價格平滑，避免劇烈波動
        self.current_price = (self.current_price * 0.9) + (new_price * 0.1)
        
        if self.current_price < 1.0: # 設置最低價（破產保護）
             self.current_price = 1.0
        

class MarketSimulator:
    """
    「全球寶可夢模擬戰鬥聯盟」(GSBL) 的核心。
    它會不斷運行戰鬥並更新價格。
    """
    def __init__(self, pokemons):
        self.pokemons = pokemons
        self.battle_log = [] # 儲存戰鬥日誌，用於 Ticker
        self.running = False
        self.lock = threading.Lock()

    def _simulate_battle(self, p1, p2):
        """模擬兩隻寶可夢的戰鬥"""
        
        # 1. 獲取屬性克制
        p1_advantage = TYPE_CHART.get(p1.p_type, {}).get(p2.p_type, 1.0)
        p2_advantage = TYPE_CHART.get(p2.p_type, {}).get(p1.p_type, 1.0)

        # 2. 計算戰鬥力 (基礎戰力 * 屬性 * 隨機值)
        p1_combat_power = p1.base_power * p1_advantage * random.uniform(0.8, 1.2)
        p2_combat_power = p2.base_power * p2_advantage * random.uniform(0.8, 1.2)

        # 3. 判斷勝負
        if p1_combat_power > p2_combat_power:
            winner, loser = p1, p2
        else:
            winner, loser = p2, p1

        return winner, loser

    def run_market_tick(self):
        """
        運行一個市場「Tick」（一次戰鬥和價格更新）。
        這會在後端被高頻率調用。
        """
        with self.lock:
            # 1. 隨機選擇兩隻不同的寶可夢進行戰鬥
            p1, p2 = random.sample(self.pokemons, 2)

            # 2. 模擬戰鬥
            winner, loser = self._simulate_battle(p1, p2)

            # 3. 更新戰績
            winner.wins += 1
            loser.losses += 1
            
            battle_result = f"戰報: {winner.name} (▲) 擊敗了 {loser.name} (▼)"
            winner.last_battle_result = "WIN"
            loser.last_battle_result = "LOSE"

            # 4. 將戰報添加到日誌 (只保留最新的 10 條)
            self.battle_log.append(battle_result)
            if len(self.battle_log) > 10:
                self.battle_log.pop(0)

            # 5. 更新所有寶可夢的價格
            # (在一個 Tick 中只更新勝利者和失敗者，或者全部更新，這裡選擇全部更新以反映市場聯動)
            for p in self.pokemons:
                p.update_price()

    def start_simulation(self):
        """在單獨的線程中開始模擬，以免阻塞主程序"""
        self.running = True
        print("--- GSBL 模擬器已啟動 ---")
        
        def loop():
            while self.running:
                self.run_market_tick()
                # 模擬真實世界的戰鬥頻率 (例如每 0.5 秒一場)
                time.sleep(0.5) 
        
        # 啟動線程
        sim_thread = threading.Thread(target=loop, daemon=True)
        sim_thread.start()

    def stop_simulation(self):
        self.running = False
        print("--- GSBL 模擬器已停止 ---")

    def get_market_data(self):
        """
        獲取市場數據。
        在真實的 App 中，這將是 API 的一個端點 (endpoint)，
        前端會調用此函數來刷新 UI。
        """
        with self.lock:
            market_data = []
            # 排序：按價格高低
            sorted_pokemons = sorted(self.pokemons, key=lambda p: p.current_price, reverse=True)
            
            for p in sorted_pokemons:
                market_data.append({
                    'name': p.name,
                    'type': p.p_type,
                    'price': p.current_price,
                    'win_rate': p.get_win_rate(),
                    'wins': p.wins,
                    'losses': p.losses,
                    'last_result': p.last_battle_result
                })
            return market_data, self.battle_log

# --- 主程序 (用於演示) ---
if __name__ == "__main__":
    # 1. 初始化市場上的寶可夢
    # (名稱, 屬性, 基礎價格, 基礎戰力)
    POKEMON_LIST = [
        Pokemon("皮卡丘", "Electric", 150, 80),
        Pokemon("小火龍", "Fire", 120, 75),
        Pokemon("傑尼龜", "Water", 120, 75),
        Pokemon("妙蛙種子", "Grass", 120, 75),
        Pokemon("卡比獸", "Normal", 200, 110),
        Pokemon("鯉魚王", "Water", 5, 10), # 股價低，戰力差
        Pokemon("快龍", "Normal", 500, 150), # 基礎價格高
    ]

    # 2. 啟動市場模擬器
    market = MarketSimulator(POKEMON_LIST)
    market.start_simulation()

    # 3. 模擬前端每 2 秒刷新一次數據
    try:
        for _ in range(20): # 模擬運行 40 秒
            time.sleep(2)
            
            # 獲取最新數據
            market_data, battle_log = market.get_market_data()

            # --- 模擬前端 UI 渲染 ---
            print("\033[H\033[J") # 清除控制台 (僅適用於 Unix-like 終端)
            print("======= 寶可夢大亨 (PokéTycoon) - Gym-DAQ 交易所 =======")
            
            print("\n--- 市場報價 (PokéValue) ---")
            print(f"{'排名':<3} {'名稱':<8} {'屬性':<8} {'當前價格':<12} {'勝率':<8} {'戰績 (W/L)':<10}")
            print("-" * 60)
            for i, data in enumerate(market_data):
                price_str = f"{data['price']:.2f}"
                win_rate_str = f"{data['win_rate']:.1%}"
                record_str = f"{data['wins']}/{data['losses']}"
                
                # 根據漲跌顯示不同顏色 (概念)
                color_start = ""
                color_end = "\033[0m"
                if data['last_result'] == 'WIN':
                    color_start = "\033[92m" # 綠色 (漲)
                elif data['last_result'] == 'LOSE':
                    color_start = "\033[91m" # 紅色 (跌)
                    
                print(f"{color_start}{i+1:<3} {data['name']:<8} {data['type']:<8} ${price_str:<12} {win_rate_str:<8} {record_str:<10}{color_end}")

            print("\n--- 即時戰報 (Battle Ticker) ---")
            for log in battle_log:
                print(f"[!] {log}")
            print("=" * 60)

    except KeyboardInterrupt:
        print("\n用戶手動停止...")
    finally:
        market.stop_simulation()