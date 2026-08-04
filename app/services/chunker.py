import re
from enum import Enum


class ChunkStrategy(str, Enum):
    FIXED = "fixed"
    SENTENCE = "sentence"


class TextChunker:
    """
    Responsible for splitting text into chunks.
    """

    @staticmethod
    def chunk(
        text: str,
        strategy: ChunkStrategy,
        chunk_size: int = 500,
        overlap: int = 50,
    ) -> list[str]:
        """
        Split text using the selected chunking strategy.
        """

        text = text.strip()

        if not text:
            return []

        if strategy == ChunkStrategy.FIXED:
            return TextChunker._fixed_chunk(
                text=text,
                chunk_size=chunk_size,
                overlap=overlap,
            )

        if strategy == ChunkStrategy.SENTENCE:
            return TextChunker._sentence_chunk(text)

        raise ValueError(f"Unsupported chunking strategy: {strategy}")

    @staticmethod
    def _fixed_chunk(
        text: str,
        chunk_size: int,
        overlap: int,
    ) -> list[str]:
        """
        Split text into overlapping fixed-size chunks.
        """

        chunks: list[str] = []

        start = 0

        while start < len(text):

            end = start + chunk_size

            chunk = text[start:end].strip()

            if chunk:
                chunks.append(chunk)

            start += chunk_size - overlap

        return chunks

    @staticmethod
    def _sentence_chunk(
        text: str,
    ) -> list[str]:
        """
        Split text by sentence boundaries.
        """

        sentences = re.split(r"(?<=[.!?])\s+", text)

        return [
            sentence.strip()
            for sentence in sentences
            if sentence.strip()
        ]