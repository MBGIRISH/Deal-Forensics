"""
Helpers to normalize deal documents and metadata.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Iterable

from langchain_core.documents import Document


@dataclass
class DealMetadata:
    """Structured view of a deal."""

    deal_name: str
    owner: str
    industry: str
    value: float | None
    close_date: datetime | None
    stage: str


def infer_metadata(text: str) -> DealMetadata:
    """
    Enhanced heuristic parser with improved extraction patterns.
    """

    import re
    from dateutil import parser as date_parser
    
    lower = text.lower()
    deal_name = "Untitled Deal"
    owner = "Unknown"
    industry = "General"
    stage = "Closed Lost"
    value = None
    close_date = None

    # Extract from structured format (key: value)
    for line in text.splitlines()[:50]:  # Check first 50 lines
        normalized = line.strip()
        if ":" not in normalized:
            continue
        key, val = normalized.split(":", 1)
        key = key.lower().strip()
        val = val.strip()
        if key in {"deal", "deal name", "opportunity", "customer", "buyer", "client"}:
            deal_name = val or deal_name
        elif key in {"owner", "rep", "sales rep", "seller", "account manager"}:
            owner = val or owner
        elif key in {"industry", "vertical", "sector"}:
            industry = val or industry
        elif key in {"value", "amount", "arr", "acv", "deal value", "deal size", "revenue"}:
            # Extract number from value (handles $2,500,000 or 2.5M)
            cleaned = re.sub(r'[^\d.]', '', val.replace(",", ""))
            if "m" in val.lower() or "million" in val.lower():
                try:
                    value = float(cleaned) * 1000000
                except ValueError:
                    pass
            elif "k" in val.lower() or "thousand" in val.lower():
                try:
                    value = float(cleaned) * 1000
                except ValueError:
                    pass
            else:
                try:
                    value = float(cleaned)
                except ValueError:
                    pass
        elif key in {"close date", "closed", "decision date", "closed date", "final date"}:
            for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%b %d, %Y", "%B %d, %Y", "%d %B %Y", "%d %b %Y"):
                try:
                    close_date = datetime.strptime(val, fmt)
                    break
                except ValueError:
                    continue
            # Try dateutil parser as fallback
            if not close_date:
                try:
                    close_date = date_parser.parse(val, fuzzy=True)
                except Exception:
                    pass
        elif key in {"stage", "sales stage", "status", "outcome"}:
            stage = val or stage

    # Enhanced extraction from unstructured text
    # Extract deal value from various patterns
    if value is None:
        value_patterns = [
            r'\$[\d,]+\.?\d*\s*(?:million|M|m)',
            r'\$[\d,]+',
            r'deal value[:\s]+\$?[\d,]+',
            r'value[:\s]+\$?[\d,]+',
            r'\$?[\d,]+\.?\d*\s*(?:million|M)',
        ]
        for pattern in value_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                val_str = match.group(0)
                cleaned = re.sub(r'[^\d.]', '', val_str.replace(",", ""))
                if "m" in val_str.lower() or "million" in val_str.lower():
                    try:
                        value = float(cleaned) * 1000000
                        break
                    except ValueError:
                        pass
                else:
                    try:
                        value = float(cleaned)
                        break
                    except ValueError:
                        pass

    # Extract deal name from title or first line
    if deal_name == "Untitled Deal":
        first_lines = text.splitlines()[:5]
        for line in first_lines:
            line = line.strip()
            if len(line) > 10 and len(line) < 100 and not line.startswith("#"):
                # Check if it looks like a title
                if any(word in line.lower() for word in ["deal", "opportunity", "platform", "system", "solution"]):
                    deal_name = line[:80]  # Limit length
                    break

    # Extract owner/seller from patterns
    if owner == "Unknown":
        owner_patterns = [
            r'owner[:\s]+([A-Z][a-zA-Z\s]+)',
            r'sales rep[:\s]+([A-Z][a-zA-Z\s]+)',
            r'rep[:\s]+([A-Z][a-zA-Z\s]+)',
            r'account manager[:\s]+([A-Z][a-zA-Z\s]+)',
        ]
        for pattern in owner_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                owner = match.group(1).strip()[:50]
                break

    # Extract industry from context
    if industry == "General":
        industry_keywords = {
            "technology": ["tech", "saas", "software", "platform", "cloud", "digital"],
            "healthcare": ["health", "medical", "hospital", "clinic", "patient"],
            "financial": ["finance", "banking", "financial", "investment", "capital"],
            "retail": ["retail", "e-commerce", "commerce", "store", "merchant"],
            "manufacturing": ["manufacturing", "production", "factory", "industrial"],
            "education": ["education", "school", "university", "learning", "student"],
        }
        for ind, keywords in industry_keywords.items():
            if any(kw in lower for kw in keywords):
                industry = ind.title()
                break

    return DealMetadata(
        deal_name=deal_name,
        owner=owner,
        industry=industry,
        value=value,
        close_date=close_date,
        stage=stage,
    )


def consolidate_documents(documents: Iterable[Document]) -> str:
    """Return a single normalized text blob for downstream processing."""

    return "\n\n".join(doc.page_content for doc in documents)

