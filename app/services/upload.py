from pathlib import Path
from pydoc import text

from sqlalchemy.orm import Session

from app.db.crud import save_chunk_metadata
from app.db.crud import save_document
from app.db.models import ChunkMetadata
from app.db.models import Document
from app.providers.embedding_provider import EmbeddingProvider
from app.providers.vector_store import VectorStore
from app.services.chunker import TextChunker
from app.services.parser import DocumentParser


class UploadService:
    """
    Handles the complete document ingestion workflow.
    """

    def __init__(
        self,
        parser: DocumentParser,
        chunker: TextChunker,
        embedding_provider: EmbeddingProvider,
        vector_store: VectorStore,
    ) -> None:
        self.parser = parser
        self.chunker = chunker
        self.embedding_provider = embedding_provider
        self.vector_store = vector_store

    def ingest_document(
        self,
        file_path: Path,
        chunk_strategy: str,
        db: Session,
    ) -> dict:
        """
        Parse a document, split it into chunks, generate embeddings,
        store vectors in Qdrant, save metadata in SQLite,
        and return an upload summary.
        """

        #  Parse document
        text = self.parser.parse(file_path)

        text = self.parser.parse(file_path)

        print("\n===== PARSED TEXT =====")
        print(repr(text))
        print("Length:", len(text))
        print("=======================\n") 

        # Chunk text
        chunks = self.chunker.chunk(
            text=text,
            strategy=chunk_strategy,
        )

        if not chunks:
             raise ValueError("The document contains no text to process.")

        print("\n===== CHUNKS =====")
        print(chunks)
        print("Chunk count:", len(chunks))
        print("==================\n")



        # Save document metadata
        document = Document(
            filename=file_path.name,
            filetype=file_path.suffix.lower(),
            chunk_strategy=chunk_strategy,
        )

        document = save_document(
            db=db,
            document=document,
        )

        #  Generate embeddings
        embeddings = self.embedding_provider.encode(chunks)

        #  Build payloads
        payloads = []

        for index, chunk in enumerate(chunks):
            payloads.append(
                {
                    "document_id": document.id,
                    "chunk_number": index,
                    "text": chunk,
                }
            )

        print("\n===== DEBUG =====")    
        print("Embeddings type:", type(embeddings))
        print("Number of embeddings:", len(embeddings))

        if embeddings:
            print("Embedding type:", type(embeddings[0]))
            print("Embedding dimension:", len(embeddings[0]))

        print("Payloads type:", type(payloads))
        print("Number of payloads:", len(payloads))

        if payloads:
            print("First payload:", payloads[0])

        print("=================\n")




        #  Store vectors in Qdrant
        vector_ids = self.vector_store.upsert(
            embeddings=embeddings,
            payloads=payloads,
        )

        #  Save chunk metadata
        for index, vector_id in enumerate(vector_ids):
            chunk_metadata = ChunkMetadata(
                document_id=document.id,
                chunk_number=index,
                vector_id=vector_id,
                chunk_size=len(chunks[index]),
            )

            save_chunk_metadata(
                db=db,
                chunk=chunk_metadata,
            )

        # Return summary
        return {
            "document_id": document.id,
            "filename": document.filename,
            "filetype": document.filetype,
            "chunk_strategy": document.chunk_strategy,
            "chunks": len(chunks),
            "vectors": len(vector_ids),
        }