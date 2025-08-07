from typing import List, Dict, Any

def clean_text(text: str) -> str:
    """
    A simple text cleaner. Can be expanded later.
    """
    # Replace multiple newlines/spaces with a single space
    return " ".join(text.split())

def chunk_article(article: Dict[str, Any], chunk_size: int = 1000, chunk_overlap: int = 100) -> List[Dict[str, Any]]:
    """
    Chunks a single article into smaller text segments.
    Each chunk retains metadata from the original article.
    """
    content = clean_text(article.get('content', ''))
    if not content or content == "This page does not contain a main article body (it may be a video).":
        return []

    chunks = []
    start = 0
    while start < len(content):
        end = start + chunk_size
        chunk_text = content[start:end]

        chunk_metadata = {
            "source_url": article.get('url'),
            "title": article.get('title'),
            "text_chunk": chunk_text
        }
        chunks.append(chunk_metadata)

        start += chunk_size - chunk_overlap

    return chunks

def process_scraped_data(scraped_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Processes a list of scraped articles into a list of all text chunks.
    """
    all_chunks = []
    for article in scraped_data:
        chunks = chunk_article(article)
        all_chunks.extend(chunks)
    return all_chunks
