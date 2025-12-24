
import json

input_file = "subject_details_main_2025-04-03.json"
try:
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"Total items: {len(data)}")
    if len(data) > 0:
        first_key = list(data.keys())[0]
        sample = data[first_key]
        print("Sample Keys:", list(sample.keys()))
        print("Sample Content:")
        for k, v in sample.items():
            print(f"{k}: {str(v)[:100]}...") # Print first 100 chars
except Exception as e:
    print(e)
