
import json
import os

input_file = "subject_data_main_2024-04-05.json"

print(f"\n--- Inspecting {input_file} ---")
try:
    if not os.path.exists(input_file):
        print("File not found.")
    else:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"Total items: {len(data)}")
        if isinstance(data, list) and len(data) > 0:
            print("Keys (List item):", sorted(list(data[0].keys())))
        elif isinstance(data, dict) and len(data) > 0:
            first_key = list(data.keys())[0]
            print("Keys (Dict item):", sorted(list(data[first_key].keys())))
        else:
            print("Empty or unknown structure")
            
except Exception as e:
    print(f"Error: {e}")
