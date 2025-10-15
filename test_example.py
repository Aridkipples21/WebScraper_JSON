import json
from playwright.sync_api import sync_playwright




urls = {
    "staging": "https://vaaltata.r-e-d-staging.co.za/",
    "live": "https://www.vaaltata.co.za/"
}


blacklist = ["https://www.supergroupdealerships.co.za/", "https://www.facebook.com/EdenvaleNissan", "twitter.com", "instagram.com", "https://www.youtube.com/user/NissanSouthAfrica"]

visited_urls = set()
final_results = {}

def detect_source(url):
    """Detect whether the site is staging or live."""
    if "staging" in url or "r-e-d-staging" in url:
        return "staging"
    return "live"

def scrape_page(page, source):
    """Scrapes all text, images, and clickable elements from the page."""
    text_content = page.evaluate("() => document.body.innerText")

    images = page.evaluate("""
        () => Array.from(document.images, img => img.src)
    """)

    clickable_selectors = page.evaluate("""
        () => Array.from(document.querySelectorAll('button, a'), el => ({
            text: el.innerText.trim(),
            href: el.href || null,
            selector: el.tagName + (el.id ? '#' + el.id : '') + 
                      (el.className ? '.' + el.className.split(' ').join('.') : '')
        }))
    """)

    return {
        "source": source,
        "text": text_content,
        "images": images,
        "clickables": clickable_selectors
    }

def test_clickables(page, clickables, base_url, source):
    """Clicks through clickable elements safely."""
    results = []
    for el in clickables:
        href = el.get("href") or ""

        
        if any(bad in href for bad in blacklist) or (href and not href.startswith(base_url)):
            results.append({
                "selector": el["selector"],
                "status": "skipped",
                "reason": "blacklisted/external",
                "source": source
            })
            continue
        
        
        if href in visited_urls:
            results.append({
                "selector": el["selector"],
                "status": "skipped",
                "reason": "already_visited",
                "source": source
            })
            continue

        try:
            if href:
                visited_urls.add(href)
                page.goto(href, timeout=10000)
            else:
                page.locator(el["selector"]).click(timeout=3000)

            results.append({
                "selector": el["selector"],
                "status": "success",
                "source": source
            })
        except Exception as e:
            results.append({
                "selector": el["selector"],
                "status": "fail",
                "error": str(e),
                "source": source
            })
    
    return results


with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, slow_mo=50)

    for name, url in urls.items():
        if url in visited_urls:
            print(f"Skipping already visited: {url}")
            continue

        visited_urls.add(url)
        source = detect_source(url)

        context = browser.new_context()
        page = context.new_page()

        print(f"\nVisiting [{source.upper()}]: {url}")
        page.goto(url, timeout=20000)

        
        if any(bad in url for bad in blacklist):
            print(f"Skipping blacklisted: {url}")
            context.close()
            continue

        
        data = scrape_page(page, source)

        
        clicks = test_clickables(page, data["clickables"], base_url=url, source=source)

       
        final_results[name] = {
            "url": url,
            "source": source,
            "scraped_data": data,
            "click_results": clicks
        }

        context.close()

    browser.close()


with open("site_comparison.json", "w", encoding="utf-8") as f:
    json.dump(final_results, f, indent=4, ensure_ascii=False)

print("\n Done! Results saved to site_comparison.json")
