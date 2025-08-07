from typing import List, Dict, Any
from google.cloud import aiplatform
from vertexai.language_models import TextEmbeddingModel
from src.finance_buddy import config

# Initialize the Vertex AI SDK
try:
    aiplatform.init(project=config.GCP_PROJECT_ID, location=config.GCP_REGION)
except Exception as e:
    print(f"Could not initialize Vertex AI SDK. Please check your GCP configuration. Error: {e}")

def get_text_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Gets text embeddings for a list of texts using Vertex AI.
    """
    try:
        aiplatform.init(project=config.GCP_PROJECT_ID, location=config.GCP_REGION)
        model = TextEmbeddingModel.from_pretrained(config.EMBEDDING_MODEL_NAME)

        # The API has a limit on the number of texts per call, so we batch them.
        batch_size = 250 # As per documentation, a safe batch size
        all_embeddings = []

        print(f"Generating embeddings for {len(texts)} text chunks in batches of {batch_size}...")
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i+batch_size]
            embeddings = model.get_embeddings(batch)
            all_embeddings.extend([list(e.values) for e in embeddings])
            print(f"  Processed batch {i//batch_size + 1}/{(len(texts)-1)//batch_size + 1}")

        return all_embeddings
    except Exception as e:
        print(f"An error occurred while generating embeddings: {e}")
        # This could be due to auth issues, invalid model name, etc.
        return []

def get_index_endpoint():
    """Initializes and returns the Vertex AI Vector Search index endpoint."""
    return aiplatform.MatchingEngineIndexEndpoint(
        index_endpoint_name=config.VECTOR_SEARCH_ENDPOINT_ID
    )

def upsert_datapoints(embeddings: List[Dict[str, Any]]):
    """
    Upserts a list of embeddings (each with an 'id' and 'embedding' key)
    into the Vector Search index.
    """
    try:
        index_endpoint = get_index_endpoint()
        # The API also has a limit on the number of vectors per upsert call.
        batch_size = 100
        print(f"Upserting {len(embeddings)} embeddings to the index...")
        for i in range(0, len(embeddings), batch_size):
            batch = embeddings[i:i+batch_size]
            index_endpoint.upsert_datapoints(datapoints=batch)
            print(f"  Upserted batch {i//batch_size + 1}/{(len(embeddings)-1)//batch_size + 1}")
        print("Upsert complete.")
    except Exception as e:
        print(f"An error occurred during upsert: {e}")

def find_nearest_neighbors(query_embedding: List[float], num_neighbors: int = 5) -> List[Any]:
    """
    Finds the nearest neighbors for a given query embedding.
    """
    try:
        index_endpoint = get_index_endpoint()

        results = index_endpoint.find_neighbors(
            queries=[query_embedding],
            num_neighbors=num_neighbors,
            deployed_index_id=config.VECTOR_SEARCH_DEPLOYED_INDEX_ID
        )
        # find_neighbors returns a list of lists of neighbors, one for each query
        if results:
            return results[0]
        return []
    except Exception as e:
        print(f"An error occurred during neighbor search: {e}")
        return []
