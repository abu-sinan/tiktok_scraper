# main.py
import asyncio
import json
import os
import csv
from playwright.async_api import async_playwright
from utils.email_extractor import extract_emails
from utils.college_detector import detect_college

# Load config
with open("config.json", "r") as f:
    CONFIG = json.load(f)

# Load keywords
with open("keywords.txt", "r") as f:
    KEYWORDS = [line.strip() for line in f if line.strip()]

OUTPUT_CSV = CONFIG["output_csv"]
MAX_PROFILES = CONFIG["max_profiles"]

async def scrape_tiktok_profiles():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=CONFIG["headless"])
        context = await browser.new_context()
        page = await context.new_page()

        scraped_profiles = []
        visited_profiles = set()

        for keyword in KEYWORDS:
            print(f"\n[+] Searching TikTok for: {keyword}")
            search_url = f"https://www.tiktok.com/search?q={keyword}"
            await page.goto(search_url, timeout=60000)
            await page.wait_for_timeout(5000)

            profile_links = await page.query_selector_all("a[href^='/@']")
            for profile in profile_links:
                if len(scraped_profiles) >= MAX_PROFILES:
                    break

                href = await profile.get_attribute("href")
                if href and href.startswith("/@") and href not in visited_profiles:
                    full_url = f"https://www.tiktok.com{href}"
                    visited_profiles.add(href)

                    print(f"  [-] Visiting: {full_url}")
                    try:
                        await page.goto(full_url, timeout=30000)
                        await page.wait_for_timeout(3000)

                        content = await page.content()
                        email = extract_emails(content)
                        college = detect_college(content)

                        if email:
                            scraped_profiles.append({
                                "profile_url": full_url,
                                "email": email,
                                "college": college
                            })
                            print(f"    [✓] Found email: {email}")
                        else:
                            print("    [x] No email found")

                    except Exception as e:
                        print(f"    [!] Error: {str(e)}")

            if len(scraped_profiles) >= MAX_PROFILES:
                break

        await browser.close()
        return scraped_profiles

def save_to_csv(data):
    os.makedirs("output", exist_ok=True)
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["profile_url", "email", "college"])
        writer.writeheader()
        for row in data:
            writer.writerow(row)

if __name__ == "__main__":
    scraped_data = asyncio.run(scrape_tiktok_profiles())
    save_to_csv(scraped_data)
    print(f"\n[✓] Done! Saved {len(scraped_data)} profiles to: {OUTPUT_CSV}")
