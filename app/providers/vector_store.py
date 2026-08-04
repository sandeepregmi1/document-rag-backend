from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance
from qdrant_client.http.models import VectorParams


class VectorStore:

    def __init__(
        self,
        host: str,
        port: int,
        collection_name: str,
        vector_size: int,
    ):
        self.collection_name = collection_name

        self.client = QdrantClient(
            host=host,
            port=port,
        )

        self._create_collection(vector_size)

    def _create_collection(
        self,
        vector_size: int,
    ) -> None:

        collections = self.client.get_collections().collections

        existing = [c.name for c in collections]

        if self.collection_name not in existing:

            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=vector_size,
                    distance=Distance.COSINE,
                ),
            )