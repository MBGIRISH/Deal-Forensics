"Loaders and chunkers for deal documents."

from __future__ import annotations

from pathlib import Path
from typing import Iterable, List

from langchain_community.document_loaders import (
    PyPDFLoader,
    Docx2txtLoader,
    UnstructuredFileLoader,
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document


class DealDocumentLoader:
    """Handles ingestion of PDF/DOCX files."""

    def __init__(self, chunk_size: int = 1024, chunk_overlap: int = 128) -> None:
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size, chunk_overlap=chunk_overlap, separators=["\n\n", "\n", ". ", " "]
        )

    def _file_loader(self, file_path: Path):
        suffix = file_path.suffix.lower()
        if suffix == ".pdf":
            return PyPDFLoader(str(file_path))
        if suffix in {".docx", ".doc"}:
            return Docx2txtLoader(str(file_path))
        return UnstructuredFileLoader(str(file_path))

    def load(self, file_path: str | Path) -> List[Document]:
        path = Path(file_path)
        loader = self._file_loader(path)
        documents = loader.load()
        return documents

    def chunk(self, documents: Iterable[Document]) -> List[Document]:
        return self.splitter.split_documents(list(documents))

