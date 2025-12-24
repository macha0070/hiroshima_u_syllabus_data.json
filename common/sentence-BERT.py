# !pip install sentence-transformers  <-- これを実行してライブラリを入れる

from sentence_transformers import SentenceTransformer, util
import pandas as pd

# 1. 高性能な学習済みモデルを読み込む（日本語対応モデル）
# これが「言葉の意味」を理解しているAIの脳みそです
model = SentenceTransformer('stsb-xlm-r-multilingual')

# 2. シラバスデータ（さきほどと同じ）
courses = [
    {"title": "授業A：プログラミング基礎", "text": "Pythonを用いてデータ分析やアルゴリズムを実装し、技術を習得する"},
    {"title": "授業B：近代日本文学", "text": "夏目漱石や森鴎外などの小説を読み、日本の文化や歴史、情緒を分析する"},
    {"title": "授業C：認知科学入門", "text": "人間の思考の仕組みや脳の働きを、計算機モデルを用いて科学的に解明する"},
]

# 3. ユーザーの興味（あえて曖昧な表現にしてみます）
user_interest = "コンピュータを使って、人の気持ちや考えを知りたい"

# --- ここから計算 ---

# シラバスとユーザー入力を一気に「意味ベクトル」に変換
# TF-IDFと違い、ここはAIが文章の意味を数値化しています
course_texts = [c["text"] for c in courses]
course_embeddings = model.encode(course_texts)
user_embedding = model.encode(user_interest)

# コサイン類似度を計算
similarities = util.cos_sim(user_embedding, course_embeddings)

# --- 結果表示 ---
print(f"【学生の興味】: {user_interest}\n")
print("--- SBERTによる推論結果 ---")

results = []
for i, score in enumerate(similarities[0]):
    results.append({"title": courses[i]["title"], "score": score.item()})

results.sort(key=lambda x: x["score"], reverse=True)

for res in results:
    print(f"マッチ度 {res['score']*100:.1f}% : {res['title']}")