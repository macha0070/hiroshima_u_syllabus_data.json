
import json
import os

files = [
    "integrated_arts_courses.json",
    "subject_data_main_2024-04-05.json"
]

for input_file in files:
    print(f"\n--- Inspecting {input_file} ---")
    try:
        if not os.path.exists(input_file):
            print("File not found.")
            continue
            
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"Total items: {len(data)}")
        if isinstance(data, dict) and len(data) > 0:
            first_key = list(data.keys())[0]
            sample = data[first_key]
            print("Keys:", sorted(list(sample.keys())))
        elif isinstance(data, list) and len(data) > 0:
            print("Keys (List item):", sorted(list(data[0].keys())))
        else:
            print("Empty or unknown structure")
            
    except Exception as e:
        print(f"Error: {e}")
