from pathlib import Path

import fitz  # PyMuPDF


class DocumentParser:
    """
    Responsible for extracting text from supported document types.
    """

    SUPPORTED_EXTENSIONS = {".pdf", ".txt"}

    @classmethod
    def parse(cls, file_path: str | Path) -> str:
        """
        Parse a document and return its extracted text.

        Args:
            file_path: Path to the uploaded file.

        Returns:
            Extracted document text.

        Raises:
            ValueError: If the file type is not supported.
        """
        path = Path(file_path)

        suffix = path.suffix.lower()

        if suffix == ".pdf":
            return cls._parse_pdf(path)

        if suffix == ".txt":
            return cls._parse_txt(path)

        raise ValueError(f"Unsupported file type: {suffix}")

    @staticmethod
    def _parse_pdf(path: Path) -> str:
        """
        Extract text from a PDF document.
        """
        text_parts: list[str] = []

        with fitz.open(path) as pdf:
            for page in pdf:
                text_parts.append(page.get_text())

        return "\n".join(text_parts).strip()

    @staticmethod
    def _parse_txt(path: Path) -> str:
        """
        Read a UTF-8 text file.
        """
        return path.read_text(encoding="utf-8").strip()