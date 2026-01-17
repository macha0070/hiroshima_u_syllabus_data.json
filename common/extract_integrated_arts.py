"""
extract_integrated_arts.py
==========================
総合科学部の授業だけを抽出して新しいJSONファイルに保存するスクリプトです。

主な機能:
1. `subject_details_main_2025-04-03.json` をロード
2. "開講部局" が "総合科学部" のデータをフィルタリング
3. `integrated_arts_courses.json` に保存
"""
import json
import os

INPUT_FILE = "subject_details_main_2025-04-03.json"
OUTPUT_FILE = "integrated_arts_courses.json"

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"Error: {INPUT_FILE} が見つかりません。")
        return

    print(f"Loading {INPUT_FILE}...")
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    extracted = {}
    count = 0

    print("Filtering courses for '総合科学部'...")
    for course_id, info in data.items():
        if info.get("開講部局") == "総合科学部":
            extracted[course_id] = info
            count += 1

    print(f"Found {count} courses.")

    print(f"Saving to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(extracted, f, ensure_ascii=False, indent=2)
    
    print("Done!")

if __name__ == "__main__":
    main()
