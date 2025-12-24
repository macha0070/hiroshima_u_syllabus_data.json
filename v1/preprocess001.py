"""
preprocess001.py
================
シラバスのJSONデータを読み込み、形態素解析（Janome）を行って名詞を抽出し、
TF-IDFベクトル化を行って検索用のベクトルデータを作成する前処理スクリプトです。

主な機能:
1. JSONデータのロード
2. テキストの正規化 (NFKC, ブラケット削除)
3. Janomeによる日本語形態素解析と名詞抽出（分かち書き）
4. Scikit-learnによるTF-IDFベクトル化（上位500語）
5. 疎行列データの圧縮と整形
6. ベクトルデータ (`syllabus_vectors.json`) とメタデータ (`course_metadata.json`) の保存
7. 類似授業データの計算と保存 (`recommendations.json`)
"""
# ==========================================
# Script Name: preprocess001.py
# Description:
#   [EN] Basic preprocessing script for syllabus data.
#        Performs morphological analysis, vectorization, and generates metadata.
#        Does NOT include the advanced skill extraction of preprocess002.py.
#   [JP] シラバスデータの基本的な前処理スクリプト。
#        形態素解析、ベクトル化、メタデータの生成を行います。
#        preprocess002.pyのような高度なスキル抽出機能は含まれていません。
#
# Data Flow:
#   Input  : reduced_integrated_arts_courses.json
#   Output : syllabus_vectors.json
#          : course_metadata.json
#          : recommendations.json
# ==========================================

import json
import re
import unicodedata
import numpy as np
from janome.tokenizer import Tokenizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ==========================================
# 設定
# ==========================================
# デモ用に軽量なファイルを使用する場合はこちら
input_file = "../common_data/integrated_arts_courses.json"
# input_file = "../common_data/subject_details_main_2025-04-03.json" # 全データを使う場合

output_file = "syllabus_vectors.json" # ベクトルデータ
metadata_file = "course_metadata.json" # メタデータ
recommendation_file = "recommendations.json" # おすすめ授業データ

# ==========================================
# データの読み込み
# ==========================================
try:
    with open(input_file, 'r', encoding='utf-8') as f:
        syllabus_data = json.load(f)
    print(f"データ読み込み完了: {len(syllabus_data)}件")
except FileNotFoundError:
    print(f"エラー: 入力ファイル '{input_file}' が見つかりません")
    exit()

# ==========================================
# 前処理関数
# ==========================================
t = Tokenizer()

def normalize_text(text):
    """
    テキストの正規化を行う
    1. NFKC正規化 (全角英数→半角, など)
    2. 不要な空白の削除
    """
    if not text:
        return ""
    normalized = unicodedata.normalize('NFKC', text)
    return normalized.strip()

def clean_course_name(name):
    """
    授業名から [1総総] などの分類タグを削除する
    """
    if not name:
        return ""
    # [1総総,1文...] のようなパターンを削除
    # 貪欲マッチにならないように注意
    cleaned = re.sub(r'\[.*?\]', '', name)
    return cleaned.strip()

def get_words(text):
    """
    形態素解析して名詞リスト（スペース区切り）を返す
    """
    # 正規化してから解析
    text = normalize_text(text)
    tokens = t.tokenize(text)
    words = []
    for token in tokens:
        # 名詞だけに絞る
        if token.part_of_speech.split(',')[0] in ['名詞']:
            words.append(token.base_form)
    return " ".join(words)

# ==========================================
# メイン処理: テキスト抽出
# ==========================================
def main():
    print("形態素解析と正規化を実行中...")
    corpus = []
    course_ids = []

    # 生成されるメタデータをここで準備
    metadata_map = {}

    for code_key, info in syllabus_data.items():
        if not isinstance(info, dict): continue

        # 元データ取得 & 正規化
        raw_name = str(info.get("授業科目名", ""))
        norm_name = normalize_text(raw_name)     # 正規化のみ
        clean_name = clean_course_name(norm_name) # 表示用にタグ削除

        target_text = (
            clean_name + " " +
            str(info.get("授業の目標・概要等", "")) + " " +
            str(info.get("メッセージ", "")) + " " +
            str(info.get("履修上の注意 受講条件等", ""))
        )
        
        words = get_words(target_text)
        # 単語がなくてもメタデータとしては登録すべき（検索にはヒットしないがグリッドには出るかも）
        # しかしベクトル化の都合上、corpusとidsは同期が必要。空文字列でもcorpusに追加する。
        
        corpus.append(words)
        course_ids.append(code_key)

        # メタデータ構築
        metadata_map[code_key] = {
            "n": clean_name,                        # Name (Cleaned)
            "d": normalize_text(info.get("開講部局", "")),
            "t": normalize_text(info.get("開設期", "")),
            "w": normalize_text(info.get("曜日・時限・講義室", "")),
            "i": normalize_text(info.get("担当教員名", "")),
            "a": normalize_text(info.get("領域", "")),
            "f": normalize_text(info.get("分野", ""))
        }

    # ==========================================
    # ベクトル化 (TF-IDF)
    # ==========================================
    print("ベクトル化中...")

    # max_features=500: 上位500語
    vectorizer = TfidfVectorizer(max_features=500)
    X = vectorizer.fit_transform(corpus)

    # 疎行列から非ゼロ要素のみ抽出 (Sparse Format)
    print("データを圧縮中...")
    sparse_vectors = []
    for i in range(X.shape[0]):
        row = X.getrow(i)
        indices = row.indices.tolist()
        data = row.data.tolist()
        # 小数点以下3桁に丸める
        data_rounded = [round(v, 3) for v in data]
        
        # [ [indices], [values] ]
        sparse_vectors.append([indices, data_rounded])

    # 語彙辞書
    vocabulary = {k: int(v) for k, v in vectorizer.vocabulary_.items()}

    # ==========================================
    # 保存 1: ベクトルデータ (検索用)
    # ==========================================
    output_vector_data = {
        "v": vocabulary,
        "d": sparse_vectors,
        "i": course_ids
    }

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output_vector_data, f, ensure_ascii=False, separators=(',', ':'))

    print(f"完了！ '{output_file}' (ベクトルデータ) を保存しました。")


    # ==========================================
    # 保存 2: メタデータ (表示用)
    # ==========================================
    with open(metadata_file, "w", encoding="utf-8") as f:
        json.dump(metadata_map, f, ensure_ascii=False, separators=(',', ':'))

    print(f"完了！ '{metadata_file}' (メタデータ) を保存しました。")


    # ==========================================
    # 保存 3: 類似授業 (おすすめ用)
    # ==========================================
    print("類似度を計算中...")
    sim_matrix = cosine_similarity(X, X)

    recommendations = {}
    top_k = 5

    for i in range(len(course_ids)):
        # 自分自身の類似度は1.0なので除外するためにコピーをとるか、indexを除外する
        scores = sim_matrix[i]
        # 自分自身を -1 に設定して選ばれないようにする
        scores[i] = -1
        
        # 降順ソートして上位K個のインデックスを取得
        # argsortは昇順なので、[::-1]で反転
        top_indices = scores.argsort()[::-1][:top_k]
        
        # スコアが0より大きいものだけ選ぶ (全く関係ないものはおすすめしない)
        filtered_indices = [idx for idx in top_indices if scores[idx] > 0]
        
        # IDのリストに変換
        recommended_ids = [course_ids[idx] for idx in filtered_indices]
        
        recommendations[course_ids[i]] = recommended_ids

    with open(recommendation_file, "w", encoding="utf-8") as f:
        json.dump(recommendations, f, ensure_ascii=False, separators=(',', ':'))

    print(f"完了！ '{recommendation_file}' (おすすめデータ) を保存しました。")

    print(f"処理対象: {len(course_ids)} 件")
    print(f"語彙数: {len(vocabulary)}")

if __name__ == "__main__":
    main()
