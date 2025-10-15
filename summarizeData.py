import json
import os

def summarize_data(file_path):
    if not os.path.exists(file_path):
        print(f" File not found: {file_path}")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    print("\n === SITE SUMMARY REPORT ===\n")

    for site_name, content in data.items():
        scraped = content.get("scraped_data", {})
        clicks = content.get("click_results", [])

        images = scraped.get("images", [])
        clickables = scraped.get("clickables", [])
        text = scraped.get("text", "")

        
        total_images = len(images)
        total_clickables = len(clickables)
        text_length = len(text)
        word_count = len(text.split())

        
        success = sum(1 for c in clicks if c.get("status") == "success")
        failed = sum(1 for c in clicks if c.get("status") == "fail")

       
        selectors = {c.get("selector") for c in clicks if c.get("selector")}
        unique_selectors = len(selectors)

        
        print(f"=== {site_name.upper()} SITE ===")
        print(f"Total images:         {total_images}")
        print(f"Total clickables:     {total_clickables}")
        print(f"Unique selectors:     {unique_selectors}")
        print(f"Successful clicks:    {success}")
        print(f"Failed clicks:        {failed}")
        print(f"Text length:          {text_length:,} characters")
        print(f"Word count:           {word_count:,} words")
        print("-" * 40)

    print("\n Summary complete!\n")



summarize_data("cleaned_site_comparison.json")
