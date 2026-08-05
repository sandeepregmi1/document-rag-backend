from app.providers.embedding_provider import EmbeddingProvider
from app.providers.vector_store import VectorStore


class Retriever:
    """
    Retrieves the most relevant document chunks
    from the vector database.
    """

    def __init__(
        self,
        embedding_provider: EmbeddingProvider,
        vector_store: VectorStore,
    ) -> None:
        self.embedding_provider = embedding_provider
        self.vector_store = vector_store

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[dict]:
        """
        Retrieve the most relevant chunks for a query.

        Args:
            query: User question.
            top_k: Number of chunks to retrieve.

        Returns:
            List of retrieved chunks with metadata.
        """

        # Generate embedding for the query
        query_embedding = self.embedding_provider.encode(
            [query]
        )[0]

        # Search Qdrant
        results = self.vector_store.search(
            query_vector=query_embedding,
            limit=top_k,
        )

        retrieved_chunks = []

        for result in results:

            retrieved_chunks.append(
                {
                    "score": result.score,
                    "document_id": result.payload["document_id"],
                    "chunk_number": result.payload["chunk_number"],
                    "text": result.payload["text"],
                }
            )

        return retrieved_chunks