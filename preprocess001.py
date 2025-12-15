import json
from janome.tokenizer import Tokenizer
from sklearn.feature_extraction.text import TfidfVectorizer

# ==========================================
# 設定
# ==========================================
input_file = "subject_details_main_2025-04-03.json"
output_file = "syllabus_vectors.json" # この中にベクトルと辞書を両方入れます

# ==========================================
# データの読み込み
# ==========================================
try:
    with open(input_file, 'r', encoding='utf-8') as f:
        syllabus_data = json.load(f)
    print(f"データ読み込み完了: {len(syllabus_data)}件")
except FileNotFoundError:
    print("エラー: 入力ファイルが見つかりません")
    exit()

# ==========================================
# 前処理（分かち書き）
# ==========================================
t = Tokenizer()

def get_words(text):
    tokens = t.tokenize(text)
    words = []
    for token in tokens:
        # 名詞だけに絞る
        if token.part_of_speech.split(',')[0] in ['名詞']:
            words.append(token.base_form)
    return " ".join(words)

print("形態素解析中...")
corpus = []
course_ids = []
course_names = []

for code_key, info in syllabus_data.items():
    if not isinstance(info, dict): continue

    # 検索に使いたいテキストを結合
    full_text = (
        str(info.get("授業科目名", "")) + " " +
        str(info.get("授業の目標・概要等", "")) + " " +
        str(info.get("メッセージ", "")) + " " +
        str(info.get("履修上の注意 受講条件等", ""))
    )
    
    words = get_words(full_text)
    if not words: continue

    corpus.append(words)
    course_ids.append(code_key)
    course_names.append(info.get("授業科目名", "名称不明"))

# ==========================================
# ベクトル化
# ==========================================
print("ベクトル化中...")

# max_features=500: 上位500語だけを使う
vectorizer = TfidfVectorizer(max_features=500)
X = vectorizer.fit_transform(corpus)

# 疎行列から非ゼロ要素のみ抽出 (Sparse Format)
# X は scipy.sparse.csr_matrix
print("データを圧縮中...")
sparse_vectors = []
for i in range(X.shape[0]):
    row = X.getrow(i)
    indices = row.indices.tolist()
    data = row.data.tolist()
    # 小数点以下を丸めてサイズ削減 (例: 0.123456 -> 0.123)
    data_rounded = [round(v, 3) for v in data]
    
    # { "i": [indices], "v": [values] }
    sparse_vectors.append([indices, data_rounded])

# 語彙辞書
vocabulary = {k: int(v) for k, v in vectorizer.vocabulary_.items()}

# ==========================================
# 保存 1: ベクトルデータ (検索用)
# ==========================================
# syllabus_vectors.json
# 構造: { "vocab": {...}, "vecs": [ [ [idx], [val] ], ... ], "ids": [...] }
# IDリストもこちらに入れて、インデックスで同期させる
output_vector_data = {
    "v": vocabulary,
    "d": sparse_vectors, # Data
    "i": course_ids      # IDs (to map index -> ID)
}

with open(output_file, "w", encoding="utf-8") as f:
    json.dump(output_vector_data, f, ensure_ascii=False, separators=(',', ':'))

print(f"完了！ '{output_file}' (ベクトルデータ) を保存しました。")


# ==========================================
# 保存 2: メタデータ (表示用 Lightweight)
# ==========================================
metadata_file = "course_metadata.json"
print("メタデータを生成中...")

metadata_map = {}
for i, cid in enumerate(course_ids):
    # 生データから必要な情報だけ抽出
    raw = syllabus_data.get(cid, {})
    metadata_map[cid] = {
        "n": raw.get("授業科目名", ""),       # Name
        "d": raw.get("開講部局", ""),         # Dept
        "t": raw.get("開設期", ""),           # Term
        "w": raw.get("曜日・時限・講義室", ""), # When/Where
        "i": raw.get("担当教員名", "")        # Instructor
    }

with open(metadata_file, "w", encoding="utf-8") as f:
    json.dump(metadata_map, f, ensure_ascii=False, separators=(',', ':'))

print(f"完了！ '{metadata_file}' (メタデータ) を保存しました。")
print(f"採用された単語数: {len(vocabulary)}")