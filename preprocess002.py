"""
preprocess002.py
================
preprocess001.py の機能に加え、正規表現による「前提知識（スキルタグ）」の自動抽出を行うスクリプトです。
抽出されたスキルは `syllabus_vectors.json` の "skills" キーに出力されます。

主な機能:
1. JSONデータのロード
2. テキストの正規化
3. Janomeによる形態素解析とTF-IDFベクトル化
4. **[NEW] 正規表現によるスキルタグ抽出 (Grade/Welcome ルール適用)**
5. ベクトルデータとメタデータの保存
"""
# ==========================================
# Script Name: preprocess002.py
# Description:
#   [EN] Syllabus text analysis and vectorization script. Extracts skills, filters by grade, and generates sparse vectors.
#   [JP] シラバスのテキスト分析およびベクトル化スクリプト。スキルの抽出、学年によるフィルタリング、疎ベクトルの生成を行います。
#
# Data Flow:
#   Input  : reduced_integrated_arts_courses.json (or integrated_arts_courses.json)
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
input_file = "integrated_arts_courses.json"
# input_file = "subject_details_main_2025-04-03.json"

output_file = "syllabus_vectors.json"
metadata_file = "course_metadata.json"
recommendation_file = "recommendations.json"

# ==========================================
# スキル抽出用 定義
# ==========================================
SKILL_PATTERNS = {
    "math_basic": r'(数学I|数学A|数I|数A|基礎計算|四則演算)',
    "math_adv": r'(数学II|数学B|数II|数B|数学III|数III|微分|積分|線形代数|解析学)',
    "stats": r'(統計|確率|検定|データ分析|回帰分析|SPSS|R言語)',
    "programming": r'(プログラミング|Python|C言語|Java|アルゴリズム|実装)',
    "reading": r'(英語|English|論文購読|原書|TOEIC)',
    "report": r'(レポート|小論文|アカデミックライティング)'
}

# Advanced topics to filter out for 1st graders
ADVANCED_SKILLS = ["math_adv", "stats", "programming"]

# Patterns that indicate "No prerequisites" / "Welcome all"
WELCOME_PATTERN = r'(文系|初心者|初学者|学部・学科|全学部|誰でも|意欲).*?(歓迎|問わない|対象|受講可能)'

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
    if not text:
        return ""
    normalized = unicodedata.normalize('NFKC', text)
    return normalized.strip()

def clean_course_name(name):
    if not name:
        return ""
    cleaned = re.sub(r'\[.*?\]', '', name)
    return cleaned.strip()

def get_words(text):
    text = normalize_text(text)
    tokens = t.tokenize(text)
    words = []
    for token in tokens:
        if token.part_of_speech.split(',')[0] in ['名詞']:
            words.append(token.base_form)
    return " ".join(words)

# ==========================================
# Patterns for Class Name Tags
# ==========================================
CLASS_NAME_TAGS = {
    "tag_experiment": r'(実験)',
    "tag_practice": r'(実習|演習)',
    "tag_seminar": r'(ゼミ|輪講|卒業研究)',
    "tag_intro": r'(概論|入門|基礎)',
    "tag_advanced": r'(特論|応用)',
}

def extract_skills(text, grade_year, info_dict):
    """
    テキスト、メタデータ、クラス名からタグ/スキルを抽出する
    """
    detected_skills = set()
    
    # --- 1. Existing Logic (Skills from Text) ---
    # Check for Welcome Pattern (If found, we add a beginner tag instead of clearing all)
    if re.search(WELCOME_PATTERN, text):
        detected_skills.add("beginner_friendly")
    
    # Extract Skills by Regex (Existing)
    for skill_key, pattern in SKILL_PATTERNS.items():
        if re.search(pattern, text):
            detected_skills.add(skill_key)
            
    # Grade Filter for Advanced Skills (Existing Logic)
    if grade_year == 1:
        for adv in ADVANCED_SKILLS:
            if adv in detected_skills:
                detected_skills.remove(adv)

    # --- 2. New Logic: Class Name Tags ---
    course_name = str(info_dict.get("授業科目名", ""))
    for tag_key, pattern in CLASS_NAME_TAGS.items():
        if re.search(pattern, course_name):
            detected_skills.add(tag_key)

    # --- 3. New Logic: Keyword Section Extraction ---
    # Try to find "【キーワード】" blocks in the text
    # Matches: 【キーワード】 term1, term2, term3 ... until Newline
    keyword_match = re.search(r'(【キーワード】|Keywords:|キーワード：)(.*?)\n', text)
    if keyword_match:
        # Extract the content part
        keywords_str = keyword_match.group(2).strip()
        # Split by common delimiters (comma, space, nakaguro)
        # Note: This might be noisy, so we'll just add the raw terms if they are short enough
        candidates = re.split(r'[,、\s]+', keywords_str)
        for c in candidates:
            c = c.strip()
            if len(c) > 1 and len(c) < 20: # Simple length filter
                detected_skills.add(f"kw_{c}")

    # --- 4. New Logic: Metadata Tags (Language, Type) ---
    lang_val = str(info_dict.get("使用言語", ""))
    if "日本" in lang_val or "J" in lang_val:
        detected_skills.add("lang_japanese")
    if "英" in lang_val or "E" in lang_val:
        detected_skills.add("lang_english")
        
    type_val = str(info_dict.get("科目区分", ""))
    if "専門" in type_val:
        detected_skills.add("type_specialized")
    elif "教養" in type_val or "基盤" in type_val:
        detected_skills.add("type_general")

    return list(detected_skills)

def get_grade(term_str):
    """
    開設期文字列から年次を抽出。見つからない場合はデフォルトで1とする。
    例: "2年次生 前期" -> 2
    """
    if not term_str:
        return 1
    match = re.search(r'(\d+)年次', term_str)
    if match:
        return int(match.group(1))
    return 1

# ==========================================
# メイン処理
# ==========================================
def main():
    print("形態素解析とスキル抽出を実行中...")
    corpus = []
    course_ids = []
    all_skills_data = [] # List of lists

    metadata_map = {}

    for code_key, info in syllabus_data.items():
        if not isinstance(info, dict): continue

        # --- Data Prep ---
        raw_name = str(info.get("授業科目名", ""))
        norm_name = normalize_text(raw_name)
        clean_name = clean_course_name(norm_name)
        
        # Combined Text for NLP & Skill Extraction
        target_text = (
            clean_name + " " +
            str(info.get("授業の目標・概要等", "")) + " " +
            str(info.get("メッセージ", "")) + " " +
            str(info.get("履修上の注意 受講条件等", ""))
        )
        
        # --- 1. TF-IDF Prep ---
        words = get_words(target_text)
        corpus.append(words)
        course_ids.append(code_key)

        # --- 2. Skill Extraction ---
        grade = get_grade(str(info.get("開設期", "")))
        skills = extract_skills(target_text, grade, info)
        all_skills_data.append(skills)

        # --- 3. Metadata Prep ---
        metadata_map[code_key] = {
            "n": clean_name,
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
    vectorizer = TfidfVectorizer(max_features=500)
    X = vectorizer.fit_transform(corpus)

    print("データを圧縮中...")
    sparse_vectors = []
    for i in range(X.shape[0]):
        row = X.getrow(i)
        indices = row.indices.tolist()
        data = row.data.tolist()
        data_rounded = [round(v, 3) for v in data]
        sparse_vectors.append([indices, data_rounded])

    vocabulary = {k: int(v) for k, v in vectorizer.vocabulary_.items()}

    # ==========================================
    # 保存 1: ベクトルデータ (検索用) + Skills
    # ==========================================
    output_vector_data = {
        "v": vocabulary,
        "d": sparse_vectors,
        "i": course_ids,
        "skills": all_skills_data  # <--- Added
    }

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output_vector_data, f, ensure_ascii=False, separators=(',', ':'))

    print(f"完了！ '{output_file}' (ベクトルデータ+スキル) を保存しました。")

    # ==========================================
    # 保存 2: メタデータ (表示用)
    # ==========================================
    with open(metadata_file, "w", encoding="utf-8") as f:
        json.dump(metadata_map, f, ensure_ascii=False, separators=(',', ':'))
    print(f"完了！ '{metadata_file}' を保存しました。")

    # ==========================================
    # 保存 3: 類似授業
    # ==========================================
    print("類似度を計算中...")
    sim_matrix = cosine_similarity(X, X)
    recommendations = {}
    top_k = 5

    for i in range(len(course_ids)):
        scores = sim_matrix[i]
        scores[i] = -1
        top_indices = scores.argsort()[::-1][:top_k]
        # スコアが0より大きいものだけ選ぶ (全く関係ないものはおすすめしない)
        filtered_indices = [idx for idx in top_indices if scores[idx] > 0]
        
        # IDとスコア(パーセンテージ用に保持)のリストに変換
        # [ [id, score], [id, score], ... ]
        recommended_data = [[course_ids[idx], round(scores[idx], 3)] for idx in filtered_indices]
        
        recommendations[course_ids[i]] = recommended_data

    with open(recommendation_file, "w", encoding="utf-8") as f:
        json.dump(recommendations, f, ensure_ascii=False, separators=(',', ':'))
    print(f"完了！ '{recommendation_file}' を保存しました。")

if __name__ == "__main__":
    main()
