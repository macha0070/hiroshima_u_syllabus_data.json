# ==========================================
# Script Name: verify_skills.py
# Description:
#   [EN] Verification script for skill extraction.
#        Checks the existence and content of the 'skills' field in syllabus_vectors.json.
#   [JP] スキル抽出機能の検証用スクリプト。
#        syllabus_vectors.json内の'skills'フィールドの存在と内容を確認します。
#
# Data Flow:
#   Input  : syllabus_vectors.json
#   Output : (Console Output / コンソール出力)
# ==========================================

import json

# Load the generated vectors file
try:
    with open("syllabus_vectors.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        
    print("Keys found:", list(data.keys()))
    
    if "skills" not in data:
        print("ERROR: 'skills' key missing!")
        exit(1)
        
    ids = data["i"]
    skills = data["skills"]
    
    print(f"Total IDs: {len(ids)}")
    print(f"Total Skills Lists: {len(skills)}")
    
    if len(ids) != len(skills):
        print("ERROR: Mismatch in length between IDs and Skills!")
    else:
        print("SUCCESS: Lengths match.")
        
    # Print sample
    print("\n--- Sample Entries ---")
    for i in range(min(10, len(ids))):
        course_id = ids[i]
        course_skills = skills[i]
        print(f"ID: {course_id}, Skills: {course_skills}")

    # Check for specific expected behavior (filtering)
    # Count empty skill lists (should be high due to 'Welcome' filter or lack of keywords)
    empty_count = sum(1 for s in skills if not s)
    print(f"\nEmpty skill lists: {empty_count} / {len(skills)}")

except Exception as e:
    print(f"An error occurred: {e}")
