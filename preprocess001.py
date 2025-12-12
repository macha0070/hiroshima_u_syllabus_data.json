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

# ==========================================
# ベクトル化
# ==========================================
print("ベクトル化中...")

# max_features=500: 上位500語だけを使う（これでブラウザからの検索が可能になる）
vectorizer = TfidfVectorizer(max_features=500)
X = vectorizer.fit_transform(corpus)
vectors = X.toarray().tolist()

# 【重要】単語辞書を取得 (例: {"数学": 0, "文化": 1, ...})
# これがあれば、ブラウザ側で「数学」と打たれた時に 0番目の数字を見ればいいと分かる
vocabulary = vectorizer.vocabulary_

# ==========================================
# 保存
# ==========================================
# 授業ごとのデータと、全体の辞書をひとまとめにする
output_json = {
    "vocabulary": vocabulary,  # 辞書データ
    "courses": []              # 各授業のベクトル
}

for i, vector in enumerate(vectors):
    output_json["courses"].append({
        "id": course_ids[i],
        "vector": vector
    })

with open(output_file, "w", encoding="utf-8") as f:
    json.dump(output_json, f, ensure_ascii=False)

print(f"完了！ '{output_file}' に保存しました。")
print(f"採用された単語数: {len(vocabulary)}")