
import json

input_file = "syllabus_vectors.json"
try:
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    skills = data.get("skills", [])
    ids = data.get("i", [])
    
    print(f"Total entries: {len(skills)}")
    
    # Check for new tags
    new_tags_count = {
        "lang_japanese": 0,
        "lang_english": 0,
        "type_specialized": 0,
        "tag_experiment": 0,
        "kw_": 0
    }
    
    sample_printed = 0
    for i, skill_list in enumerate(skills):
        for s in skill_list:
            if s in new_tags_count:
                new_tags_count[s] += 1
            if s.startswith("kw_"):
                new_tags_count["kw_"] += 1
                
        if sample_printed < 5 and len(skill_list) > 0:
            print(f"ID: {ids[i]} | Skills: {skill_list}")
            sample_printed += 1
            
    print("\nTag Counts:")
    for k, v in new_tags_count.items():
        print(f"{k}: {v}")

except Exception as e:
    print(e)
