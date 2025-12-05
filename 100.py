# 必要なライブラリ（scikit-learn）
# インストールしていない場合は pip install scikit-learn で入ります
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd

# 1. 仮想のシラバスデータ（本来はここを大学のサイトから取得します）
# ※日本語の単語をスペースで区切って簡易化しています
courses = [
    {"title": "授業A：プログラミング基礎", "text": "Python を 用いて データ 分析 や AI 人工知能 の 基礎 を 学び 技術 を 習得 する"},
    {"title": "授業B：近代日本文学", "text": "夏目漱石 や 森鴎外 などの 小説 を 読み 日本 の 文化 や 歴史 心 の 動き を 分析 する"},
    {"title": "授業C：認知科学入門", "text": "人間 の 心 の 仕組み や 脳 の 働き を AI 人工知能 の モデル を 用いて 科学的 に 分析 する"},
]

# 2. 学生の「やりたいこと」を入力（ここを変えて遊べます）
user_interest = "AI と 人間 の 心 の 関係 について 知りたい"

# --- ここから裏側の計算ロジック ---

# 全データ（授業＋学生の興味）をまとめる
texts = [c["text"] for c in courses] + [user_interest]

# 文字を「数値ベクトル」に変換する（TF-IDF法）
vectorizer = TfidfVectorizer()
vectors = vectorizer.fit_transform(texts)

# 「学生の興味」と「各授業」の距離（類似度）を計算
# 最後のベクトル（学生）と、それ以外（授業）を比較
user_vec = vectors[-1]
course_vecs = vectors[:-1]
similarities = cosine_similarity(user_vec, course_vecs)

# --- 結果の表示 ---

print(f"【学生の興味】: {user_interest}\n")
print("--- おすすめ授業ランキング ---")

# 結果を整理して表示
results = []
for i, score in enumerate(similarities[0]):
    results.append({"title": courses[i]["title"], "score": score})

# スコアが高い順に並び替え
results.sort(key=lambda x: x["score"], reverse=True)

for res in results:
    # スコアを%表示（100%に近いほどマッチしている）
    print(f"マッチ度 {res['score']*100:.1f}% : {res['title']}")