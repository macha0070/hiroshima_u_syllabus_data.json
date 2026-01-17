
import json
from collections import Counter

input_file = "subject_details_main_2025-04-03.json"
try:
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    languages = []
    classifications = []
    
    for k, v in data.items():
        if "使用言語" in v:
            languages.append(v["使用言語"])
        if "科目区分" in v:
            classifications.append(v["科目区分"])

    print("Top 10 Languages:", Counter(languages).most_common(10))
    print("Top 10 Classifications:", Counter(classifications).most_common(10))

except Exception as e:
    print(e)
