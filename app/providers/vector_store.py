# /home/sandeep/Projects/document-rag-backend/app/providers/vector_store.py
from uuid import uuid4

from qdrant_client import QdrantClient
from qdrant_client.http.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchValue,
    PointStruct,
    VectorParams,
)


class VectorStore:
    """
    Wrapper around Qdrant operations.

    Responsible for:
    - Creating collections
    - Storing vectors
    - Searching vectors
    - Deleting vectors
    """

    def __init__(
        self,
        host: str,
        port: int,
        collection_name: str,
        vector_size: int,
    ) -> None:
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
        """
        Create the collection if it doesn't already exist.
        """

        collections = self.client.get_collections().collections
        existing = [collection.name for collection in collections]

        if self.collection_name not in existing:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=vector_size,
                    distance=Distance.COSINE,
                ),
            )

    def upsert(
        self,
        embeddings: list[list[float]],
        payloads: list[dict],
    ) -> list[str]:
        """
        Store embeddings and metadata in Qdrant.

        Returns:
            List of generated vector IDs.
        """

        vector_ids: list[str] = []
        points: list[PointStruct] = []

        for embedding, payload in zip(embeddings, payloads):
            vector_id = str(uuid4())

            vector_ids.append(vector_id)

            points.append(
                PointStruct(
                    id=vector_id,
                    vector=embedding,
                    payload=payload,
                )
            )

        self.client.upsert(
            collection_name=self.collection_name,
            points=points,
        )

        return vector_ids

    def search(
        self,
        query_vector: list[float],
        limit: int = 5,
    ):
        """
        Search for the most similar vectors.
        """

        results = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            limit=limit,
            with_payload=True,
        )

        return results.points

    def delete_document(
        self,
        document_id: int,
    ) -> None:
        """
        Delete all vectors belonging to a document.
        """

        self.client.delete(
            collection_name=self.collection_name,
            points_selector=Filter(
                must=[
                    FieldCondition(
                        key="document_id",
                        match=MatchValue(value=document_id),
                    )
                ]
            ),
        )

    def collection_info(self):
        """
        Return collection information.
        """

        return self.client.get_collection(
            self.collection_name
        )
