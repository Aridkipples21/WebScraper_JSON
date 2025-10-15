import json
import os

# Define what you consider "blacklisted" data
blacklisted_reasons = {"already_visited", "blacklisted/external"}
blacklisted_statuses = {"skipped"}

def clean_data(file_path):
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    # 1. Load the JSON file
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    cleaned_data = {}

   
    for section, content in data.items():
        click_results = content.get("click_results", [])

        seen_selectors = set()
        new_click_results = []

        
        for entry in click_results:
            status = entry.get("status", "")
            reason = entry.get("reason", "")
            selector = entry.get("selector", "")

            
            if status in blacklisted_statuses or reason in blacklisted_reasons:
                continue

            
            if selector in seen_selectors:
                continue

            seen_selectors.add(selector)
            new_click_results.append(entry)

        
        content["click_results"] = new_click_results
        cleaned_data[section] = content

    
    output_path = "cleaned_site_comparison.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(cleaned_data, f, indent=4, ensure_ascii=False)

    print(f" Cleaned data saved to: {output_path}")



clean_data("site_comparison.json")
