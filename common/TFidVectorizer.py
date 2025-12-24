import json
import pandas as pd
from janome.tokenizer import Tokenizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ==========================================
# 設定
# ==========================================
JSON_FILE = "all_syllabus_merged.json" # マージ済みのファイル
TARGET_KEYWORD = "プログラミング"       # 検索したいキーワード（または授業名の一部）

# ==========================================
# 1. データの読み込みと前処理
# ==========================================
print("データを読み込んでいます...")

try:
    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
except FileNotFoundError:
    print(f"エラー: {JSON_FILE} が見つかりません。")
    exit()

# データフレームに変換
df = pd.DataFrame(data)

# 分析に使うテキストを1つにまとめる
# 授業名 + 授業計画 + アドバイス などの文章を全部つなげる
df['combined_text'] = (
    df['course_name'].fillna('') + " " + 
    df.get('schedule', pd.Series([""] * len(df))).fillna('') + " " + 
    df.get('advice', pd.Series([""] * len(df))).fillna('') + " " + 
    df.get('textbooks', pd.Series([""] * len(df))).fillna('')
)

print(f"データ数: {len(df)} 件")

# ==========================================
# 2. 日本語の形態素解析（分かち書き）
# ==========================================
print("日本語を解析しています（少し時間がかかります）...")
t = Tokenizer()

def tokenize(text):
    """文章を単語のリストに変換する関数"""
    tokens = []
    for token in t.tokenize(text):
        # 名詞のみを抽出すると精度が上がりやすい
        if token.part_of_speech.split(',')[0] in ['名詞']: 
            tokens.append(token.surface)
    return " ".join(tokens)

# 全データのテキストを単語区切りに変換
df['wakati_text'] = df['combined_text'].apply(tokenize)

# ==========================================
# 3. TF-IDF ベクトル化
# ==========================================
print("ベクトル化計算中...")
# max_features=1000: 上位1000語の重要単語のみ使用（計算軽量化）
vectorizer = TfidfVectorizer(max_features=1000) 
tfidf_matrix = vectorizer.fit_transform(df['wakati_text'])

# ==========================================
# 4. 検索・推薦機能
# ==========================================

def search_similar_courses(query_text, top_k=5):
    """
    入力されたテキスト（検索語や授業内容）に似ている授業を探す
    """
    # クエリ（検索語）も同じように処理
    query_wakati = tokenize(query_text)
    query_vec = vectorizer.transform([query_wakati])
    
    # コサイン類似度を計算（全授業と比較）
    similarities = cosine_similarity(query_vec, tfidf_matrix).flatten()
    
    # 類似度が高い順にインデックスを取得
    related_docs_indices = similarities.argsort()[::-1][:top_k]
    
    print(f"\nResult: '{query_text}' に関連する授業 TOP{top_k}:")
    print("-" * 50)
    
    for i in related_docs_indices:
        score = similarities[i]
        if score > 0: # 類似度が0より大きいものだけ表示
            print(f"スコア: {score:.4f} | 科目: {df.iloc[i]['course_name']}")
            # print(f"   URL: {df.iloc[i]['url']}") # URLがあれば表示
        else:
            pass

# ==========================================
# 実行
# ==========================================

# テスト1: キーワード検索
search_similar_courses(TARGET_KEYWORD)

# テスト2: 特定の授業データを使って、それに似たものを探す（レコメンド）
# 例: リストの最初の授業に似ているものを探す
if len(df) > 0:
    target_course_idx = 0 
    target_course_text = df.iloc[target_course_idx]['combined_text']
    target_course_name = df.iloc[target_course_idx]['course_name']
    
    print(f"\n\n--- レコメンドテスト ---")
    print(f"『{target_course_name}』を履修した人へのおすすめ:")
    search_similar_courses(target_course_text)