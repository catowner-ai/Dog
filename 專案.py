import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from mpl_toolkits.mplot3d import Axes3D

# --- 0. 環境設定與文件讀取 ---
# 檔案名稱
file_name = 'RSTA3104_1141007.csv'

# 設定matplotlib中文顯示
# 這裡嘗試使用多個常見的中文/Unicode字體
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei', 'SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False # 解決負號'-'顯示為方塊的問題

try:
    # 讀取CSV檔案
    df = pd.read_csv(file_name)
except FileNotFoundError:
    print(f"錯誤：找不到檔案 {file_name}")
    exit()

# --- 1. 資料清理與預處理 ---
numeric_cols = ['收盤', '漲跌', '開盤', '最高', '最低', '均價', '成交股數', '成交金額', '成交筆數',
                '最後買價', '最後賣價', '發行股數', '次日參考價', '次日漲停價', '次日跌停價']

for col in numeric_cols:
    # 移除非數字字符並轉換為 float，無法轉換則設為 NaN
    df[col] = pd.to_numeric(df[col].astype(str).str.replace(r'[^\d\.\-]', '', regex=True), errors='coerce')

# 移除含有 NaN 值的行
df.dropna(subset=numeric_cols, inplace=True)

# 轉換 '資料日期' 欄位為日期時間格式
df['資料日期'] = pd.to_datetime(df['資料日期'], format='%Y%m%d', errors='coerce')

# --- 2. 數據分析與指標計算 ---
# 計算 '漲跌幅 (%)'
df['漲跌幅 (%)'] = (df['漲跌'] / (df['收盤'] - df['漲跌'])) * 100

# --- 3. 精美圖表生成 ---

# ----------------------------------------------------
# 3.1 熱力圖 (Heatmap) - 價格相關性分析
# ----------------------------------------------------
price_cols = ['開盤', '最高', '最低', '收盤', '均價', '漲跌幅 (%)']
correlation_matrix = df[price_cols].corr()

plt.figure(figsize=(8, 6))
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt=".2f", linewidths=.5, cbar_kws={'label': '相關係數'})
plt.title('價格與漲跌幅相關性熱力圖', fontsize=16)
plt.show()

# ----------------------------------------------------
# 3.2 圓餅圖 (Pie Chart) - 成交金額前五大股票佔比
# ----------------------------------------------------
top_5_stocks = df.nlargest(5, '成交金額')
other_amount = df['成交金額'].sum() - top_5_stocks['成交金額'].sum()

pie_data = top_5_stocks[['名稱', '成交金額']].copy()
pie_data.loc[len(pie_data)] = ['其他', other_amount]
labels = pie_data['名稱']
sizes = pie_data['成交金額']

plt.figure(figsize=(10, 10))
explode_list = [0.1] + [0] * (len(sizes) - 1)
plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90,
        wedgeprops={'edgecolor': 'black', 'linewidth': 1},
        shadow=True, explode=explode_list)
plt.title('成交金額前五大股票佔比 (總成交金額)', fontsize=16)
plt.axis('equal')
plt.show()

# ----------------------------------------------------
# 3.3 長條圖 (Bar Chart) - 成交股數與成交金額比較 (投影片 4)
# ----------------------------------------------------
top_10_volume = df.nlargest(10, '成交股數').sort_values(by='成交股數', ascending=False)
labels_bar = top_10_volume['名稱']

fig, ax1 = plt.subplots(figsize=(14, 7))

# 左 Y 軸：成交股數
volume_data = top_10_volume['成交股數'] / 1000000
color = 'tab:blue'
ax1.set_xlabel('股票名稱 (成交股數前 10 大)', fontsize=12)
ax1.set_ylabel('成交股數 (百萬股)', color=color, fontsize=12)
ax1.bar(labels_bar, volume_data, color=color, alpha=0.7, label='成交股數')
ax1.tick_params(axis='y', labelcolor=color)
ax1.set_xticklabels(labels_bar, rotation=45, ha='right')
ax1.grid(axis='y', linestyle='--', alpha=0.5)

# 右 Y 軸：成交金額
amount_data = top_10_volume['成交金額'] / 100000000
ax2 = ax1.twinx()
color = 'tab:red'
ax2.set_ylabel('成交金額 (億元)', color=color, fontsize=12)
ax2.plot(labels_bar, amount_data, color=color, marker='o', linestyle='-', linewidth=2, label='成交金額')
ax2.tick_params(axis='y', labelcolor=color)

plt.title('成交股數前 10 大股票：股數與金額比較', fontsize=16)
fig.tight_layout()
plt.show()

# ----------------------------------------------------
# 3.4 散佈圖 (Scatter Plot) - 價格 vs. 漲跌幅 (氣泡大小代表成交股數) (投影片 5)
# ----------------------------------------------------
# 排除收盤價小於 1 元的數據點 (優化)
plot_df_filtered = df[df['收盤'] >= 1].copy()

# 設置顏色：漲跌幅 > 0 為紅，否則為綠/灰
plot_df_filtered['Color'] = np.where(plot_df_filtered['漲跌幅 (%)'] > 0, 'red', 
                                     np.where(plot_df_filtered['漲跌幅 (%)'] < 0, 'green', 'gray'))

# 設置氣泡大小：將成交股數縮放並限制上限
plot_df_filtered['Size'] = plot_df_filtered['成交股數'] / 100000
plot_df_filtered['Size'] = plot_df_filtered['Size'].clip(upper=3000)

plt.figure(figsize=(14, 8))

plt.scatter(
    plot_df_filtered['收盤'], 
    plot_df_filtered['漲跌幅 (%)'], 
    s=plot_df_filtered['Size'], 
    c=plot_df_filtered['Color'],
    alpha=0.6,
    edgecolors='w',
    linewidth=0.5
)

plt.xlabel('收盤價 (元)', fontsize=14)
plt.ylabel('漲跌幅 (%)', fontsize=14)
plt.title('收盤價 vs. 漲跌幅 (氣泡大小代表成交股數)', fontsize=16)

# 設定優化後的座標軸範圍
plt.xlim(0, 500) 
plt.ylim(-10.5, 10.5) 
plt.axhline(10, color='red', linestyle=':', linewidth=1, alpha=0.5)
plt.axhline(-10, color='green', linestyle=':', linewidth=1, alpha=0.5)
plt.axhline(0, color='black', linestyle='--', linewidth=1, alpha=0.7)

# 添加圖例 (Legend for Size)
handles = [
    plt.Line2D([0], [0], marker='o', color='w', label='500萬股', 
               markerfacecolor='gray', markersize=np.sqrt(5000000 / 100000)),
    plt.Line2D([0], [0], marker='o', color='w', label='2000萬股', 
               markerfacecolor='gray', markersize=np.sqrt(20000000 / 100000)),
    plt.Line2D([0], [0], marker='o', color='w', label='5000萬股', 
               markerfacecolor='gray', markersize=np.sqrt(50000000 / 100000))
]
plt.legend(handles=handles, title="成交股數參考", loc='upper right')

plt.grid(True, linestyle=':', alpha=0.5)
plt.show()

# ----------------------------------------------------
# 3.5 折線圖 (Line Plot) - 漲跌幅與成交股數關係 (投影片 6)
# ----------------------------------------------------
# 按漲跌幅排序
plot_df_line = df.sort_values(by='漲跌幅 (%)', ascending=False).reset_index(drop=True)

fig, ax1 = plt.subplots(figsize=(12, 6))

# 繪製漲跌幅 (左Y軸)
color = 'tab:red'
ax1.set_xlabel('股票 (按漲跌幅排序的序號)', fontsize=12)
ax1.set_ylabel('漲跌幅 (%)', color=color, fontsize=12)
ax1.plot(plot_df_line.index, plot_df_line['漲跌幅 (%)'], color=color, label='漲跌幅 (%)')
ax1.tick_params(axis='y', labelcolor=color)
ax1.grid(True, linestyle='--', alpha=0.6)

# 建立第二個Y軸 (右Y軸)
ax2 = ax1.twinx()
color = 'tab:blue'
ax2.set_ylabel('成交股數 (百萬股)', color=color, fontsize=12)
ax2.plot(plot_df_line.index, plot_df_line['成交股數'] / 1000000, color=color, linestyle='--', alpha=0.7, label='成交股數')
ax2.tick_params(axis='y', labelcolor=color)

plt.title('股票漲跌幅與成交股數趨勢 (排序觀察)', fontsize=16)
ax1.set_xticks([])
fig.tight_layout()
plt.show()

# ----------------------------------------------------
# 3.6 3D 柱狀圖 (3D Bar Plot) - 成交股數前 5 大股票 (投影片 7)
# ----------------------------------------------------
# 選擇成交股數最大的前 5 支股票
top_5_volume = df.nlargest(5, '成交股數').copy()

fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')

# 數據
x_data = top_5_volume['收盤']
y_data = top_5_volume['漲跌幅 (%)']
z_data = top_5_volume['成交股數'] / 1000000 # 轉換為百萬股
labels_3d = top_5_volume['名稱']

# 柱子定位
xpos = x_data.values
ypos = y_data.values
zpos = np.zeros_like(z_data.values)
dx = np.ones_like(xpos) * (xpos.max() - xpos.min()) / 10
dy = np.ones_like(ypos) * 0.5
dz = z_data.values

# 繪製3D柱狀圖
ax.bar3d(xpos, ypos, zpos, dx, dy, dz, shade=True, color='purple', alpha=0.8)

ax.set_xlabel('收盤價 (元)', fontsize=12, labelpad=10)
ax.set_ylabel('漲跌幅 (%)', fontsize=12, labelpad=10)
ax.set_zlabel('成交股數 (百萬股)', fontsize=12, labelpad=10)
ax.set_title('成交股數前 5 大股票的 3D 關係', fontsize=16)

# 在柱子頂部標註名稱
for i in range(len(top_5_volume)):
    ax.text(xpos[i], ypos[i] + dy[i] / 2, zpos[i] + dz[i] * 1.05, 
            labels_3d.iloc[i], 
            color='black', 
            fontsize=9, 
            fontweight='bold',
            ha='center')

ax.view_init(elev=25, azim=40) 
plt.show()


# 3.7 直方圖 (Histogram) - 漲跌幅分佈 (投影片 8)
# ----------------------------------------------------
# 排除極端值，僅查看 -10% 到 +10% 之間的數據，以聚焦市場常態
change_df = df[(df['漲跌幅 (%)'] >= -10.5) & (df['漲跌幅 (%)'] <= 10.5)].copy()

# 根據漲跌幅的正負設置顏色，用於繪製直方圖
change_df['Change_Direction'] = np.where(change_df['漲跌幅 (%)'] > 0, '上漲', 
                                         np.where(change_df['漲跌幅 (%)'] < 0, '下跌', '持平'))
colors = {'上漲': 'red', '下跌': 'green', '持平': 'gray'}

plt.figure(figsize=(12, 6))



# 使用 plt.hist 繪製直方圖
# 創建三個數據集：上漲、下跌、持平
data_up = change_df[change_df['Change_Direction'] == '上漲']['漲跌幅 (%)']
data_down = change_df[change_df['Change_Direction'] == '下跌']['漲跌幅 (%)']
data_flat = change_df[change_df['Change_Direction'] == '持平']['漲跌幅 (%)']

# bins設定區間，例如每 0.5% 一個區間
bins = np.arange(-10.0, 10.5, 0.5)

plt.hist(data_up, bins=bins, color='red', alpha=0.7, label='上漲 (Count)')
plt.hist(data_down, bins=bins, color='green', alpha=0.7, label='下跌 (Count)')
plt.hist(data_flat, bins=bins, color='gray', alpha=0.8, label='持平 (Count)')

plt.xlabel('漲跌幅 (%)', fontsize=14)
plt.ylabel('股票數量 (檔)', fontsize=14)
plt.title('市場漲跌幅分佈直方圖 (-10% 至 +10%)', fontsize=16)

plt.legend(loc='upper left')
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.xticks(np.arange(-10, 11, 1)) # X軸標籤間距設為 1%
plt.show()

# 3.8 盒鬚圖 (Box Plot) - 價格區間漲跌幅分佈 (投影片 9)
# ----------------------------------------------------
# 排除收盤價小於 1 元的數據點
box_plot_df = df[df['收盤'] >= 1].copy()

# 定義價格區間
def categorize_price(price):
    if price <= 20:
        return '低價股 (<= 20元)'
    elif price <= 100:
        return '中價股 (20元 < P <= 100元)'
    else:
        return '高價股 (> 100元)'

box_plot_df['價格類別'] = box_plot_df['收盤'].apply(categorize_price)

# 設置繪圖順序
category_order = ['低價股 (<= 20元)', '中價股 (20元 < P <= 100元)', '高價股 (> 100元)']

plt.figure(figsize=(10, 8))
sns.boxplot(x='價格類別', y='漲跌幅 (%)', data=box_plot_df, 
            order=category_order, 
            palette=['#A569BD', '#5DADE2', '#58D683'], # 自定義顏色
            notch=True, 
            medianprops={'color': 'black', 'linewidth': 2})

plt.xlabel('股票價格類別', fontsize=14)
plt.ylabel('漲跌幅 (%)', fontsize=14)
plt.title('不同價格區間的漲跌幅分佈 (盒鬚圖)', fontsize=16)

# 限制 Y 軸範圍以聚焦常態分佈，並顯示漲跌停線
plt.ylim(-10.5, 10.5) 
plt.axhline(10, color='red', linestyle=':', linewidth=1, alpha=0.5)
plt.axhline(-10, color='green', linestyle=':', linewidth=1, alpha=0.5)

plt.grid(axis='y', linestyle='--', alpha=0.5)
plt.show()


print("\n--- 程式碼執行完畢 ---")
print("所有圖表已生成，請根據圖表結果填寫 Markdown 報告。")

