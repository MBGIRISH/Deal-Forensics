"""
Vector store manager for FAISS vector database.

This module provides:
- FAISS-based similarity search for RAG
- Document indexing and retrieval
- Persistent storage of vector indices
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, List

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

from core.config import get_settings
from rag.embedder import EmbeddingService


class VectorStoreManager:
    """
    Manages FAISS vector store for similarity search in RAG pipeline.
    
    Features:
    - Builds FAISS indices from documents
    - Performs similarity search for retrieval
    - Persists indices to disk for reuse
    """

    def __init__(self, embedding_service: EmbeddingService | None = None) -> None:
        """
        Initialize vector store manager.
        
        Args:
            embedding_service: Optional embedding service (creates default if None)
        """
        self.settings = get_settings()
        self.embedding_service = embedding_service or EmbeddingService()
        self.faiss_index: FAISS | None = None

    def build_index(self, documents: List[Document]) -> None:
        """
        Build FAISS index from documents.
        
        Args:
            documents: List of LangChain Document objects to index
        """
        self.faiss_index = FAISS.from_documents(documents, self.embedding_service.model)

    def persist(self) -> None:
        """Persist FAISS index to disk for later reuse."""
        if not self.faiss_index:
            return
        path = Path(self.settings.vector_db_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        self.faiss_index.save_local(str(path))

    def load_or_build(self, documents: List[Document]) -> None:
        """
        Load existing index or build new one from documents.
        
        Args:
            documents: Documents to use if building new index
        """
        path = Path(self.settings.vector_db_path)
        if path.exists():
            self.faiss_index = FAISS.load_local(
                str(path),
                self.embedding_service.model,
                allow_dangerous_deserialization=True,
            )
        else:
            self.build_index(documents)
            self.persist()

    def similarity_search(self, query: str, k: int = 5) -> List[Document]:
        """
        Perform similarity search to retrieve relevant documents.
        
        Args:
            query: Search query string
            k: Number of documents to retrieve
            
        Returns:
            List of most similar documents
            
        Raises:
            RuntimeError: If index not initialized
        """
        if not self.faiss_index:
            raise RuntimeError("Vector store not initialized")
        return self.faiss_index.similarity_search(query, k=k)

    def as_retriever(self, **kwargs) -> Any:
        """
        Get LangChain retriever interface.
        
        Args:
            **kwargs: Additional retriever configuration
            
        Returns:
            LangChain retriever object
        """
        if not self.faiss_index:
            raise RuntimeError("Vector store not initialized")
        return self.faiss_index.as_retriever(search_kwargs=kwargs)
