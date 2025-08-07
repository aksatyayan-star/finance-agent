import requests
from bs4 import BeautifulSoup
import json
import time
import os

# --- Configuration ---
MODULES_URL = "https://zerodha.com/varsity/modules/"
HEADERS = {
    'User-Agent': 'My Financial AI Scraper Bot/1.0 (for educational project; contact at youremail@example.com)'
}
REQUEST_DELAY_SECONDS = 2
OUTPUT_FILE = 'zerodha_varsity_content.json'
OUTPUT_DIR = 'scraped_data'

def get_all_chapter_urls():
    """
    Crawls the main Varsity 'modules' page to find links to all modules,
    then visits each module to find links to all its chapters, ignoring comment links.
    """
    print("Starting crawl from the modules page to find all module URLs...")
    try:
        response = requests.get(MODULES_URL, headers=HEADERS)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        module_links = []
        for link in soup.find_all('a', href=True):
            if '/module/' in link['href'] and link['href'].startswith('https://zerodha.com/varsity/module/'):
                module_links.append(link['href'])

        module_links = list(set(module_links))
        print(f"Found {len(module_links)} modules. Now finding chapters in each...")

        chapter_urls = []
        for module_url in module_links:
            time.sleep(REQUEST_DELAY_SECONDS)
            print(f"  Fetching chapters from: {module_url}")
            try:
                module_response = requests.get(module_url, headers=HEADERS)
                module_response.raise_for_status()
                module_soup = BeautifulSoup(module_response.content, 'html.parser')

                found_chapters_on_page = 0
                for chapter_link in module_soup.find_all('a', href=True):
                    href = chapter_link['href']
                    if '/chapter/' in href and '#comment' not in href:
                        chapter_urls.append(href)
                        found_chapters_on_page += 1

                print(f"    Found {found_chapters_on_page} unique chapters on this page.")

            except requests.exceptions.RequestException as e:
                print(f"    Could not fetch module {module_url}: {e}")

        unique_chapters = list(set(chapter_urls))
        print(f"Finished crawling. Found a total of {len(unique_chapters)} unique chapters.")
        return unique_chapters

    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch the main Varsity modules page: {e}")
        return []

def scrape_chapter_content(url):
    """
    Scrapes the title and content using a robust method that looks inside the main  tag.
    """
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        title = "No Title Found"
        content = "No content found."

        # Find the main article container first. This is a more stable anchor.
        article = soup.find('article')

        if article:
            # If we found the article, search for the title and content INSIDE it.
            title_tag = article.find('h1')
            if title_tag:
                title = title_tag.get_text(strip=True)

            content_div = article.find('div', class_='content-post')
            if content_div:
                content = content_div.get_text(separator=' ', strip=True)
            else:
                # Handle cases like video pages that have an article tag but no text content
                content = "This page does not contain a main article body (it may be a video)."
        else:
            # If no  tag is found at all, the page layout is completely different.
            print(f"    Note: Could not find the main  container for {url}.")


        return {"url": url, "title": title, "content": content}

    except requests.exceptions.RequestException as e:
        print(f"  Error scraping {url}: {e}")
        return None

def main(write_to_file=True):
    """
    Main function to orchestrate the crawling and scraping process.
    If write_to_file is True, it saves the data to a JSON file.
    Always returns the scraped data.
    """
    chapter_urls = get_all_chapter_urls()
    if not chapter_urls:
        print("No chapter URLs found. Exiting.")
        return []

    all_data = []
    total_chapters = len(chapter_urls)
    for i, url in enumerate(chapter_urls):
        print(f"Scraping chapter {i + 1}/{total_chapters}: {url}")
        data = scrape_chapter_content(url)
        if data:
            all_data.append(data)
        time.sleep(REQUEST_DELAY_SECONDS)

    if write_to_file:
        if not os.path.exists(OUTPUT_DIR):
            os.makedirs(OUTPUT_DIR)
        output_path = os.path.join(OUTPUT_DIR, OUTPUT_FILE)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(all_data, f, ensure_ascii=False, indent=4)
        print(f"\nScraping complete! All data saved to {output_path}")

    return all_data

if __name__ == "__main__":
    main(write_to_file=True)
