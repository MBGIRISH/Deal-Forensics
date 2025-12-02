"""
Enhanced Business Intelligence scoring logic.

This module computes 6 comprehensive metrics:
1. Pricing Clarity Score: Based on pricing discussions, ambiguity, renegotiations
2. Communication Quality Score: Based on sentiment, response times, clarity
3. Documentation Quality Score: Based on written confirmations, contracts, records
4. Competitive Risk Score: Based on competitor mentions, competitive pressure
5. Delivery/Execution Score: Based on timeline clarity, delivery planning, execution issues
6. Final Deal Health Score: Weighted composite of all metrics
"""

from __future__ import annotations

from dataclasses import dataclass
from statistics import mean
from typing import Any
import re
import json


@dataclass
class Scorecard:
    """
    Comprehensive business intelligence scorecard for a deal.
    
    All scores are normalized to 0-10 scale where:
    - 10 = Excellent / Low Risk / High Quality
    - 5 = Average / Medium Risk / Medium Quality
    - 0 = Poor / High Risk / Low Quality
    """
    
    pricing_clarity_score: float
    communication_quality_score: float
    documentation_quality_score: float
    competitive_risk_score: float
    delivery_execution_score: float
    final_deal_health_score: float

    def as_dict(self) -> dict[str, float]:
        """
        Convert scorecard to dictionary format.
        
        Returns:
            Dictionary with all score metrics
        """
        return {
            "pricing_clarity_score": self.pricing_clarity_score,
            "communication_quality_score": self.communication_quality_score,
            "documentation_quality_score": self.documentation_quality_score,
            "competitive_risk_score": self.competitive_risk_score,
            "delivery_execution_score": self.delivery_execution_score,
            "final_deal_health_score": self.final_deal_health_score,
        }


class DealScorer:
    """
    Enhanced deal health scoring based on multiple dimensions.
    
    Analyzes keywords, risks, missing sections, ambiguity, sentiment, and structure.
    """

    @staticmethod
    def _normalize(value: float, min_val: float = 0.0, max_val: float = 10.0) -> float:
        """Normalize a value to the 0-10 range."""
        return max(0.0, min(10.0, value))

    def _analyze_text_for_keywords(self, text: str, keywords: list[str]) -> int:
        """Count occurrences of keywords in text (case-insensitive)."""
        if not text:
            return 0
        text_lower = text.lower()
        return sum(1 for keyword in keywords if keyword.lower() in text_lower)

    def score(
        self, timeline: dict[str, Any], comparative: dict[str, Any], playbook: dict[str, Any]
    ) -> Scorecard:
        """
        Compute comprehensive deal health scorecard with 6 metrics.
        
        Args:
            timeline: Timeline analysis from Timeline Agent
            comparative: Comparative analysis from Comparative Agent
            playbook: Playbook analysis from Playbook Agent
            
        Returns:
            Scorecard with all 6 computed metrics
        """
        # Combine all text for keyword analysis
        all_text = json.dumps(timeline, ensure_ascii=False) + " " + \
                   json.dumps(comparative, ensure_ascii=False) + " " + \
                   json.dumps(playbook, ensure_ascii=False)
        
        # 1. PRICING CLARITY SCORE (0-10)
        pricing_score = self._score_pricing_clarity(timeline, comparative, all_text)
        
        # 2. COMMUNICATION QUALITY SCORE (0-10)
        comm_score = self._score_communication_quality(timeline, all_text)
        
        # 3. DOCUMENTATION QUALITY SCORE (0-10)
        doc_score = self._score_documentation_quality(timeline, playbook, all_text)
        
        # 4. COMPETITIVE RISK SCORE (0-10, inverted - high risk = low score)
        comp_risk = comparative.get("competitor_risk", 0.5)
        competitive_score = self._normalize(10 - (comp_risk * 10))
        
        # 5. DELIVERY/EXECUTION SCORE (0-10)
        delivery_score = self._score_delivery_execution(timeline, all_text)
        
        # 6. FINAL DEAL HEALTH SCORE (weighted composite)
        final_health = self._normalize(
            (pricing_score * 0.20) +
            (comm_score * 0.20) +
            (doc_score * 0.15) +
            (competitive_score * 0.20) +
            (delivery_score * 0.25)
        )
        
        return Scorecard(
            pricing_clarity_score=pricing_score,
            communication_quality_score=comm_score,
            documentation_quality_score=doc_score,
            competitive_risk_score=competitive_score,
            delivery_execution_score=delivery_score,
            final_deal_health_score=final_health,
        )
    
    def _score_pricing_clarity(self, timeline: dict, comparative: dict, text: str) -> float:
        """Score pricing clarity based on ambiguity, renegotiations, and clarity indicators."""
        base_score = 10.0
        
        # Penalize pricing delta
        pricing_delta = comparative.get("pricing_delta", 0.5)
        base_score -= pricing_delta * 5  # Up to -5 points
        
        # Count pricing negotiation events
        events = timeline.get("events", [])
        pricing_events = [e for e in events if isinstance(e, dict) and "pricing" in e.get("phase", "").lower()]
        if len(pricing_events) > 2:
            base_score -= 2.0  # Multiple renegotiations indicate ambiguity
        if len(pricing_events) > 4:
            base_score -= 1.5  # Excessive renegotiations
        
        # Enhanced pricing ambiguity keywords
        ambiguity_keywords = [
            "unclear", "to be determined", "tbd", "discuss later", "negotiable", "flexible",
            "pricing gap", "budget gap", "price too high", "too expensive", "out of budget",
            "renegotiate", "renegotiation", "counter offer", "price dispute"
        ]
        ambiguity_count = self._analyze_text_for_keywords(text, ambiguity_keywords)
        base_score -= min(3.0, ambiguity_count * 0.4)
        
        # Enhanced clear pricing indicators
        clarity_keywords = [
            "final price", "agreed price", "contract price", "signed price", "approved price",
            "pricing confirmed", "price agreed", "budget approved", "pricing locked"
        ]
        clarity_count = self._analyze_text_for_keywords(text, clarity_keywords)
        base_score += min(2.5, clarity_count * 0.4)
        
        # Check for risk terms
        risk_keywords = ["pricing issue", "price concern", "budget constraint", "cost overrun"]
        risk_count = self._analyze_text_for_keywords(text, risk_keywords)
        base_score -= min(2.0, risk_count * 0.5)
        
        return self._normalize(base_score)
    
    def _score_communication_quality(self, timeline: dict, text: str) -> float:
        """Score communication quality based on sentiment and clarity."""
        base_score = 10.0
        
        # Analyze communication events sentiment
        comm_events = timeline.get("communication_events", [])
        if comm_events:
            negative_count = sum(
                1 for event in comm_events
                if isinstance(event, dict) and event.get("sentiment") == "negative"
            )
            total_comm = len(comm_events)
            negative_ratio = negative_count / total_comm if total_comm > 0 else 0
            base_score -= negative_ratio * 6  # Up to -6 points for negative communication
        
        # Analyze timeline event sentiment
        events = timeline.get("events", [])
        negative_events = [e for e in events if isinstance(e, dict) and e.get("sentiment") == "negative"]
        if events:
            negative_event_ratio = len(negative_events) / len(events)
            base_score -= negative_event_ratio * 4  # Up to -4 points
        
        # Enhanced communication issue keywords
        issue_keywords = [
            "delayed response", "no response", "miscommunication", "confusion", "unclear",
            "communication breakdown", "poor communication", "lack of communication",
            "silence", "unresponsive", "delayed reply", "no reply"
        ]
        issue_count = self._analyze_text_for_keywords(text, issue_keywords)
        base_score -= min(3.5, issue_count * 0.5)
        
        # Enhanced good communication indicators
        good_keywords = [
            "clear communication", "prompt response", "confirmed", "documented", "written",
            "quick response", "responsive", "regular updates", "transparent", "open communication"
        ]
        good_count = self._analyze_text_for_keywords(text, good_keywords)
        base_score += min(2.5, good_count * 0.35)
        
        # Check escalation counts
        escalation_keywords = ["escalation", "escalated", "escalate", "escalating"]
        escalation_count = self._analyze_text_for_keywords(text, escalation_keywords)
        if escalation_count > 0:
            base_score -= min(2.0, escalation_count * 0.5)
        
        return self._normalize(base_score)
    
    def _score_documentation_quality(self, timeline: dict, playbook: dict, text: str) -> float:
        """Score documentation quality based on written records and confirmations."""
        base_score = 10.0
        
        # Check for missing documentation red flags
        red_flags = playbook.get("red_flags", [])
        doc_red_flags = [f for f in red_flags if isinstance(f, str) and ("written" in f.lower() or "document" in f.lower() or "verbal" in f.lower())]
        base_score -= len(doc_red_flags) * 1.5  # Penalize missing documentation
        
        # Check for verbal-only agreements (bad)
        verbal_keywords = ["verbal agreement", "verbal commitment", "said", "told", "mentioned"]
        verbal_count = self._analyze_text_for_keywords(text, verbal_keywords)
        if verbal_count > 3:
            base_score -= 3.0  # Too many verbal-only agreements
        
        # Check for written documentation indicators (good)
        written_keywords = ["written", "documented", "contract", "agreement", "signed", "confirmed in writing"]
        written_count = self._analyze_text_for_keywords(text, written_keywords)
        base_score += min(3.0, written_count * 0.4)
        
        # Check for missing documents
        missing_keywords = ["missing", "not provided", "not received", "pending"]
        missing_count = self._analyze_text_for_keywords(text, missing_keywords)
        base_score -= min(3.0, missing_count * 0.5)
        
        return self._normalize(base_score)
    
    def _score_delivery_execution(self, timeline: dict, text: str) -> float:
        """Score delivery/execution based on timeline clarity and execution issues."""
        base_score = 10.0
        
        # Check for delivery planning events
        events = timeline.get("events", [])
        delivery_events = [e for e in events if isinstance(e, dict) and "delivery" in e.get("phase", "").lower()]
        
        if not delivery_events:
            base_score -= 2.0  # No delivery planning is a red flag
        
        # Enhanced vague timeline keywords
        vague_keywords = [
            "tbd", "to be determined", "flexible", "approximately", "around", "sometime",
            "tentative", "estimated", "roughly", "maybe", "possibly", "uncertain timeline"
        ]
        vague_count = self._analyze_text_for_keywords(text, vague_keywords)
        base_score -= min(3.5, vague_count * 0.5)
        
        # Enhanced specific timeline indicators
        specific_keywords = [
            "specific date", "exact timeline", "confirmed date", "signed timeline",
            "guaranteed timeline", "committed date", "firm deadline", "locked timeline"
        ]
        specific_count = self._analyze_text_for_keywords(text, specific_keywords)
        base_score += min(2.5, specific_count * 0.5)
        
        # Enhanced delivery issue keywords
        issue_keywords = [
            "delay", "late", "behind schedule", "missed deadline", "timeline issue",
            "delivery delay", "implementation delay", "project delay", "schedule slip",
            "timeline concern", "delivery problem", "execution issue"
        ]
        issue_count = self._analyze_text_for_keywords(text, issue_keywords)
        base_score -= min(4.5, issue_count * 0.7)
        
        # Check escalation events
        escalation_events = [e for e in events if isinstance(e, dict) and "escalation" in e.get("phase", "").lower()]
        if escalation_events:
            base_score -= len(escalation_events) * 1.2
        
        # Check competitor references in delivery context
        competitor_keywords = ["competitor", "alternative vendor", "other solution", "competing"]
        comp_count = self._analyze_text_for_keywords(text, competitor_keywords)
        if comp_count > 2:
            base_score -= 1.0  # Competitive pressure affects execution
        
        return self._normalize(base_score)
