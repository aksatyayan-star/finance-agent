from typing import List, Dict, Any
from src.finance_buddy.rag_pipeline import vertex_ai_manager
import json
import os

# This file path should be consistent with the one in rag_pipeline/main.py
# A better approach in a larger system would be to get this path from a shared config.
CHUNKS_DB_FILE = 'data/text_chunks.json'

def _load_chunks_db() -> Dict[str, Dict[str, Any]]:
    """Loads the chunks database from the JSON file."""
    try:
        with open(CHUNKS_DB_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Chunks database not found at {CHUNKS_DB_FILE}. Please run the RAG pipeline first.")
        return {}
    except json.JSONDecodeError:
        print(f"Error decoding JSON from {CHUNKS_DB_FILE}.")
        return {}

def answer_conceptual_question(query: str) -> List[Dict[str, Any]]:
    """
    Answers a conceptual question using the RAG pipeline.
    1. Gets an embedding for the user's query.
    2. Finds the most similar document chunks from the Vector Search index.
    3. Retrieves the full text of those chunks.
    4. Returns the retrieved chunks as context.
    """
    print(f"Answering conceptual question: '{query}'")

    # 1. Get embedding for the query
    query_embedding = vertex_ai_manager.get_text_embeddings([query])
    if not query_embedding:
        print("Could not generate an embedding for the query.")
        return []

    # 2. Find nearest neighbors in Vector Search
    neighbors = vertex_ai_manager.find_nearest_neighbors(query_embedding[0])
    if not neighbors:
        print("Could not find any neighbors in the vector index.")
        return []

    # 3. Retrieve the original text chunks using their IDs
    chunks_db = _load_chunks_db()
    if not chunks_db:
        return []

    retrieved_chunks = []
    print(f"Found {len(neighbors)} neighbors. Retrieving text chunks...")
    for neighbor in neighbors:
        chunk_id = neighbor.id
        chunk_data = chunks_db.get(chunk_id)
        if chunk_data:
            retrieved_chunks.append({
                "source": chunk_data.get('source_url'),
                "title": chunk_data.get('title'),
                "text": chunk_data.get('text_chunk'),
                "distance": neighbor.distance
            })

    return retrieved_chunks
