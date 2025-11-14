# -*- coding: utf-8 -*-
"""
Created on Tue Nov 11 09:40:12 2025

@author: USER
"""

import random

def get_card():
    """隨機選取一張撲克牌的花色和數字。"""
    suits = ['黑桃', '紅心', '方塊', '梅花']
    # 數字：A, 2, 3, 4, 5, 6, 7, 8, 9, 10, J, Q, K
    ranks = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']

    chosen_suit = random.choice(suits)
    chosen_rank = random.choice(ranks)

    return chosen_suit, chosen_rank

def play_game():
    """主遊戲邏輯。"""
    print("--- 🃏 歡迎來到撲克牌猜謎遊戲！ 🃏 ---")
    print("我已經從一副牌中隨機選了一張牌，現在請你來猜猜看！")

    # 獲取要猜測的牌
    actual_suit, actual_rank = get_card()
    
    # 允許的花色和數字輸入（用於檢查）
    valid_suits = ['黑桃', '紅心', '方塊', '梅花']
    valid_ranks = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']

    guessed_correctly = False
    attempts = 0

    while not guessed_correctly:
        attempts += 1
        print(f"\n--- 第 {attempts} 次嘗試 ---")
        
        # 1. 猜測花色
        while True:
            guess_suit = input(f"請猜花色（{'/'.join(valid_suits)}）：").strip().title()
            # 檢查輸入是否在有效花色列表中
            if guess_suit in valid_suits:
                break
            else:
                print("輸入的花色無效，請重新輸入！")

        # 2. 猜測數字
        while True:
            guess_rank = input(f"請猜數字（{'/'.join(valid_ranks)}）：").strip().upper()
            # 檢查輸入是否在有效數字列表中
            if guess_rank in valid_ranks:
                break
            else:
                print("輸入的數字無效，請重新輸入！")
        
        # 3. 檢查結果
        is_suit_correct = (guess_suit == actual_suit)
        is_rank_correct = (guess_rank == actual_rank)
        
        if is_suit_correct and is_rank_correct:
            # 兩者都猜對了
            guessed_correctly = True
            print(f"\n🎉 恭喜你！你猜對了！這張牌是 **{actual_suit}{actual_rank}**！")
            print(f"你總共花了 {attempts} 次嘗試。")
        else:
            # 至少有一項猜錯了
            feedback = "提示："
            if is_suit_correct:
                feedback += "花色猜對了！"
            else:
                feedback += "花色猜錯了。"

            if is_rank_correct:
                feedback += " 數字猜對了！"
            else:
                feedback += " 數字猜錯了。"
                
            print(f"很可惜，猜錯了。{feedback} 請再試一次。")

if __name__ == "__main__":
    play_game()


#%%
import random

def get_card():
    """隨機選取一張撲克牌的花色和數字。"""
    suits = ['黑桃', '紅心', '方塊', '梅花']
    ranks = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
    
    return random.choice(suits), random.choice(ranks)

# 數字到數值的映射，用於比較大小
RANK_TO_VALUE = {
    'A': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7,
    '8': 8, '9': 9, '10': 10, 'J': 11, 'Q': 12, 'K': 13
}
# 花色到色系的映射
SUIT_TO_COLOR = {
    '黑桃': '黑色系', 
    '梅花': '黑色系', 
    '紅心': '紅色系', 
    '方塊': '紅色系'
}

def select_difficulty():
    """讓玩家選擇遊戲難度並設定計分參數與提示等級。"""
    print("\n## 選擇遊戲難度")
    print("1. 簡單：有花色色系和數字大小提示。")
    print("2. 中等：僅有數字大小提示。")
    print("3. 困難：無額外提示。")
    
    while True:
        choice = input("請輸入數字選擇難度（1/2/3）：").strip()
        
        if choice == '1':
            # 簡單: 兩者提示都有
            return '簡單', {'suit': 5, 'rank': 10, 'bonus': 50}, {'suit_hint': True, 'rank_hint': True}
        elif choice == '2':
            # 中等: 只有數字大小提示
            return '中等', {'suit': 10, 'rank': 20, 'bonus': 100}, {'suit_hint': False, 'rank_hint': True}
        elif choice == '3':
            # 困難: 兩者提示都沒有
            return '困難', {'suit': 20, 'rank': 40, 'bonus': 200}, {'suit_hint': False, 'rank_hint': False}
        else:
            print("⚠️ 無效的選擇，請輸入 1, 2 或 3。")

def play_game():
    """主遊戲邏輯，包含難度選擇、計分和根據難度區分的提示。"""
    print("--- 🃏 **最終版撲克牌猜謎遊戲！** 🃏 ---")
    print("> 數字順序：A(最小) < 2 < ... < 10 < J < Q < K(最大)")

    # 1. 選擇難度並獲取配置
    difficulty_name, score_config, hint_config = select_difficulty()
    print(f"\n✅ 已選擇：**{difficulty_name}** 模式。")

    # 2. 獲取要猜測的牌
    actual_suit, actual_rank = get_card()
    actual_value = RANK_TO_VALUE[actual_rank] # 實際數字轉為數值
    actual_color = SUIT_TO_COLOR[actual_suit] # 實際花色所屬色系
    
    # 3. 定義有效輸入
    valid_suits = list(SUIT_TO_COLOR.keys())
    valid_ranks = list(RANK_TO_VALUE.keys())
    rank_hint_options = "A, 2 到 10, J, Q, K"

    # 4. 初始化遊戲變數
    guessed_correctly = False
    attempts = 0
    total_score = 0

    while not guessed_correctly:
        attempts += 1
        print(f"\n--- ➡️ 第 **{attempts}** 次嘗試 (目前總分: {total_score}) ---")
        
        # 4-1. 猜測花色
        while True:
            guess_suit = input(f"請猜花色（{'/'.join(valid_suits)}）：").strip().title()
            if guess_suit in valid_suits:
                break
            else:
                print("⚠️ 輸入的花色無效，請重新輸入！")

        # 4-2. 猜測數字
        while True:
            guess_rank = input(f"請猜數字（例如：{rank_hint_options}）：").strip().upper()
            if guess_rank in valid_ranks:
                guess_value = RANK_TO_VALUE[guess_rank] # 猜測數字轉為數值
                break
            else:
                print("⚠️ 輸入的數字無效，請檢查您的輸入。")
        
        # 4-3. 檢查並計分
        is_suit_correct = (guess_suit == actual_suit)
        is_rank_correct = (guess_rank == actual_rank)
        
        round_score = 0
        feedback = "**本次提示：**"
        
        # --- 花色提示邏輯 ---
        if is_suit_correct:
            round_score += score_config['suit']
            feedback += f" 花色猜對了！(+{score_config['suit']} 分)"
        else:
            feedback += " 花色猜錯了。"
            # 簡單模式 (hint_config['suit_hint'] == True) 時，提供色系提示
            if hint_config['suit_hint']:
                guess_color = SUIT_TO_COLOR[guess_suit]
                feedback += f" 實際花色屬於 **{actual_color}**。"

        # --- 數字提示邏輯 ---
        if is_rank_correct:
            round_score += score_config['rank']
            feedback += f" 數字猜對了！(+{score_config['rank']} 分)"
        else:
            feedback += " 數字猜錯了。"
            # 簡單或中等模式 (hint_config['rank_hint'] == True) 時，提供大小提示
            if hint_config['rank_hint']:
                if guess_value < actual_value:
                    feedback += f" 實際數字比 **{guess_rank}** 大。"
                else: # guess_value > actual_value
                    feedback += f" 實際數字比 **{guess_rank}** 小。"
        
        total_score += round_score
        
        # 4-4. 結束或繼續
        if is_suit_correct and is_rank_correct:
            # 完全猜中
            guessed_correctly = True
            bonus = score_config['bonus']
            total_score += bonus
            
            print("\n===========================================")
            print(f"🎉 **恭喜！你完全猜對了！**")
            print(f"實際的牌是：**{actual_suit}{actual_rank}**")
            print(f"獲得額外獎勵：+{bonus} 分")
            print(f"總共花費：**{attempts}** 次嘗試")
            print(f"最終總分：**{total_score}** 分（{difficulty_name} 模式）")
            print("===========================================")
        else:
            # 猜錯，提供回饋
            print(feedback)
            print(f"本回合得分：**{round_score}** 分，累積總分：**{total_score}** 分。")
            print("請再試一次！")

if __name__ == "__main__":
    play_game()