
import json
import os

files = [
    "integrated_arts_courses.json",
    "subject_details_main_2025-04-03.json",
    "subject_data_main_2024-04-05.json"
]

results = {}

for fpath in files:
    if not os.path.exists(fpath):
        results[fpath] = "Not Found"
        continue
    
    with open(fpath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    count = len(data)
    keys = set()
    has_bunaya = False
    has_ryoiki = False
    keyword_hit = 0
    
    if isinstance(data, dict):
        sample = data[list(data.keys())[0]]
        keys = set(sample.keys())
        # Check text checks
        for k, v in data.items():
            str_v = str(v)
            if "キーワード" in str_v:
                keyword_hit += 1
    elif isinstance(data, list):
        if len(data) > 0:
            keys = set(data[0].keys())
        for item in data:
            str_v = str(item)
            if "キーワード" in str_v:
                keyword_hit += 1

    has_bunaya = '分野' in keys
    has_ryoiki = '領域' in keys

    results[fpath] = {
        "count": count,
        "keys": sorted(list(keys)),
        "has_bunaya": has_bunaya,
        "has_ryoiki": has_ryoiki,
        "keyword_string_hits": keyword_hit
    }

print(json.dumps(results, indent=2, ensure_ascii=False))
