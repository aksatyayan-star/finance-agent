import unittest
from unittest.mock import patch, mock_open, MagicMock
from src.finance_buddy.rag_pipeline import text_processor, vertex_ai_manager
from src.finance_buddy.knowledge_base import retriever

class TestRagSystem(unittest.TestCase):

    def test_chunk_article(self):
        article = {
            "url": "http://example.com",
            "title": "Test Title",
            "content": "This is a test content that is long enough to be chunked." * 100
        }
        chunks = text_processor.chunk_article(article, chunk_size=100, chunk_overlap=10)
        self.assertGreater(len(chunks), 1)
        self.assertIn("This is a test content", chunks[0]['text_chunk'])

    @patch('src.finance_buddy.rag_pipeline.vertex_ai_manager.aiplatform')
    @patch('src.finance_buddy.rag_pipeline.vertex_ai_manager.TextEmbeddingModel')
    def test_get_text_embeddings(self, MockModel, mock_aiplatform):
        # Mock the model and its return value
        mock_embedding = MagicMock()
        mock_embedding.values = [0.1, 0.2, 0.3]
        mock_model_instance = MockModel.from_pretrained.return_value
        mock_model_instance.get_embeddings.return_value = [mock_embedding]

        embeddings = vertex_ai_manager.get_text_embeddings(["test text"])

        self.assertEqual(len(embeddings), 1)
        self.assertEqual(embeddings[0], [0.1, 0.2, 0.3])
        mock_aiplatform.init.assert_called_once()
        MockModel.from_pretrained.assert_called_once()

    @patch('src.finance_buddy.knowledge_base.retriever.vertex_ai_manager')
    @patch('builtins.open', new_callable=mock_open, read_data='{"chunk1": {"text_chunk": "test content"}}')
    def test_answer_conceptual_question(self, mock_file, mock_vertex_manager):
        # Mock the vertex AI manager functions
        mock_vertex_manager.get_text_embeddings.return_value = [[0.1, 0.2]]

        mock_neighbor = MagicMock()
        mock_neighbor.id = 'chunk1'
        mock_neighbor.distance = 0.9
        mock_vertex_manager.find_nearest_neighbors.return_value = [mock_neighbor]

        context = retriever.answer_conceptual_question("What is a test?")

        self.assertEqual(len(context), 1)
        self.assertEqual(context[0]['text'], "test content")
        mock_vertex_manager.get_text_embeddings.assert_called_once_with(["What is a test?"])
        mock_vertex_manager.find_nearest_neighbors.assert_called_once()

if __name__ == '__main__':
    unittest.main()
