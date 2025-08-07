import json
import uuid
from . import scraper, text_processor, vertex_ai_manager

def update_knowledge_base(event, context):
    """
    Cloud Function entry point to update the knowledge base.
    1. Scrapes data from Zerodha Varsity.
    2. Chunks the articles.
    3. Generates embeddings for the chunks.
    4. Upserts the embeddings into the Vector Search index.
    """
    print("Starting knowledge base update...")

    # 1. Scrape data
    scraped_articles = scraper.main(write_to_file=False)
    if not scraped_articles:
        print("Scraping failed or returned no articles. Exiting.")
        return


    # 2. Process and chunk the text
    print("Processing and chunking articles...")
    all_chunks = text_processor.process_scraped_data(scraped_articles)
    if not all_chunks:
        print("No text chunks were generated. Exiting.")
        return

    # 3. Generate embeddings
    texts_to_embed = [chunk['text_chunk'] for chunk in all_chunks]
    embeddings = vertex_ai_manager.get_text_embeddings(texts_to_embed)
    if not embeddings:
        print("Failed to generate embeddings. Exiting.")
        return

    # 4. Prepare data for upsert and for the chunks database
    chunks_db = {}
    embeddings_for_upsert = []
    print(f"Preparing {len(all_chunks)} chunks and embeddings for upsert...")
    for chunk, embedding in zip(all_chunks, embeddings):
        chunk_id = str(uuid.uuid4())

        # Add the ID to the chunk data itself before storing
        chunk_with_id = chunk.copy()
        chunk_with_id['id'] = chunk_id
        chunks_db[chunk_id] = chunk_with_id

        embeddings_for_upsert.append({
            "id": chunk_id,
            "embedding": embedding
        })

    # Save the chunks database for later retrieval
    db_path = 'data/text_chunks.json'
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    with open(db_path, 'w', encoding='utf-8') as f:
        json.dump(chunks_db, f, ensure_ascii=False, indent=4)
    print(f"Saved {len(chunks_db)} chunks to {db_path}")

    # 5. Upsert to Vector Search
    print("Upserting embeddings to Vector Search...")
    vertex_ai_manager.upsert_datapoints(embeddings_for_upsert)

    print("Knowledge base update complete.")

# Example of how to run it locally (for testing)
if __name__ == '__main__':
    # This is for local testing and won't be called in the Cloud Function environment
    update_knowledge_base(None, None)
