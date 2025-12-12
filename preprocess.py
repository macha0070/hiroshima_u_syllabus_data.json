import json
from janome.tokenizer import Tokenizer
from sklearn.feature_extraction.text import TfidfVectorizer

# ==========================================
# 1. データの読み込み 
# ==========================================

# スクレイピングした実際のファイル名を指定
input_file = "subject_details_main_2025-04-03.json"
output_file = "syllabus_vectors.json"

try:
    with open(input_file, 'r', encoding='utf-8') as f:
        # 辞書形式 {"ID": {データ}, ...} として読み込み
        syllabus_data = json.load(f)
        
    print(f"成功: {len(syllabus_data)} 件のデータを読み込みました。")

except FileNotFoundError:
    print(f"エラー: {input_file} が見つかりません。同じフォルダに置いてください。")
    exit()

# ==========================================
# 前処理の関数定義
# ==========================================

# Janomeの準備
t = Tokenizer()

def get_words(text):
    """
    文章を受け取り、意味のある「名詞」だけをスペース区切りで返す関数
    """
    tokens = t.tokenize(text)
    words = []
    for token in tokens:
        part_of_speech = token.part_of_speech.split(',')[0]
        if part_of_speech in ['名詞']:
            words.append(token.base_form)
    return " ".join(words)

# ==========================================
# メイン処理：テキスト統合と分かち書き
# ==========================================

print("1. テキストの統合と分かち書きを実行中...")

corpus = []       # 分かち書きしたテキストのリスト
course_ids = []   # IDのリスト
course_names = [] # 授業名のリスト

# 辞書型なので .items() で回す
for code_key, info in syllabus_data.items():
    
    # ID取得
    course_id = code_key 

    # データが辞書型であることを確認
    if not isinstance(info, dict):
        continue

    # 1. 分析に使いたいフィールドを結合
    # ※Noneが入っている場合に備えて str() で囲むか "" をデフォルトにする
    full_text = (
        str(info.get("授業科目名", "")) + " " +
        str(info.get("授業の目標・概要等", "")) + " " +
        str(info.get("メッセージ", "")) + " " +
        str(info.get("履修上の注意 受講条件等", ""))
    )
    
    # 2. 名詞だけ抜き出す
    words = get_words(full_text)
    
    # 単語が抽出できなかった（空っぽの）授業はスキップ
    if not words:
        continue

    # 3. リストに追加
    corpus.append(words)
    course_ids.append(course_id)
    course_names.append(info.get("授業科目名", "名称不明"))

print(f"サンプル: {corpus[0][:50]}...") 


# ==========================================
# ベクトル化 (TF-IDF)
# ==========================================

print("\n2. ベクトル化(TF-IDF)を実行中...")

# 【重要】Webアプリで軽く動かすために、特徴語をトップ300個に絞ります
# これがないとファイルサイズが数百MBになり、ブラウザで動きません
vectorizer = TfidfVectorizer(max_features=300)

# 計算実行
X = vectorizer.fit_transform(corpus)
vectors = X.toarray().tolist()

print(f"  ベクトル次元数: {len(vectors[0])} (300なら成功)")


# ==========================================
# 結果の保存
# ==========================================

print("3. ファイル保存中...")

output_data = []

for i, vector in enumerate(vectors):
    output_data.append({
        "id": course_ids[i],
        "name": course_names[i],
        "vector": vector
    })

# JSONファイルに書き出し
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(output_data, f, ensure_ascii=False) 

print(f"\n完了！ '{output_file}' に保存しました。")