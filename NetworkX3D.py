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
json_path = 'subject_details_main_2025-04-03.json'
try:
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
except FileNotFoundError:
    print(f"Error: {json_path} が見つかりません。")
    sys.exit(1)

courses = []
for course_id, details in data.items():
    # 総合科学部のみ抽出
    if details.get("開講部局") == "総合科学部":
        title = details.get("授業科目名", "不明")
        text = details.get("授業の目標・概要等", "")
        if text:
            courses.append({
                "id": course_id,
                "title": title,
                "text": text
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

# クラスタリング（K-Means）
num_clusters = 5
kmeans = KMeans(n_clusters=num_clusters, random_state=42)
kmeans.fit(tfidf_matrix)
labels = kmeans.labels_
# 各コースにラベルを割り当て
for i, course in enumerate(courses):
    course["group"] = labels[i]

# 3. グラフ（ネットワーク）の生成
G = nx.Graph()

# ノード（授業）を追加
for course in courses:
    G.add_node(course["title"], group=course["group"])

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

# 点（ノード）を描画（色分け）
scatter = ax.scatter(x_nodes, y_nodes, z_nodes, s=100, c=node_colors, cmap='Set1', alpha=0.9, edgecolors="gray")

# 線（エッジ）を描画
for u, v in G.edges():
    x_coords = [pos[u][0], pos[v][0]]
    y_coords = [pos[u][1], pos[v][1]]
    z_coords = [pos[u][2], pos[v][2]]
    
    # 重みに応じた太さ
    weight = G[u][v]['weight']
    ax.plot(x_coords, y_coords, z_coords, color="gray", alpha=0.3, linewidth=weight * 3)

# ラベル（授業名）を描画
for node, (x, y, z) in pos.items():
    ax.text(x, y, z, node, fontsize=8, fontname="MS Gothic", alpha=0.8)

ax.set_title("総合科学部 授業相関ネットワーク (3D)", fontsize=15, fontname="MS Gothic")

# 軸ラベルの設定
ax.set_xlabel('X Axis')
ax.set_ylabel('Y Axis')
ax.set_zlabel('Z Axis')

# 凡例（カラーバー）の追加（簡易的）
cbar = plt.colorbar(scatter, ax=ax, pad=0.1)
cbar.set_label('Cluster Group')

print("3Dグラフを表示します。マウスで回転できます。")
plt.show()
