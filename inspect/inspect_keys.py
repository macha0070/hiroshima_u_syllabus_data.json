
import json

input_file = "subject_details_main_2025-04-03.json"
try:
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if len(data) > 0:
        first_key = list(data.keys())[0]
        sample = data[first_key]
        print("All Keys:", sorted(list(sample.keys())))
except Exception as e:
    print(e)
