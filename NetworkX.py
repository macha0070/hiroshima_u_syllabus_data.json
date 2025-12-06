import networkx as nx
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# 1. データの準備（総合科学部っぽい、少しずつ関連した5つの授業）
courses = [
    {"id": "A", "title": "プログラミング基礎", "text": "Python データ 分析 アルゴリズム AI 計算機"},
    {"id": "B", "title": "認知科学", "text": "脳 思考 AI 人工知能 心理学 計算機 モデル"},
    {"id": "C", "title": "現代心理学", "text": "心理学 心 行動 認知 感情 ストレス"},
    {"id": "D", "title": "情報社会論", "text": "社会 情報 メディア ネットワーク データ AI 倫理"},
    {"id": "E", "title": "日本文学", "text": "文学 漱石 小説 文化 歴史 言葉"},
]

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
nx.draw_networkx_labels(G, pos, font_family="IPAGothic", font_size=10) # 日本語フォント指定（環境に合わせて変更要）
# ※ Colab等で日本語が出ない場合は font_family を削除して英字のみにするか、Japanize-matplotlibを入れてください

plt.title("総合科学部 授業相関ネットワーク", fontsize=15)
plt.axis("off")
plt.show()