"""
Embedding service with caching and retry logic.

This module provides:
- HuggingFace sentence transformer embeddings
- Embedding cache to avoid recomputation
- Retry logic for reliability
"""

from __future__ import annotations

from typing import Iterable, List

from langchain_community.embeddings import HuggingFaceEmbeddings
from tenacity import retry, stop_after_attempt, wait_exponential

from core.cache import EmbeddingCache
from core.config import get_settings


class EmbeddingService:
    """
    Wrapper around HuggingFace sentence transformers for embeddings.
    
    Features:
    - Caching to avoid recomputing embeddings
    - Retry logic for reliability
    - Support for both document and query embeddings
    """

    def __init__(self) -> None:
        """Initialize embedding service with cache."""
        settings = get_settings()
        self.cache = EmbeddingCache(settings.embedding_cache_path)
        self.model = HuggingFaceEmbeddings(model_name=settings.embedding_model)

    def _maybe_cached(self, text: str) -> list[float] | None:
        """
        Check if embedding is cached.
        
        Args:
            text: Text to check
            
        Returns:
            Cached embedding vector or None
        """
        return self.cache.get(text)

    def _store_cache(self, text: str, vector: list[float]) -> None:
        """
        Store embedding in cache.
        
        Args:
            text: Original text
            vector: Embedding vector
        """
        self.cache.set(text, vector)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, max=10))
    def embed_documents(self, documents: Iterable[str]) -> List[List[float]]:
        """
        Embed multiple documents with caching.
        
        Args:
            documents: Iterable of document strings
            
        Returns:
            List of embedding vectors
        """
        vectors: List[List[float]] = []
        for doc in documents:
            cached = self._maybe_cached(doc)
            if cached is not None:
                vectors.append(cached)
                continue
            vector = self.model.embed_query(doc)
            self._store_cache(doc, vector)
            vectors.append(vector)
        return vectors

    def embed_query(self, text: str) -> List[float]:
        """
        Embed a query string with caching.
        
        Args:
            text: Query text
            
        Returns:
            Embedding vector
        """
        cached = self._maybe_cached(text)
        if cached is not None:
            return cached
        vector = self.model.embed_query(text)
        self._store_cache(text, vector)
        return vector
