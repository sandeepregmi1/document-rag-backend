from sentence_transformers import SentenceTransformer


class EmbeddingProvider:
    """
    Wrapper around SentenceTransformer.
    Responsible only for loading the model
    and generating embeddings.
    """

    def __init__(self, model_name: str):
        self.model = SentenceTransformer(model_name)

    def encode(self, texts: list[str]) -> list[list[float]]:
        """
        Convert list of texts into embeddings.
        """
        embeddings = self.model.encode(
            texts,
            normalize_embeddings=True,
            convert_to_numpy=True,
        )

        return embeddings.tolist()