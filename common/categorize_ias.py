"""
categorize_ias.py
=================
「総合科学部」の授業データを読み込み、授業名や概要に含まれるキーワードに基づいて
以下の5つの領域に自動分類するスクリプトです。

カテゴリ:
1. 総合科学部共通科目
2. 自然探求領域
3. 人間探究領域
4. 社会探究領域
5. その他

※キーワードリストは必要に応じて編集してください。
"""
import json
import os

INPUT_FILE = "integrated_arts_courses.json"
OUTPUT_FILE = "integrated_arts_courses.json" # 上書き保存

# キーワード設定 (優先順位順に評価されます)
KEYWORDS = {
    "自然探求領域": [
        "数学", "物理", "化学", "生物", "地球", "宇宙", "環境", "自然", 
        "情報", "データ", "計算機", "プログラミング", "アルゴリズム", "AI", 
        "エネルギー", "物質", "生態", "生命", "数理"
    ],
    "人間探究領域": [
        "哲学", "倫理", "歴史", "文学", "芸術", "言語", "心理", "認知", 
        "思想", "文化", "宗教", "人間", "心", "行動", "日本語", "英語"
    ],
    "社会探究領域": [
        "社会", "経済", "法", "政治", "教育", "メディア", "ジェンダー", 
        "平和", "国際", "経営", "行政", "地域", "福祉", "コミュニケーション"
    ],
    "総合科学部共通科目": [
        "入門", "概論", "基礎", "演習", "リテラシー", "セミナー", 
        "キャリア", "インターンシップ"
    ]
}

def determine_category(text):
    """テキストからカテゴリを判定する"""
    for category, keywords in KEYWORDS.items():
        for kw in keywords:
            if kw in text:
                return category
    return "その他"

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"Error: {INPUT_FILE} が見つかりません。まず extract_integrated_arts.py を実行してください。")
        return

    print(f"Loading {INPUT_FILE}...")
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    updated_count = 0
    
    print("Categorizing courses...")
    for course_id, info in data.items():
        # 判定対象のテキスト（授業名 + 概要）
        target_text = str(info.get("授業科目名", "")) + " " + str(info.get("授業の目標・概要等", ""))
        
        # 既存のカテゴリがあればスキップするか、上書きするか（ここでは上書き）
        category = determine_category(target_text)
        
        # 結果を保存
        info["領域"] = category
        updated_count += 1
        # print(f"{info.get('授業科目名')} -> {category}")

    print(f"Categorized {updated_count} courses.")

    print(f"Saving to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print("Done! Check 'integrated_arts_courses.json' for the '領域' field.")

if __name__ == "__main__":
    main()
