"""
NetworkX3D.py
=============
シラバスデータ（JSON）を読み込み、TF-IDFとK-Meansクラスタリングを用いて授業をグループ化し、
NetworkXとMatplotlib (mplot3d) を使用して3次元の相関ネットワークグラフを描画するスクリプトです。

主な機能:
1. JSONデータのロードとフィルタリング（総合科学部のみ）
2. テキストのTF-IDFベクトル化とコサイン類似度計算
3. K-Means法による授業のクラスタリング（色分け用）
4. NetworkXによる3次元配置座標の計算 (spring_layout dim=3)
5. 3D散布図としてのノード描画とエッジの描画
6. マウス操作可能な3Dグラフの表示
"""
import json
import networkx as nx
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
import sys

# 日本語フォント設定（Windows向け/MS Gothic）
plt.rcParams['font.family'] = 'MS Gothic'

# 1. データの準備（JSONから読み込み）
json_path = 'integrated_arts_courses.json'
try:
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
except FileNotFoundError:
    print(f"Error: {json_path} が見つかりません。")
    sys.exit(1)

courses = []
for course_id, details in data.items():
    # 抽出済みファイルなので部局フィルタは不要（または全許可）
    title = details.get("授業科目名", "不明")
    text = details.get("授業の目標・概要等", "")
    field = details.get("分野", "未分類") # Get field
    if text:
        courses.append({
            "id": course_id,
            "title": title,
            "text": text,
            "field": field
        })

print(f"分析対象の授業数: {len(courses)}")

if len(courses) == 0:
    print("分析対象の授業が見つかりませんでした。")
    sys.exit(0)

# 2. 類似度の計算（TF-IDFを使用）
texts = [c["text"] for c in courses]
vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(texts)
similarity_matrix = cosine_similarity(tfidf_matrix)

# 分野ごとの色分け設定
# 分野リストを取得
unique_fields = list(set([c["field"] for c in courses]))
unique_fields.sort()
print("Fields found:", unique_fields)

# 色のマップを作成 (tab20などを使用)
import matplotlib.cm as cm
import numpy as np

# Apply colors based on field index
field_to_id = {f: i for i, f in enumerate(unique_fields)}
for c in courses:
    c["group"] = field_to_id[c["field"]]

# 3. グラフ（ネットワーク）の生成
G = nx.Graph()

# ノード（授業）を追加
for course in courses:
    G.add_node(course["title"], group=course["group"], field=course["field"])

# エッジ（線）を追加：類似度が「0.1以上」なら線を引く
threshold = 0.1
num_courses = len(courses)

edge_list = []
for i in range(num_courses):
    for j in range(i + 1, num_courses):
        sim = similarity_matrix[i][j]
        if sim > threshold:
            # 類似度を線の太さ（weight）にする
            G.add_edge(courses[i]["title"], courses[j]["title"], weight=sim)
            edge_list.append((courses[i]["title"], courses[j]["title"], sim))

print(f"エッジの数: {len(edge_list)}")

# 4. 可視化（3D描画）の設定
# 3次元配置を計算 (dim=3)
pos = nx.spring_layout(G, k=0.8, dim=3)

fig = plt.figure(figsize=(12, 10))
ax = fig.add_subplot(111, projection='3d')

# ノード（点）の座標と色を取得
x_nodes = [pos[node][0] for node in G.nodes()]
y_nodes = [pos[node][1] for node in G.nodes()]
z_nodes = [pos[node][2] for node in G.nodes()]
node_colors = [G.nodes[node]['group'] for node in G.nodes()]

# 点（ノード）を描画（色分け） - tab20を使用
scatter = ax.scatter(x_nodes, y_nodes, z_nodes, s=50, c=node_colors, cmap='tab20', alpha=0.9, edgecolors="gray")

# 線（エッジ）を描画
for u, v in G.edges():
    x_coords = [pos[u][0], pos[v][0]]
    y_coords = [pos[u][1], pos[v][1]]
    z_coords = [pos[u][2], pos[v][2]]
    
    # 重みに応じた太さ
    weight = G[u][v]['weight']
    ax.plot(x_coords, y_coords, z_coords, color="gray", alpha=0.2, linewidth=weight * 2)

# ラベル（授業名）を描画 - 削除 (Requested by user)
# for node, (x, y, z) in pos.items():
#     ax.text(x, y, z, node, fontsize=8, fontname="MS Gothic", alpha=0.8)

ax.set_title("総合科学部 授業相関ネットワーク (3D) - 色: 分野", fontsize=15, fontname="MS Gothic")

# 軸ラベルの設定
ax.set_xlabel('X Axis')
ax.set_ylabel('Y Axis')
ax.set_zlabel('Z Axis')

# 凡例（カラーバーではなく凡例リストにする）
# Create custom legend handles
from matplotlib.lines import Line2D
cmap = plt.get_cmap('tab20')
legend_elements = []
for i, field_name in enumerate(unique_fields):
    if not field_name: field_name = "未分類"
    # Choose color from map
    color = cmap(i / max(1, len(unique_fields) - 1)) if len(unique_fields) > 1 else cmap(0)
    legend_elements.append(Line2D([0], [0], marker='o', color='w', label=field_name,
                          markerfacecolor=color, markersize=10))

ax.legend(handles=legend_elements, title="分野", loc="upper right", prop={"family": "MS Gothic", "size": 8})

print("3Dグラフを表示します。マウスで回転できます。")
plt.show()
