# -*- coding: utf-8 -*-
"""
寶可夢迷宮 V8.0 - 終極完整版
功能：道具、BOSS、陷阱、商店、排行榜、進化動畫、音效、背景音樂
"""

import streamlit as st
from PIL import Image, ImageDraw, ImageFilter
import requests
import io
import random
import time
import base64
import json

# ===================== 1. 頁面設定 =====================
st.set_page_config(page_title="寶可夢迷宮 V8.0", page_icon="pokeball", layout="centered")

# ===================== 2. CSS + 動畫 + 音效 =====================
st.markdown("""
<style>
    .main { background: #0f3460; color: white; text-align: center; font-family: 'Arial'; }
    .btn { background: #e94560; color: white; padding: 10px 20px; border-radius: 12px; font-weight: bold; border: none; cursor: pointer; }
    .btn:hover { background: #ff6b6b; transform: scale(1.05); }
    .maze { display: grid; grid-template-columns: repeat(5, 60px); gap: 5px; margin: 20px auto; }
    .cell { width: 60px; height: 60px; border: 2px solid #34495e; font-size: 24px; display: flex; align-items: center; justify-content: center; border-radius: 10px; }
    .player { background: #f1c40f; color: #2c3e50; }
    .pokemon { background: #e74c3c; color: white; }
    .boss { background: #9b59b6; color: white; font-weight: bold; }
    .exit { background: #27ae60; color: white; }
    .wall { background: #2c3e50; }
    .path { background: #34495e; }
    .captured { background: #3498db; color: white; }
    .trap { background: #e67e22; color: white; }
    .shop { background: #f39c12; color: white; padding: 10px; border-radius: 15px; margin: 5px; display: inline-block; }
    .leaderboard { background: #16213e; padding: 15px; border-radius: 15px; margin-top: 20px; }
    .evo { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: white; z-index: 999; display: flex; flex-direction: column; justify-content: center; align-items: center; animation: flash 0.4s 4; }
    @keyframes flash { 0%, 100% { opacity: 1; } 50% { opacity: 0.2; } }
    .evo-text { font-size: 3em; color: #f39c12; font-weight: bold; text-shadow: 0 0 30px gold; animation: glow 1s infinite; }
    @keyframes glow { 0%, 100% { text-shadow: 0 0 30px gold; } 50% { text-shadow: 0 0 50px orange; } }
</style>
""", unsafe_allow_html=True)

# 背景音樂
st.markdown('''
<audio autoplay loop>
    <source src="https://www.soundjay.com/misc/sounds/bell-ringing-05.mp3" type="audio/mpeg">
</audio>
''', unsafe_allow_html=True)

# 音效播放
def play(effect):
    sounds = {
        "encounter": "https://www.soundjay.com/misc/bell-ring-01.mp3",
        "capture": "https://assets.mixkit.co/sfx/preview/mixkit-achievement-bell-600.mp3",
        "escape": "https://www.soundjay.com/buttons/button-4.mp3",
        "evolve": "https://assets.mixkit.co/sfx/preview/mixkit-arcade-game-level-up-2064.mp3",
        "victory": "https://assets.mixkit.co/sfx/preview/mixkit-winning-chimes-2015.mp3",
        "trap": "https://www.soundjay.com/human/sounds/scream-01.mp3",
        "buy": "https://assets.mixkit.co/sfx/preview/mixkit-coin-win-1939.mp3"
    }
    if effect in sounds:
        st.markdown(f'<audio autoplay><source src="{sounds[effect]}" type="audio/mpeg"></audio>', unsafe_allow_html=True)

# ===================== 3. 迷宮生成（必須先定義！）=====================
def generate_maze():
    size = 5
    maze = [['wall'] * size for _ in range(size)]
    def carve(x, y):
        maze[y][x] = 'path'
        for dx, dy in random.sample([(0,1),(1,0),(0,-1),(-1,0)], 4):
            nx, ny = x + dx*2, y + dy*2
            if 0 <= nx < size and 0 <= ny < size and maze[ny][nx] == 'wall':
                maze[y+dy][x+dx] = 'path'
                carve(nx, ny)
    carve(0, 0)
    maze[0][0] = 'player'
    maze[4][4] = 'exit'
    # 隨機寶可夢
    for _ in range(3 + st.session_state.stage // 3):
        x, y = random.randint(0,4), random.randint(0,4)
        if maze[y][x] in ['path']:
            maze[y][x] = 'boss' if st.session_state.stage % 5 == 0 else 'pokemon'
    # 陷阱
    for _ in range(max(1, st.session_state.stage // 3)):
        x, y = random.randint(0,4), random.randint(0,4)
        if maze[y][x] == 'path':
            maze[y][x] = 'trap'
    return maze

# ===================== 4. 初始化（後呼叫）=====================
def init():
    defaults = {
        'stage': 1, 'coins': 50, 'score': 0, 'hp': 3,
        'inventory': {'pokeball': 3, 'hint': 1, 'bomb': 0},
        'captured': [], 'maze': [], 'player': [0,0],
        'evolving': None, 'game_state': 'menu',
        'boss_defeated': False, 'leaderboard': []
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v
    if not st.session_state.maze:
        st.session_state.maze = generate_maze()
        st.session_state.player = [0, 0]

init()

# ===================== 5. 資料 =====================
POKEMONS = {
    "妙蛙種子": "bulbasaur", "妙蛙草": "ivysaur", "妙蛙花": "venusaur",
    "小火龍": "charmander", "火恐龍": "charmeleon", "噴火龍": "charizard",
    "傑尼龜": "squirtle", "卡咪龜": "wartortle", "水箭龜": "blastoise",
    "皮卡丘": "pikachu", "雷丘": "raichu", "伊布": "eevee", "水伊布": "vaporeon",
    "卡比獸": "snorlax", "超夢": "mewtwo", "夢幻": "mew", "暴鯉龍": "gyarados"
}
NAMES = list(POKEMONS.keys())

EVOLUTION = {
    "妙蛙種子": ("妙蛙草", 3), "妙蛙草": ("妙蛙花", 5),
    "小火龍": ("火恐龍", 3), "火恐龍": ("噴火龍", 5),
    "傑尼龜": ("卡咪龜", 3), "卡咪龜": ("水箭龜", 5),
    "皮卡丘": ("雷丘", 4)
}

def get_img(name):
    url = f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/{POKEMONS[name]}.png"
    try:
        r = requests.get(url, timeout=3)
        return Image.open(io.BytesIO(r.content)).resize((80,80))
    except:
        img = Image.new('RGBA', (80,80), (220,220,220,255))
        draw = ImageDraw.Draw(img)
        draw.text((20,30), name[0], fill="black")
        return img

def fuse(p1, p2):
    img1, img2 = get_img(p1), get_img(p2)
    fused = Image.new('RGBA', (160,80))
    fused.paste(img1, (0,0))
    fused.paste(img2, (80,0))
    return fused

# ===================== 6. 進化動畫 =====================
def show_evo(old, new):
    old_img = get_img(old)
    new_img = get_img(new)
    st.session_state.evolving = {'old': old_img, 'new': new_img, 'name': f"{old}→{new}", 'time': time.time()}
    play("evolve")
    st.rerun()

if st.session_state.evolving:
    elapsed = time.time() - st.session_state.evolving['time']
    if elapsed < 3:
        alpha = elapsed / 3
        blended = Image.blend(st.session_state.evolving['old'], st.session_state.evolving['new'], alpha)
        blurred = blended.filter(ImageFilter.GaussianBlur(5 * (1-alpha)))
        buf = io.BytesIO()
        blurred.save(buf, "PNG")
        b64 = base64.b64encode(buf.getvalue()).decode()
        st.markdown(f"""
        <div class="evo">
            <div class="evo-text">進化中！</div>
            <img src="data:image/png;base64,{b64}" width="200">
            <div class="evo-text">{st.session_state.evolving['name']}</div>
        </div>
        """, unsafe_allow_html=True)
        st.rerun()
    else:
        st.session_state.evolving = None
        st.session_state.coins += 300
        st.balloons()
        st.rerun()

# ===================== 7. 主畫面 =====================
st.title("寶可夢迷宮 V8.0")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("關卡", st.session_state.stage)
with col2:
    st.metric("金幣", st.session_state.coins)
with col3:
    st.metric("HP", f"❤️ {st.session_state.hp}")

# 道具欄
st.write("**背包**")
cols = st.columns(4)
items = ['pokeball', 'hint', 'bomb']
for i, item in enumerate(items):
    with cols[i]:
        st.write(f"**{item}**: {st.session_state.inventory[item]}")

# 迷宮
maze_div = "<div class='maze'>"
for y in range(5):
    for x in range(5):
        cell = st.session_state.maze[y][x]
        icon = {"player":"P", "pokemon":"pokeball", "boss":"B", "exit":"door", "wall":"brick", "path":"dot", "captured":"check", "trap":"warning"}.get(cell, "")
        cls = f"cell {cell}"
        maze_div += f"<div class='{cls}'>{icon}</div>"
maze_div += "</div>"
st.markdown(maze_div, unsafe_allow_html=True)

# 移動
def move(dx, dy):
    x, y = st.session_state.player
    nx, ny = x + dx, y + dy
    if 0 <= nx < 5 and 0 <= ny < 5 and st.session_state.maze[ny][nx] != 'wall':
        st.session_state.maze[y][x] = 'path'
        st.session_state.player = [nx, ny]
        st.session_state.maze[ny][nx] = 'player'
        # 陷阱
        if st.session_state.maze[ny][nx] == 'trap':
            st.session_state.hp -= 1
            play("trap")
            st.session_state.maze[ny][nx] = 'path'
            if st.session_state.hp <= 0:
                st.error("HP 歸零！遊戲結束！")
                st.session_state.game_state = 'gameover'
        st.rerun()

col1, col2, col3 = st.columns(3)
with col2:
    if st.button("上移"): move(0, -1)
col_l, col_c, col_r = st.columns(3)
with col_l:
    if st.button("左移"): move(-1, 0)
with col_r:
    if st.button("右移"): move(1, 0)
if st.button("下移"): move(0, 1)

# 遭遇
x, y = st.session_state.player
cell = st.session_state.maze[y][x]
if cell in ['pokemon', 'boss']:
    play("encounter")
    p1, p2 = random.sample(NAMES, 2)
    img = fuse(p1, p2)
    buf = io.BytesIO()
    img.save(buf, "PNG")
    b64 = base64.b64encode(buf.getvalue()).decode()
    st.image(f"data:image/png;base64,{b64}", width=200)
    st.write(f"**{'BOSS戰！' if cell=='boss' else '遭遇！'} 選出兩隻寶可夢**")
    
    opts = [p1, p2] + random.sample([n for n in NAMES if n not in (p1,p2)], 2)
    random.shuffle(opts)
    
    col1, col2 = st.columns(2)
    with col1:
        g1 = st.selectbox("第一隻", opts, key="g1")
    with col2:
        g2 = st.selectbox("第二隻", opts, key="g2")
    
    if st.button("捕捉！"):
        if {g1, g2} == {p1, p2}:
            play("capture")
            st.success("捕捉成功！")
            st.session_state.captured.append(f"{p1}+{p2}")
            st.session_state.coins += 100
            st.session_state.score += 50
            # 進化檢查
            for base, (next_form, count) in EVOLUTION.items():
                if base in [p1, p2] and sum(1 for c in st.session_state.captured if base in c) >= count:
                    show_evo(base, next_form)
            st.session_state.maze[y][x] = 'captured'
            if cell == 'boss':
                st.session_state.boss_defeated = True
            st.balloons()
        else:
            play("escape")
            st.error("答錯了！逃跑了！")
            st.session_state.maze[y][x] = 'path'
        st.rerun()

# 出口
if cell == 'exit' and (st.session_state.stage % 5 != 0 or st.session_state.boss_defeated):
    play("victory")
    st.success(f"第 {st.session_state.stage} 關破關！+200金幣")
    st.session_state.coins += 200
    st.session_state.score += 200
    if st.button("下一關"):
        st.session_state.stage += 1
        st.session_state.maze = generate_maze()
        st.session_state.player = [0, 0]
        st.session_state.boss_defeated = False
        st.rerun()

# 商店
with st.expander("商店"):
    col1, col2 = st.columns(2)
    with col1:
        if st.button("精靈球 ×1 (50金幣)", disabled=st.session_state.coins < 50):
            st.session_state.coins -= 50
            st.session_state.inventory['pokeball'] += 1
            play("buy")
            st.rerun()
    with col2:
        if st.button("提示 ×1 (80金幣)", disabled=st.session_state.coins < 80):
            st.session_state.coins -= 80
            st.session_state.inventory['hint'] += 1
            play("buy")
            st.rerun()

# 排行榜
if st.button("提交成績"):
    name = st.text_input("輸入名字")
    if name:
        st.session_state.leaderboard.append({"name": name, "score": st.session_state.score, "stage": st.session_state.stage})
        st.session_state.leaderboard = sorted(st.session_state.leaderboard, key=lambda x: x["score"], reverse=True)[:5]
        st.success("提交成功！")
with st.expander("排行榜"):
    if st.session_state.leaderboard:
        for i, entry in enumerate(st.session_state.leaderboard):
            st.write(f"**{i+1}. {entry['name']}** - {entry['score']} 分 (第 {entry['stage']} 關)")
    else:
        st.write("暫無紀錄")

# 圖鑑
if st.session_state.captured:
    with st.expander("圖鑑"):
        for c in st.session_state.captured[-5:]:
            st.write(f"Pokeball {c}")