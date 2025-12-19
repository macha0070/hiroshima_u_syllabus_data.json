"""
NetworkX.py
===========
シラバスデータ（JSON）を読み込み、TF-IDFとコサイン類似度を用いて授業間の類似度を計算し、
NetworkXを使用して2次元の相関ネットワークグラフを描画するスクリプトです。

主な機能:
1. JSONデータのロードとフィルタリング（総合科学部のみ）
2. テキスト（授業の目標・概要等）のTF-IDFベクトル化
3. コサイン類似度の計算
4. 類似度が閾値（0.1）以上の授業間にエッジを張る
5. Matplotlibによる2Dネットワーク図の可視化
"""
import networkx as nx
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# 日本語フォント設定（Windows向け）
plt.rcParams['font.family'] = 'MS Gothic'

import json

# 1. データの準備（JSONから読み込み）
json_path = 'subject_details_main_2025-04-03.json'
with open(json_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

courses = []
for course_id, details in data.items():
    # 総合科学部のみ抽出
    if details.get("開講部局") == "総合科学部":
        title = details.get("授業科目名", "不明")
        # テキストとして「授業の目標・概要等」を使用。なければ空文字
        text = details.get("授業の目標・概要等", "")
        # テキストが空でない場合のみ追加（または空でも追加するかは要件次第だが、空だと類似度計算できないので除外推奨だがとりあえず入れる）
        if text:
            courses.append({
                "id": course_id,
                "title": title,
                "text": text
            })

print(f"分析対象の授業数: {len(courses)}")

# 2. 類似度の計算（TF-IDFを使用）
texts = [c["text"] for c in courses]
vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(texts)
similarity_matrix = cosine_similarity(tfidf_matrix)

# 3. グラフ（ネットワーク）の生成
G = nx.Graph()

# ノード（授業）を追加
for course in courses:
    G.add_node(course["title"])

# エッジ（線）を追加：類似度が「0.1以上」なら線を引く
threshold = 0.1
num_courses = len(courses)

print("--- つながりの強さ（エッジ） ---")
for i in range(num_courses):
    for j in range(i + 1, num_courses):
        sim = similarity_matrix[i][j]
        if sim > threshold:
            # 類似度を線の太さ（weight）にする
            G.add_edge(courses[i]["title"], courses[j]["title"], weight=sim)
            print(f"{courses[i]['title']} <--> {courses[j]['title']} : {sim:.2f}")

# 4. 可視化（描画）の設定
plt.figure(figsize=(10, 8))
pos = nx.spring_layout(G, k=0.8) # バネモデル（つながりが強いほど近くに配置される）

# 線（エッジ）を描画
weights = [G[u][v]['weight'] * 5 for u, v in G.edges()] # 類似度が高いほど太く
nx.draw_networkx_edges(G, pos, width=weights, alpha=0.5, edge_color="gray")

# 点（ノード）を描画
nx.draw_networkx_nodes(G, pos, node_size=3000, node_color="skyblue", alpha=0.9)

# ラベル（授業名）を描画
nx.draw_networkx_labels(G, pos, font_family="MS Gothic", font_size=10) # 日本語フォント指定（環境に合わせて変更要）
# ※ Colab等で日本語が出ない場合は font_family を削除して英字のみにするか、Japanize-matplotlibを入れてください

plt.title("総合科学部 授業相関ネットワーク", fontsize=15, fontname="MS Gothic")
plt.axis("off")
plt.show()