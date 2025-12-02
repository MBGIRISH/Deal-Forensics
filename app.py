"Main orchestration entry-point for the Deal Forensics system."

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Any, Dict

from agents import ComparativeAgent, PlaybookAgent, TimelineAgent
from agents.graph import DealForensicsGraph
from core.config import ensure_directories
from core.deal_parser import consolidate_documents, infer_metadata
from core.document_validator import (
    validate_file_type,
    validate_file_size,
    extract_text_from_document,
    validate_financial_document,
    sanitize_pdf_text,
    process_valid_document,
    validate_document_relevance,
    handle_invalid_document,
)
from core.repository import DealRepository
from core.scoring import DealScorer
from rag.embedder import EmbeddingService
from rag.loader import DealDocumentLoader
from rag.vectorstore import VectorStoreManager
from utils.pdf_report import ReportBuilder


class DealForensicsOrchestrator:
    """Coordinates ingestion, retrieval, multi-agent reasoning, and persistence."""

    def __init__(self) -> None:
        ensure_directories()
        self.loader = DealDocumentLoader()
        self.embedding_service = EmbeddingService()
        self.vector_store = VectorStoreManager(self.embedding_service)
        self.timeline_agent = TimelineAgent()
        self.comparative_agent = ComparativeAgent()
        self.playbook_agent = PlaybookAgent()
        self.scorer = DealScorer()
        self.graph = DealForensicsGraph(
            timeline_agent=self.timeline_agent,
            comparative_agent=self.comparative_agent,
            playbook_agent=self.playbook_agent,
            scorer=self.scorer,
        )
        self.repository = DealRepository()
        self.report_builder = ReportBuilder()

    def _save_temp_file(self, file_bytes: bytes, filename: str) -> Path:
        """Save uploaded file to temporary location."""
        suffix = Path(filename).suffix.lower()
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as handle:
            handle.write(file_bytes)
            temp_path = Path(handle.name)
        return temp_path

    def _build_deal_summary(self, metadata: Dict[str, Any], text: str) -> str:
        snippet = text[:800].replace("\n", " ")
        name = metadata.get("deal_name") or "Unnamed Opportunity"
        owner = metadata.get("owner") or "Unknown"
        return f"Deal {name} owned by {owner}. Stage: {metadata.get('stage', 'Closed Lost')}. Summary: {snippet}"

    def analyze_file(self, file_bytes: bytes, filename: str) -> Dict[str, Any]:
        """
        Analyze a financial/deal PDF file with strict validation.
        
        Args:
            file_bytes: PDF file content as bytes
            filename: Name of the uploaded file
            
        Returns:
            Dictionary with analysis results
            
        Raises:
            ValueError: If validation fails at any stage
        """
        # Step 1: Validate file type (ONLY PDF allowed)
        is_valid_type, type_error = validate_file_type(filename)
        if not is_valid_type:
            raise ValueError(type_error)
        
        # Step 2: Validate file size
        is_valid_size, size_error = validate_file_size(file_bytes)
        if not is_valid_size:
            raise ValueError(size_error)
        
        # Step 3: Extract text from document (PDF or DOCX)
        try:
            extracted_text, page_count = extract_text_from_document(file_bytes, filename)
        except Exception as e:
            raise ValueError(f"Failed to extract text from document: {str(e)}")
        
        # Step 4: Sanitize text
        extracted_text = sanitize_pdf_text(extracted_text)
        
        # Step 5: Validate financial/deal content (STRICT)
        is_financial, financial_error = validate_financial_document(extracted_text, page_count)
        if not is_financial:
            raise ValueError(financial_error)
        
        # Step 6: Final validation check (STRICT - prevents non-business content)
        is_valid, validation_error = process_valid_document(extracted_text, page_count)
        if not is_valid:
            raise ValueError(validation_error)
        
        # Step 7: Additional LLM validation for edge cases (STRICT)
        is_relevant, relevance_error = validate_document_relevance(extracted_text, filename)
        if not is_relevant:
            raise ValueError(f"❌ Document Validation Failed: {relevance_error}")
        
        # Step 8: Process document (all validations passed - NO OUTPUT if validation fails)
        temp_path = self._save_temp_file(file_bytes, filename)
        try:
            documents = self.loader.load(temp_path)
            chunks = self.loader.chunk(documents)
            
            if not chunks:
                raise ValueError("No readable content detected in the uploaded file after processing.")

            self.vector_store.build_index(chunks)
            combined_text = consolidate_documents(chunks)
            metadata = infer_metadata(combined_text)
            deal_summary = self._build_deal_summary(metadata.__dict__, combined_text)

            retrieved_docs = self.vector_store.similarity_search(deal_summary, k=5)
            retrieved_chunks = [doc.page_content for doc in retrieved_docs]

            state = {
                "raw_context": combined_text,
                "deal_summary": deal_summary,
                "retrieved_chunks": retrieved_chunks,
            }

            result = self.graph.run(state)

            record = {
                "deal_name": metadata.deal_name,
                "owner": metadata.owner,
                "industry": metadata.industry,
                "value": metadata.value,
                "stage": metadata.stage,
                "scores": result.get("scorecard"),
                "loss_summary": result.get("playbook", {}).get("what_went_wrong"),
            }
            self.repository.insert(record)

            report_bytes = self.report_builder.build(result)
            result["report"] = report_bytes
            result["documents_ingested"] = len(chunks)
            result["metadata"] = metadata.__dict__

            return result
        finally:
            # Always clean up temp file
            temp_path.unlink(missing_ok=True)

