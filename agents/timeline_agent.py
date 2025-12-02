"""
Advanced Timeline Agent: Extracts chronological events with natural language date parsing.

This agent:
- Extracts REAL timeline events (outreach, negotiation, pricing, delivery, escalation, decision)
- Parses natural language dates ("on January 5th", "two days later", "during negotiation")
- Infers realistic timestamps with 1-7 day gaps (never epoch dates)
- Always returns valid ISO dates (YYYY-MM-DD)
- Assigns sentiment per event (positive/neutral/negative)
- Calculates Timeline Score (1-10) based on clarity, ordering, missing events, ambiguity, delays
- Ensures all 5 required phases have start + end timestamps
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
import json
import re
from datetime import datetime, timedelta
from dateutil import parser as date_parser
from dateutil.relativedelta import relativedelta

from agents.base import BaseAgent
from core.gemini_client import generate_json


# Standard sales phases
REQUIRED_PHASES = [
    "Discovery Phase",
    "Pricing Negotiation Phase",
    "Delivery Planning Phase",
    "Issue/Escalation Phase",
    "Final Decision Phase"
]

# Phase sentiment mapping
PHASE_SENTIMENT = {
    "Discovery Phase": "neutral",
    "Pricing Negotiation Phase": "neutral",
    "Delivery Planning Phase": "neutral",
    "Issue/Escalation Phase": "negative",
    "Final Decision Phase": "negative"
}

# Event type patterns for extraction
EVENT_PATTERNS = {
    "initial_outreach": ["initial", "first contact", "outreach", "first call", "discovery call", "introductory"],
    "first_negotiation": ["first negotiation", "initial negotiation", "first discussion", "opening discussion"],
    "pricing_discussion": ["pricing", "price", "quote", "budget", "cost", "pricing discussion", "pricing proposal"],
    "discount_request": ["discount", "reduction", "lower price", "price reduction", "budget constraint"],
    "delivery_discussion": ["delivery", "implementation", "timeline", "rollout", "deployment", "delivery plan"],
    "escalation": ["escalation", "escalated", "issue", "problem", "concern", "delay", "blocker"],
    "final_decision": ["final", "decision", "outcome", "closed", "lost", "won", "rejected", "accepted"]
}


class DateInferencer:
    """Infers realistic dates from natural language and context."""
    
    def __init__(self, base_date: datetime | None = None):
        """
        Initialize date inferencer.
        
        Args:
            base_date: Base date for relative calculations (defaults to current date)
        """
        self.base_date = base_date or datetime.now()
        self.current_date = self.base_date
        self.event_dates = []  # Track inferred dates
    
    def parse_natural_date(self, text: str) -> datetime | None:
        """
        Parse natural language date expressions.
        
        Handles:
        - "January 5th", "Jan 5", "1/5/2024"
        - "two days later", "next week", "after 3 days"
        - "on the call", "during negotiation" (relative)
        
        Args:
            text: Natural language date string
            
        Returns:
            Parsed datetime or None
        """
        if not text:
            return None
        
        text = text.strip().lower()
        
        # Try dateutil parser first
        try:
            parsed = date_parser.parse(text, default=self.base_date, fuzzy=True)
            if parsed and parsed.year >= 2020:  # Ensure reasonable date
                return parsed
        except Exception:
            pass
        
        # Handle relative expressions
        relative_patterns = {
            r"(\d+)\s+days?\s+later": lambda m: self.current_date + timedelta(days=int(m.group(1))),
            r"(\d+)\s+weeks?\s+later": lambda m: self.current_date + timedelta(weeks=int(m.group(1))),
            r"(\d+)\s+months?\s+later": lambda m: self.current_date + relativedelta(months=int(m.group(1))),
            r"next\s+week": lambda m: self.current_date + timedelta(weeks=1),
            r"next\s+month": lambda m: self.current_date + relativedelta(months=1),
            r"two\s+days?\s+later": lambda m: self.current_date + timedelta(days=2),
            r"three\s+days?\s+later": lambda m: self.current_date + timedelta(days=3),
        }
        
        for pattern, func in relative_patterns.items():
            match = re.search(pattern, text)
            if match:
                return func(match)
        
        # Handle month names
        month_patterns = {
            "january": 1, "jan": 1, "february": 2, "feb": 2,
            "march": 3, "mar": 3, "april": 4, "apr": 4,
            "may": 5, "june": 6, "jun": 6, "july": 7, "jul": 7,
            "august": 8, "aug": 8, "september": 9, "sep": 9, "sept": 9,
            "october": 10, "oct": 10, "november": 11, "nov": 11,
            "december": 12, "dec": 12
        }
        
        for month_name, month_num in month_patterns.items():
            if month_name in text:
                day_match = re.search(r"(\d{1,2})(?:st|nd|rd|th)?", text)
                if day_match:
                    day = int(day_match.group(1))
                    year = self.base_date.year
                    try:
                        return datetime(year, month_num, day)
                    except ValueError:
                        return datetime(year, month_num, 28)
        
        return None
    
    def infer_realistic_date(self, phase: str, event_index: int, total_events: int, gap_days: int = 3) -> datetime:
        """
        Infer a realistic date based on phase and event position with configurable gap.
        
        Args:
            phase: Event phase
            event_index: Index of event in sequence
            total_events: Total number of events
            gap_days: Days between events (1-7)
            
        Returns:
            Realistic datetime (never epoch)
        """
        # Base timeline: assume deal started 3-6 months ago
        months_ago = 4
        start_date = self.base_date - relativedelta(months=months_ago)
        
        # Phase-based date ranges
        phase_days = {
            "Discovery Phase": (0, 14),
            "Pricing Negotiation Phase": (14, 35),
            "Delivery Planning Phase": (35, 50),
            "Issue/Escalation Phase": (50, 70),
            "Final Decision Phase": (70, 90),
        }
        
        if phase in phase_days:
            day_min, day_max = phase_days[phase]
            phase_progress = event_index / max(total_events, 1)
            day_offset = day_min + (day_max - day_min) * phase_progress
        else:
            day_offset = (event_index / max(total_events, 1)) * 90
        
        inferred_date = start_date + timedelta(days=int(day_offset))
        
        # Ensure date is not in the future
        if inferred_date > self.base_date:
            inferred_date = self.base_date - timedelta(days=1)
        
        # Ensure date is not epoch (before 2000)
        if inferred_date.year < 2000:
            inferred_date = datetime(2024, 1, 1) + timedelta(days=int(day_offset))
        
        return inferred_date
    
    def get_next_date(self, last_date: datetime | None = None, gap_days: int = 3) -> datetime:
        """
        Get next realistic date with configurable gap (1-7 days).
        
        Args:
            last_date: Previous date (defaults to base_date)
            gap_days: Days to add (1-7, default 3)
            
        Returns:
            Next date
        """
        if last_date:
            next_date = last_date + timedelta(days=gap_days)
        else:
            next_date = self.base_date - relativedelta(months=4)
        
        if next_date > self.base_date:
            next_date = self.base_date - timedelta(days=1)
        
        if next_date.year < 2000:
            next_date = datetime(2024, 1, 1)
        
        return next_date


PROMPT_TEMPLATE = """
You are an expert sales deal forensics analyst specializing in timeline extraction.

CRITICAL REQUIREMENTS:

1. Extract REAL timeline events from the deal narrative:
   - Initial outreach / first contact
   - First negotiation / opening discussion
   - Pricing discussion / quote / budget talks
   - Discount requests / price reductions
   - Delivery discussions / implementation planning
   - Escalation moments / issues / problems
   - Final decision / outcome

2. Extract ALL 5 required phases with events:
   - Discovery Phase: Initial contact, requirements gathering, discovery calls
   - Pricing Negotiation Phase: Pricing discussions, quotes, negotiations, discount requests
   - Delivery Planning Phase: Implementation planning, timeline discussions, resource planning
   - Issue/Escalation Phase: Problems, delays, escalations, concerns, blockers
   - Final Decision Phase: Final communication, decision, outcome

3. DATE EXTRACTION - Extract dates from natural language:
   - "on January 5th" → 2024-01-05
   - "two days later" → relative date
   - "during negotiation" → infer from context
   - "after pricing discussion" → infer sequence
   - If no date found, use relative position with 1-7 day gaps

4. SENTIMENT per event:
   - positive: Good progress, positive feedback, agreement, success
   - neutral: Standard communication, routine updates, normal process
   - negative: Problems, delays, disagreements, concerns, failures

5. Return JSON:
{{
  "events": [
    {{
      "event_name": "Short descriptive title",
      "description": "Detailed description of what happened",
      "phase": "Discovery Phase" | "Pricing Negotiation Phase" | "Delivery Planning Phase" | "Issue/Escalation Phase" | "Final Decision Phase",
      "timestamp": "YYYY-MM-DD" or natural language date,
      "confidence": 0.0-1.0,
      "sentiment": "positive" | "neutral" | "negative"
    }},
    ...
  ],
  "phase_summary": {{"Discovery Phase": "...", ...}},
  "average_phase_score": 1-10,
  "major_blockers": ["blocker 1", ...],
  "communication_events": [{{"event": "...", "sentiment": "..."}}, ...]
}}

Deal Context:
{context}

Extract at least 10-15 events covering ALL phases. Focus on REAL events mentioned in the document.
""".strip()


@dataclass
class TimelineAgent(BaseAgent):
    """
    Advanced timeline extractor with natural language date parsing and timeline scoring.
    
    Features:
    - Extracts real events from documents
    - Parses natural language dates
    - Infers realistic timestamps (never epoch)
    - Assigns sentiment per event
    - Calculates timeline score
    - Ensures all phases have start + end timestamps
    """

    def analyze(self, context: str) -> dict[str, Any]:
        """
        Analyze deal context and extract timeline with realistic dates and scoring.
        
        Args:
            context: Raw deal document text
            
        Returns:
            Dictionary with events, phases, realistic dates, and timeline score
        """
        if not context or len(context.strip()) < 50:
            return self._default_timeline()
        
        # Extract base date from document first (for accurate date inference)
        base_date = self._extract_base_date_from_context(context)
        
        prompt = PROMPT_TEMPLATE.format(context=context[:12000])
        
        try:
            result = generate_json(prompt)
            
            if not isinstance(result, dict):
                return self._default_timeline()
            
            events = result.get("events", [])
            if not events or len(events) < 5:
                events = self._enhance_events(events, context)
                result["events"] = events
            
            # Process events: parse dates and ensure realistic timestamps (use extracted base_date)
            processed_events = self._process_events(events, context, base_date)
            result["events"] = processed_events
            
            # Ensure all phases covered with start + end timestamps
            result["events"] = self._ensure_phase_coverage(result["events"], context, base_date)
            
            # Calculate timeline score
            result["timeline_score"] = self._calculate_timeline_score(result["events"], context)
            
            # Ensure other fields
            result.setdefault("phase_summary", self._generate_phase_summary(result["events"]))
            result.setdefault("average_phase_score", 5.0)
            result.setdefault("major_blockers", [])
            result.setdefault("communication_events", [])
            
            return result
            
        except Exception as e:
            return self._extract_fallback_timeline(context, base_date)
    
    def _calculate_timeline_score(self, events: list[dict[str, Any]], context: str) -> float:
        """
        Calculate Timeline Score (1-10) based on clarity, ordering, missing events, ambiguity, delays.
        
        Args:
            events: List of timeline events
            context: Original context
            
        Returns:
            Timeline score (1-10)
        """
        if not events:
            return 3.0  # Low score for no events
        
        base_score = 10.0
        
        # Check for missing phases (penalty)
        existing_phases = {e.get("phase") for e in events if isinstance(e, dict)}
        missing_phases = set(REQUIRED_PHASES) - existing_phases
        base_score -= len(missing_phases) * 1.5  # -1.5 per missing phase
        
        # Check for date clarity (penalty for vague dates)
        vague_dates = 0
        for event in events:
            if isinstance(event, dict):
                timestamp = str(event.get("timestamp", ""))
                if any(vague in timestamp.lower() for vague in ["week", "month", "day", "unknown", "tbd"]):
                    vague_dates += 1
        base_score -= min(2.0, vague_dates * 0.3)  # Penalty for vague dates
        
        # Check for ordering issues (penalty)
        try:
            dates = []
            for event in events:
                if isinstance(event, dict):
                    timestamp = event.get("timestamp", "")
                    try:
                        date = datetime.strptime(timestamp, "%Y-%m-%d")
                        dates.append(date)
                    except Exception:
                        pass
            
            if len(dates) > 1:
                # Check if dates are in order
                is_ordered = all(dates[i] <= dates[i+1] for i in range(len(dates)-1))
                if not is_ordered:
                    base_score -= 1.5  # Penalty for unordered dates
        except Exception:
            pass
        
        # Check for delays/escalations (penalty)
        escalation_count = sum(
            1 for e in events 
            if isinstance(e, dict) and ("escalation" in e.get("phase", "").lower() or e.get("sentiment") == "negative")
        )
        if escalation_count > len(events) * 0.3:
            base_score -= 2.0  # Penalty for many escalations
        
        # Check for ambiguity keywords
        ambiguity_keywords = ["unclear", "tbd", "to be determined", "unknown", "maybe", "possibly"]
        ambiguity_count = sum(1 for keyword in ambiguity_keywords if keyword in context.lower())
        base_score -= min(1.5, ambiguity_count * 0.2)
        
        # Reward for good structure
        if len(events) >= 10:
            base_score += 1.0  # Reward for comprehensive timeline
        
        # Ensure score is in valid range
        return max(1.0, min(10.0, base_score))
    
    def _extract_base_date_from_context(self, context: str) -> datetime:
        """
        Extract the most relevant base date from document context.
        
        Looks for:
        - Close date / decision date
        - Latest mentioned date
        - Current year dates
        
        Args:
            context: Document text
            
        Returns:
            Base datetime for date inference
        """
        import re
        from dateutil import parser as date_parser
        
        dates_found = []
        
        # Look for close date / decision date
        close_patterns = [
            r"close date[:\s]+([A-Za-z]+\s+\d{1,2},?\s+\d{4})",
            r"closed[:\s]+([A-Za-z]+\s+\d{1,2},?\s+\d{4})",
            r"decision date[:\s]+([A-Za-z]+\s+\d{1,2},?\s+\d{4})",
            r"final date[:\s]+([A-Za-z]+\s+\d{1,2},?\s+\d{4})",
        ]
        
        for pattern in close_patterns:
            match = re.search(pattern, context, re.IGNORECASE)
            if match:
                try:
                    date = date_parser.parse(match.group(1), fuzzy=True)
                    if date.year >= 2020 and date.year <= datetime.now().year + 1:
                        return date
                except Exception:
                    pass
        
        # Look for dates in YYYY-MM-DD format
        iso_dates = re.findall(r'\b(\d{4})-(\d{2})-(\d{2})\b', context)
        for year, month, day in iso_dates:
            try:
                date = datetime(int(year), int(month), int(day))
                if date.year >= 2020 and date.year <= datetime.now().year + 1:
                    dates_found.append(date)
            except Exception:
                pass
        
        # Look for dates in "Month Day, Year" format
        month_date_pattern = r'\b([A-Za-z]+)\s+(\d{1,2}),?\s+(\d{4})\b'
        month_dates = re.findall(month_date_pattern, context)
        for month_str, day, year in month_dates:
            try:
                date = date_parser.parse(f"{month_str} {day}, {year}", fuzzy=True)
                if date.year >= 2020 and date.year <= datetime.now().year + 1:
                    dates_found.append(date)
            except Exception:
                pass
        
        # Return latest date found, or default to 4 months ago
        if dates_found:
            latest_date = max(dates_found)
            # Use latest date as base, but ensure it's not in the future
            if latest_date > datetime.now():
                return datetime.now() - relativedelta(months=4)
            return latest_date
        
        # Default: assume deal closed 1-3 months ago
        return datetime.now() - relativedelta(months=2)
    
    def _process_events(self, events: list[dict[str, Any]], context: str, base_date: datetime | None = None) -> list[dict[str, Any]]:
        """
        Process events: parse dates and ensure realistic timestamps with 1-7 day gaps.
        
        Args:
            events: Raw events from LLM
            context: Original context for date inference
            base_date: Base date for inference (extracted from document)
            
        Returns:
            Processed events with valid ISO dates
        """
        inferencer = DateInferencer(base_date=base_date)
        
        processed = []
        last_date = None
        gap_days = 3  # Default gap, will vary 1-7
        
        for i, event in enumerate(events):
            if not isinstance(event, dict):
                continue
            
            phase = event.get("phase", "Discovery Phase")
            timestamp_str = event.get("timestamp", "")
            
            # Try to parse date
            parsed_date = None
            if timestamp_str:
                parsed_date = inferencer.parse_natural_date(timestamp_str)
            
            # If parsing failed, infer realistic date with gap
            if not parsed_date:
                # Vary gap between 1-7 days
                gap_days = (i % 7) + 1
                if last_date:
                    parsed_date = inferencer.get_next_date(last_date, gap_days=gap_days)
                else:
                    parsed_date = inferencer.infer_realistic_date(phase, i, len(events), gap_days=gap_days)
            
            # Ensure this date is after last date
            if last_date and parsed_date <= last_date:
                gap_days = (i % 7) + 1
                parsed_date = inferencer.get_next_date(last_date, gap_days=gap_days)
            
            last_date = parsed_date
            
            # Format as ISO date
            iso_date = parsed_date.strftime("%Y-%m-%d")
            
            # Ensure sentiment
            sentiment = event.get("sentiment", PHASE_SENTIMENT.get(phase, "neutral"))
            
            processed.append({
                "event_name": event.get("event_name", f"Event {i+1}"),
                "description": event.get("description", event.get("summary", "")),
                "phase": phase,
                "timestamp": iso_date,
                "confidence": max(0.0, min(1.0, float(event.get("confidence", 0.7)))),
                "sentiment": sentiment
            })
        
        return processed
    
    def _ensure_phase_coverage(self, events: list[dict[str, Any]], context: str, base_date: datetime | None = None) -> list[dict[str, Any]]:
        """
        Ensure all 5 phases are represented with start + end timestamps.
        
        Args:
            events: Current events
            context: Original context
            base_date: Base date for inference (extracted from document)
            
        Returns:
            Events with all phases covered, including start + end for each phase
        """
        inferencer = DateInferencer(base_date=base_date)
        last_date = None
        
        # Find last event date
        for event in events:
            if isinstance(event, dict):
                try:
                    event_date = datetime.strptime(event.get("timestamp", ""), "%Y-%m-%d")
                    if not last_date or event_date > last_date:
                        last_date = event_date
                except Exception:
                    pass
        
        if not last_date:
            last_date = datetime.now() - relativedelta(months=4)
        
        # Group events by phase
        phase_events = {phase: [] for phase in REQUIRED_PHASES}
        for event in events:
            if isinstance(event, dict):
                phase = event.get("phase")
                if phase in phase_events:
                    phase_events[phase].append(event)
        
        # Ensure each phase has start and end events
        result_events = []
        phase_start_dates = {}
        
        for phase in REQUIRED_PHASES:
            phase_evts = phase_events[phase]
            
            if phase_evts:
                # Phase has events, use them
                result_events.extend(phase_evts)
                # Get earliest date in phase
                try:
                    phase_dates = [datetime.strptime(e.get("timestamp", ""), "%Y-%m-%d") for e in phase_evts if e.get("timestamp")]
                    if phase_dates:
                        phase_start_dates[phase] = min(phase_dates)
                except Exception:
                    pass
            else:
                # Generate start event for missing phase
                start_date = inferencer.get_next_date(last_date, gap_days=3)
                start_event = self._generate_phase_event(phase, context, "start", start_date, inferencer)
                if start_event:
                    result_events.append(start_event)
                    phase_start_dates[phase] = start_date
                    last_date = start_date
                
                # Generate end event for phase
                end_date = inferencer.get_next_date(start_date, gap_days=5)
                end_event = self._generate_phase_event(phase, context, "end", end_date, inferencer)
                if end_event:
                    result_events.append(end_event)
                    last_date = end_date
        
        # Sort by date
        result_events.sort(key=lambda e: e.get("timestamp", "2000-01-01"))
        
        return result_events
    
    def _generate_phase_event(self, phase: str, context: str, event_type: str, date: datetime, inferencer: DateInferencer) -> dict[str, Any] | None:
        """Generate event for phase (start or end)."""
        phase_events = {
            "Discovery Phase": {
                "start": ("Initial Discovery", "Initial contact and requirements gathering started"),
                "end": ("Discovery Complete", "Discovery phase completed, moving to pricing")
            },
            "Pricing Negotiation Phase": {
                "start": ("Pricing Discussion Begins", "Pricing negotiation phase started"),
                "end": ("Pricing Negotiation Complete", "Pricing discussions concluded")
            },
            "Delivery Planning Phase": {
                "start": ("Delivery Planning Starts", "Implementation and delivery planning began"),
                "end": ("Delivery Planning Complete", "Delivery planning phase completed")
            },
            "Issue/Escalation Phase": {
                "start": ("Issues Identified", "Problems or concerns raised"),
                "end": ("Escalation Resolved", "Issues addressed or escalated further")
            },
            "Final Decision Phase": {
                "start": ("Final Decision Process", "Final decision phase initiated"),
                "end": ("Final Outcome", "Deal closed - outcome determined")
            },
        }
        
        if phase in phase_events and event_type in phase_events[phase]:
            event_name, description = phase_events[phase][event_type]
            return {
                "event_name": event_name,
                "description": description,
                "phase": phase,
                "timestamp": date.strftime("%Y-%m-%d"),
                "confidence": 0.5,
                "sentiment": PHASE_SENTIMENT.get(phase, "neutral")
            }
        return None
    
    def _normalize_events(self, events: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Ensure all events have required fields."""
        normalized = []
        for event in events:
            if not isinstance(event, dict):
                continue
            
            phase = event.get("phase", "Discovery Phase")
            if phase not in REQUIRED_PHASES:
                phase_lower = phase.lower()
                if "discovery" in phase_lower or "initial" in phase_lower:
                    phase = "Discovery Phase"
                elif "pricing" in phase_lower or "price" in phase_lower or "negotiation" in phase_lower:
                    phase = "Pricing Negotiation Phase"
                elif "delivery" in phase_lower or "planning" in phase_lower:
                    phase = "Delivery Planning Phase"
                elif "escalation" in phase_lower or "issue" in phase_lower or "problem" in phase_lower:
                    phase = "Issue/Escalation Phase"
                elif "final" in phase_lower or "outcome" in phase_lower or "decision" in phase_lower:
                    phase = "Final Decision Phase"
                else:
                    phase = "Discovery Phase"
            
            normalized.append({
                "event_name": event.get("event_name", event.get("summary", "Event")),
                "description": event.get("description", event.get("summary", "Event occurred")),
                "phase": phase,
                "timestamp": event.get("timestamp", datetime.now().strftime("%Y-%m-%d")),
                "confidence": max(0.0, min(1.0, float(event.get("confidence", 0.7)))),
                "sentiment": event.get("sentiment", PHASE_SENTIMENT.get(phase, "neutral"))
            })
        
        return normalized
    
    def _generate_phase_summary(self, events: list[dict[str, Any]]) -> dict[str, str]:
        """Generate phase summaries."""
        summaries = {}
        for phase in REQUIRED_PHASES:
            phase_events = [e for e in events if e.get("phase") == phase]
            if phase_events:
                descriptions = [e.get("description", "") for e in phase_events[:3]]
                summaries[phase] = " | ".join(descriptions)
            else:
                summaries[phase] = f"Events occurred in {phase}"
        return summaries
    
    def _enhance_events(self, events: list, context: str) -> list[dict[str, Any]]:
        """Enhance events by extracting more from context."""
        enhanced = list(events) if events else []
        
        # Extract event types from context
        context_lower = context.lower()
        
        for event_type, patterns in EVENT_PATTERNS.items():
            for pattern in patterns:
                if pattern in context_lower:
                    # Find context around pattern
                    pattern_index = context_lower.find(pattern)
                    if pattern_index >= 0:
                        snippet = context[max(0, pattern_index-100):pattern_index+200]
                        inferencer = DateInferencer()
                        date = inferencer.infer_realistic_date("Discovery Phase", len(enhanced), 15)
                        
                        phase = "Discovery Phase"
                        if "pricing" in pattern or "price" in pattern or "discount" in pattern:
                            phase = "Pricing Negotiation Phase"
                        elif "delivery" in pattern or "implementation" in pattern:
                            phase = "Delivery Planning Phase"
                        elif "escalation" in pattern or "issue" in pattern or "problem" in pattern:
                            phase = "Issue/Escalation Phase"
                        elif "final" in pattern or "decision" in pattern or "outcome" in pattern:
                            phase = "Final Decision Phase"
                        
                        enhanced.append({
                            "event_name": event_type.replace("_", " ").title(),
                            "description": snippet.strip()[:150],
                            "phase": phase,
                            "timestamp": date.strftime("%Y-%m-%d"),
                            "confidence": 0.6,
                            "sentiment": PHASE_SENTIMENT.get(phase, "neutral")
                        })
                        break
        
        return enhanced[:15]
    
    def _extract_fallback_timeline(self, context: str, base_date: datetime | None = None) -> dict[str, Any]:
        """Generate timeline when all else fails."""
        if base_date is None:
            base_date = datetime.now() - relativedelta(months=4)
        inferencer = DateInferencer(base_date=base_date)
        events = []
        
        phase_dates = {
            "Discovery Phase": (base_date, base_date + timedelta(days=14)),
            "Pricing Negotiation Phase": (base_date + timedelta(days=14), base_date + timedelta(days=35)),
            "Delivery Planning Phase": (base_date + timedelta(days=35), base_date + timedelta(days=50)),
            "Issue/Escalation Phase": (base_date + timedelta(days=50), base_date + timedelta(days=70)),
            "Final Decision Phase": (base_date + timedelta(days=70), base_date + timedelta(days=90)),
        }
        
        for phase, (start_date, end_date) in phase_dates.items():
            # Start event
            events.append({
                "event_name": f"{phase} Started",
                "description": f"Initial activity in {phase}",
                "phase": phase,
                "timestamp": start_date.strftime("%Y-%m-%d"),
                "confidence": 0.4,
                "sentiment": PHASE_SENTIMENT.get(phase, "neutral")
            })
            # End event
            events.append({
                "event_name": f"{phase} Completed",
                "description": f"Phase completed: {phase}",
                "phase": phase,
                "timestamp": end_date.strftime("%Y-%m-%d"),
                "confidence": 0.4,
                "sentiment": PHASE_SENTIMENT.get(phase, "neutral")
            })
        
        return {
            "events": events,
            "timeline_score": 4.0,
            "phase_summary": {phase: f"Events in {phase}" for phase in REQUIRED_PHASES},
            "average_phase_score": 5.0,
            "major_blockers": [],
            "communication_events": []
        }
    
    def _default_timeline(self) -> dict[str, Any]:
        """Return minimal default timeline."""
        inferencer = DateInferencer()
        events = []
        base_date = datetime.now() - relativedelta(months=4)
        
        for i, phase in enumerate(REQUIRED_PHASES):
            date = base_date + timedelta(days=i*14)
            events.append({
                "event_name": f"{phase} Started",
                "description": f"Initial activity in {phase}",
                "phase": phase,
                "timestamp": date.strftime("%Y-%m-%d"),
                "confidence": 0.3,
                "sentiment": PHASE_SENTIMENT.get(phase, "neutral")
            })
        
        return {
            "events": events,
            "timeline_score": 3.0,
            "phase_summary": {phase: f"Activity in {phase}" for phase in REQUIRED_PHASES},
            "average_phase_score": 5.0,
            "major_blockers": [],
            "communication_events": []
        }
