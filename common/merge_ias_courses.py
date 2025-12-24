"""
merge_ias_courses.py
====================
`subject_details_main_2025-04-03.json` から、「総合科学部」で始まる全ての部局の授業
（専門教育科目を含む）を抽出し、既存の `integrated_arts_courses.json` にマージするスクリプトです。

主な機能:
1. 全データの読み込み
2. 現在のIASリストの読み込み
3. "総合科学部..." で始まる部局のデータを検索
4. 新しい授業があればリストに追加して保存
"""
import json
import os

SOURCE_FILE = "subject_details_main_2025-04-03.json"
TARGET_FILE = "integrated_arts_courses.json"

def main():
    if not os.path.exists(SOURCE_FILE):
        print(f"Error: {SOURCE_FILE} が見つかりません。")
        return
    
    # Load Source
    print(f"Loading {SOURCE_FILE}...")
    with open(SOURCE_FILE, 'r', encoding='utf-8') as f:
        source_data = json.load(f)

    # Load Target (if exists, else empty dict)
    if os.path.exists(TARGET_FILE):
        print(f"Loading {TARGET_FILE}...")
        with open(TARGET_FILE, 'r', encoding='utf-8') as f:
            target_data = json.load(f)
    else:
        print(f"Creating new {TARGET_FILE}...")
        target_data = {}

    initial_count = len(target_data)
    added_count = 0

    print("Merging courses...")
    for course_id, info in source_data.items():
        dept = info.get("開講部局", "")
        # Check if department starts with "総合科学部" (covers 総合科学部, 総合科学部総合科学科, 総合科学部国際共創学科)
        if dept.startswith("総合科学部"):
            if course_id not in target_data:
                target_data[course_id] = info
                added_count += 1
                # Optional: Initialize category fields if missing
                if "領域" not in target_data[course_id]:
                    target_data[course_id]["領域"] = "その他" # Default until categorized
                if "分野" not in target_data[course_id]:
                    target_data[course_id]["分野"] = ""

    print(f"Added {added_count} new courses.")
    print(f"Total courses: {len(target_data)}")

    if added_count > 0:
        print(f"Saving to {TARGET_FILE}...")
        with open(TARGET_FILE, 'w', encoding='utf-8') as f:
            json.dump(target_data, f, ensure_ascii=False, indent=2)
        print("Done!")
    else:
        print("No new courses found to add.")

if __name__ == "__main__":
    main()
