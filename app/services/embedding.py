from app.providers.embedding_provider import EmbeddingProvider


class EmbeddingService:
    """
    Service responsible for generating embeddings using
    the configured embedding provider.
    """

    def __init__(
        self,
        embedding_provider: EmbeddingProvider,
    ):
        self.embedding_provider = embedding_provider

    def generate_embedding(
        self,
        text: str,
    ) -> list[float]:
        """
        Generate an embedding for a single text.
        """

        return self.embedding_provider.encode([text])[0]

    def generate_embeddings(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        """
        Generate embeddings for multiple texts.
        """

        if not texts:
            return []

        return self.embedding_provider.encode(texts)