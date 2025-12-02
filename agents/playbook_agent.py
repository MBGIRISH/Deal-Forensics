"""
Playbook Agent: Generates highly actionable remediation guidance and recovery playbooks.

This agent produces four critical sections:
1. What Went Wrong (Root Causes) - 6-10 specific points
2. Red Flags (Warning Signs) - 6-10 strong warnings
3. Recommendations (Short-Term Action Plan) - 8-12 actionable steps
4. Best Practices (Long-Term Improvements) - 6-10 long-term improvements

All insights are document-specific and based on actual deal content.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
import json
import re

from agents.base import BaseAgent
from core.gemini_client import generate_json


PROMPT_TEMPLATE = """
You are an expert revenue operations strategist and sales excellence consultant with deep experience in deal post-mortems.

CRITICAL: You MUST analyze the ACTUAL DEAL DOCUMENT below and generate document-specific insights. DO NOT use generic responses.

Your task: Analyze THIS SPECIFIC deal failure and create a HIGHLY ACTIONABLE recovery playbook based on what actually happened in THIS deal.

DEAL DOCUMENT CONTENT:
{raw_document}

TIMELINE ANALYSIS:
{timeline}

COMPARATIVE INSIGHTS:
{comparative}

DEAL SUMMARY:
{deal_summary}

CRITICAL REQUIREMENTS - Analyze the document above and produce:

1. WHAT WENT WRONG (Root Causes) - Output EXACTLY 6-10 specific points based on THIS deal:
   - Extract specific issues from the document: pricing renegotiations, communication breakdowns, delivery delays, competitor mentions
   - Look for explicit problems: "pricing gap", "delayed response", "competitor mentioned", "delivery delay", "missing documentation"
   - Detect implicit problems: If pricing was discussed multiple times, that's pricing ambiguity. If dates are vague, that's timeline issues.
   - Be SPECIFIC to THIS deal: Mention actual amounts, dates, competitors, or specific issues from the document
   - Examples from document: "Pricing was renegotiated from $520K to $420K indicating unclear initial requirements", "Competitor CloudTech Solutions offered 10% lower price", "Delivery timeline changed from 6 months to 4 months causing resource conflicts"
   - Format: List of 6-10 specific, actionable root cause statements

2. RED FLAGS (Warning Signs) - Output EXACTLY 6-10 strong warnings from THIS deal:
   - Extract from document: "verbal agreement", "customer said", "to be determined", "we'll discuss later", "no written confirmation"
   - Look for: Discounts mentioned verbally, vague timelines ("Q2", "sometime"), missing warranty terms, undefined penalties
   - Be SPECIFIC: "Red flag: Discount of $50K mentioned verbally on March 15 without written confirmation", "Timeline mentioned as 'Q2' without specific date"
   - Format: List of 6-10 specific warning signs detected in THIS deal

3. RECOMMENDATIONS (Short-Term Action Plan) - Output EXACTLY 8-12 actionable improvements:
   - Base recommendations on ACTUAL issues found in THIS deal
   - If pricing was an issue: "Send written pricing summary within 24 hours of each pricing discussion to prevent renegotiations"
   - If competitor was mentioned: "Create competitive differentiation matrix and share early in sales cycle to address competitor CloudTech Solutions"
   - If delivery was delayed: "Define delivery timeline with penalty clauses for delays to prevent timeline changes"
   - Each recommendation should address a SPECIFIC issue from THIS deal
   - Format: List of 8-12 specific action items with priority (High/Med/Low), impact (1-10), and owner

4. BEST PRACTICES (Long-Term Improvements) - Output EXACTLY 6-10 long-term process improvements:
   - Base on patterns found in THIS deal
   - If verbal agreements were an issue: "Require written confirmation for all verbal agreements within 24 hours"
   - If pricing ambiguity: "Implement budget qualification checklist in discovery phase"
   - If competitor pressure: "Establish competitor intelligence gathering process for deals over $200K"
   - Format: List of 6-10 best practice recommendations

Return JSON with these EXACT keys:
{{
  "what_went_wrong": ["specific root cause 1 from document", "specific root cause 2 from document", ...],  // EXACTLY 6-10 items
  "red_flags": ["specific red flag 1 from document", "specific red flag 2 from document", ...],  // EXACTLY 6-10 items
  "recommendations": [
    {{"priority": "High/Med/Low", "action": "specific action addressing document issue", "impact": 1-10, "owner": "Sales Rep/Sales Manager/Product Team"}},
    ...
  ],  // EXACTLY 8-12 items
  "best_practices": ["best practice 1", "best practice 2", ...]  // EXACTLY 6-10 items
}}

REMEMBER: All insights MUST be based on the actual deal document content above. Be specific, not generic.
""".strip()


@dataclass
class PlaybookAgent(BaseAgent):
    """
    Agent that generates comprehensive recovery playbooks with document-specific insights.
    
    Produces four critical sections with specific, deal-aware recommendations based on actual document content.
    """

    def analyze(
        self, deal_summary: str, timeline: dict[str, Any], comparative: dict[str, Any], raw_document: str = ""
    ) -> dict[str, Any]:
        """
        Generate comprehensive recovery playbook from deal analysis.
        
        Args:
            deal_summary: Summary of the deal
            timeline: Timeline analysis from Timeline Agent
            comparative: Comparative analysis from Comparative Agent
            raw_document: Raw document text for document-specific analysis
            
        Returns:
            Dictionary with:
            - what_went_wrong: List of 6-10 root cause statements
            - red_flags: List of 6-10 warning signs
            - recommendations: List of 8-12 prioritized action items
            - best_practices: List of 6-10 process improvements
        """
        # Extract document-specific insights FIRST
        doc_insights = self._extract_document_insights(raw_document)
        
        prompt = PROMPT_TEMPLATE.format(
            raw_document=raw_document[:6000] if raw_document else deal_summary[:3000],
            deal_summary=deal_summary[:2000],
            timeline=json.dumps(timeline, ensure_ascii=False)[:4000],
            comparative=json.dumps(comparative, ensure_ascii=False)[:4000],
        )
        
        try:
            result = generate_json(prompt)
            
            if not isinstance(result, dict):
                result = {}
            
            # ========== WHAT WENT WRONG (6-10 items) ==========
            what_went_wrong = result.get("what_went_wrong", [])
            if not isinstance(what_went_wrong, list):
                what_went_wrong = []
            
            # Add document-specific insights
            what_went_wrong.extend(doc_insights.get("what_went_wrong", []))
            
            # Ensure we have AT LEAST 6 items
            while len(what_went_wrong) < 6:
                additional = self._generate_additional_root_causes(timeline, comparative, raw_document)
                what_went_wrong.extend(additional)
                if not additional:  # If no more can be generated, use defaults
                    break
            
            # Fill to minimum if still not enough
            if len(what_went_wrong) < 6:
                what_went_wrong.extend(self._get_default_what_went_wrong()[:6-len(what_went_wrong)])
            
            result["what_went_wrong"] = list(dict.fromkeys(what_went_wrong))[:10]  # Remove duplicates, limit to 10
            
            # ========== RED FLAGS (6-10 items) ==========
            red_flags = result.get("red_flags", [])
            if not isinstance(red_flags, list):
                red_flags = []
            
            # Add document-specific red flags
            red_flags.extend(doc_insights.get("red_flags", []))
            
            # Ensure we have AT LEAST 6 items
            while len(red_flags) < 6:
                additional = self._generate_additional_red_flags(timeline, comparative, raw_document)
                red_flags.extend(additional)
                if not additional:
                    break
            
            # Fill to minimum if still not enough
            if len(red_flags) < 6:
                red_flags.extend(self._get_default_red_flags()[:6-len(red_flags)])
            
            result["red_flags"] = list(dict.fromkeys(red_flags))[:10]
            
            # ========== RECOMMENDATIONS (8-12 items) ==========
            recommendations = result.get("recommendations", [])
            if not isinstance(recommendations, list):
                recommendations = []
            
            # Add document-specific recommendations
            recommendations.extend(doc_insights.get("recommendations", []))
            
            # Ensure we have AT LEAST 8 items
            while len(recommendations) < 8:
                additional = self._generate_additional_recommendations(timeline, comparative, raw_document)
                recommendations.extend(additional)
                if not additional:
                    break
            
            # Fill to minimum if still not enough
            if len(recommendations) < 8:
                recommendations.extend(self._get_default_recommendations()[:8-len(recommendations)])
            
            # Validate all recommendations have required fields
            validated_recs = []
            for rec in recommendations[:12]:
                if isinstance(rec, dict):
                    validated_recs.append({
                        "priority": rec.get("priority", "Med"),
                        "action": rec.get("action", "Review deal process"),
                        "impact": int(rec.get("impact", 5)),
                        "owner": rec.get("owner", "Sales Rep")
                    })
                elif isinstance(rec, str):
                    validated_recs.append({
                        "priority": "Med",
                        "action": rec,
                        "impact": 6,
                        "owner": "Sales Rep"
                    })
            
            result["recommendations"] = validated_recs[:12]
            
            # ========== BEST PRACTICES (6-10 items) ==========
            best_practices = result.get("best_practices", [])
            if not isinstance(best_practices, list):
                best_practices = []
            
            # Add document-specific best practices
            best_practices.extend(doc_insights.get("best_practices", []))
            
            # Ensure we have AT LEAST 6 items
            while len(best_practices) < 6:
                additional = self._generate_additional_best_practices(raw_document)
                best_practices.extend(additional)
                if not additional:
                    break
            
            # Fill to minimum if still not enough
            if len(best_practices) < 6:
                best_practices.extend(self._get_default_best_practices()[:6-len(best_practices)])
            
            result["best_practices"] = list(dict.fromkeys(best_practices))[:10]
            
            return result
            
        except Exception as e:
            # Return document-specific fallback
            return self._generate_document_specific_playbook(timeline, comparative, raw_document)
    
    def _extract_document_insights(self, document: str) -> dict[str, Any]:
        """
        Extract document-specific insights from raw document text.
        
        Args:
            document: Raw document text
            
        Returns:
            Dictionary with extracted insights
        """
        if not document:
            return {}
        
        doc_lower = document.lower()
        insights = {
            "what_went_wrong": [],
            "red_flags": [],
            "recommendations": [],
            "best_practices": []
        }
        
        # Extract pricing issues
        pricing_mentions = len(re.findall(r"\bpricing\b|\bprice\b|\bbudget\b|\bcost\b", doc_lower))
        if pricing_mentions > 2:
            # Extract specific pricing amounts
            price_matches = re.findall(r"\$[\d,]+|\d+[\d,]*\s*(?:k|thousand|million)", document, re.IGNORECASE)
            price_context = ""
            if price_matches:
                price_context = f" (pricing discussed: {', '.join(price_matches[:3])})"
            
            insights["what_went_wrong"].append(f"Pricing was discussed {pricing_mentions} times indicating unclear initial pricing requirements{price_context}")
            insights["red_flags"].append("Multiple pricing discussions without written confirmation")
            insights["recommendations"].append({
                "priority": "High",
                "action": "Implement budget qualification checklist in discovery phase to avoid pricing renegotiations",
                "impact": 9,
                "owner": "Sales Rep"
            })
        
        # Extract pricing gap
        if "pricing gap" in doc_lower or "budget gap" in doc_lower:
            gap_match = re.search(r"gap[:\s]+(\$?[\d,]+|\d+%)", document, re.IGNORECASE)
            gap_info = f" ({gap_match.group(1)})" if gap_match else ""
            insights["what_went_wrong"].append(f"Significant pricing gap between proposal and customer budget{gap_info}")
            insights["red_flags"].append("Budget constraints not properly qualified early in sales cycle")
        
        # Extract competitor mentions (improved - more precise)
        competitor_patterns = [
            r"lost to ([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+){0,2})",  # Company name (1-3 words, capitalized)
            r"competitor[:\s]+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+){0,2})",  # More precise
            r"alternative vendor[:\s]+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+){0,2})",
            r"([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+){0,2})\s+(?:solutions|systems|technologies|corp|inc|llc|ltd)",
            r"([A-Z][a-zA-Z]+)\s+(?:solutions|systems|technologies)",  # Single word + solutions
        ]
        
        competitor_name = ""
        for pattern in competitor_patterns:
            match = re.search(pattern, document, re.IGNORECASE)
            if match:
                competitor_name = match.group(1).strip()
                # Clean up common words
                competitor_name = re.sub(r'\b(was|is|the|a|an|vendor|solution|company|due|to|pricing|concerns|and|delivery|timeline)\b', '', competitor_name, flags=re.IGNORECASE).strip()
                # Remove extra spaces
                competitor_name = re.sub(r'\s+', ' ', competitor_name).strip()
                # Limit to reasonable length (30 chars for company name)
                if 3 < len(competitor_name) <= 30:
                    break
                elif len(competitor_name) > 30:
                    # Take first 2 words if too long
                    words = competitor_name.split()[:2]
                    competitor_name = ' '.join(words)
                    if len(competitor_name) <= 30:
                        break
                    else:
                        competitor_name = ""
        
        if competitor_name or "competitor" in doc_lower:
            comp_name = competitor_name or "a competitor"
            insights["what_went_wrong"].append(f"Competitive pressure from {comp_name} not addressed early enough")
            insights["red_flags"].append(f"Competitor {comp_name} explicitly mentioned during negotiations")
            insights["recommendations"].append({
                "priority": "High",
                "action": f"Create competitive differentiation matrix to address {comp_name} early in sales cycle",
                "impact": 8,
                "owner": "Sales Manager"
            })
        
        # Extract delivery/timeline issues
        if "delay" in doc_lower or "timeline" in doc_lower or "delivery" in doc_lower:
            if "vague" in doc_lower or "tbd" in doc_lower or "flexible" in doc_lower or "q2" in doc_lower or "q3" in doc_lower:
                insights["what_went_wrong"].append("Vague delivery timeline expectations led to misalignment")
                insights["red_flags"].append("Delivery timeline mentioned without specific dates (e.g., 'Q2', 'flexible')")
                insights["recommendations"].append({
                    "priority": "Med",
                    "action": "Define delivery timeline with specific dates and penalty clauses",
                    "impact": 7,
                    "owner": "Sales Manager"
                })
            elif "delay" in doc_lower:
                delay_match = re.search(r"delay[ed]?\s+(?:of|for)?\s*(\d+\s*(?:days?|weeks?|months?))", doc_lower)
                delay_info = f" ({delay_match.group(1)})" if delay_match else ""
                insights["what_went_wrong"].append(f"Delivery delays occurred{delay_info}")
                insights["red_flags"].append("Timeline delays indicate poor planning or resource allocation")
        
        # Extract communication issues
        if "delayed response" in doc_lower or "no response" in doc_lower or "miscommunication" in doc_lower:
            insights["what_went_wrong"].append("Communication breakdown between sales and customer")
            insights["red_flags"].append("Delayed responses to critical questions")
            insights["recommendations"].append({
                "priority": "Med",
                "action": "Establish regular check-in cadence to prevent communication delays",
                "impact": 7,
                "owner": "Sales Rep"
            })
        
        # Extract documentation issues
        if "verbal" in doc_lower and ("agreement" in doc_lower or "commitment" in doc_lower or "discount" in doc_lower):
            insights["what_went_wrong"].append("Verbal-only commitments without written confirmation")
            insights["red_flags"].append("Verbal agreements without written follow-up")
            insights["recommendations"].append({
                "priority": "High",
                "action": "Require written confirmation for all verbal agreements within 24 hours",
                "impact": 8,
                "owner": "Sales Rep"
            })
        
        # Extract escalation issues
        if "escalation" in doc_lower or "escalated" in doc_lower:
            insights["what_went_wrong"].append("Multiple escalation phases indicate unresolved issues that should have been addressed earlier")
            insights["red_flags"].append("Issues escalated multiple times without resolution")
            insights["recommendations"].append({
                "priority": "Med",
                "action": "Establish clear escalation paths and resolution processes before issues arise",
                "impact": 7,
                "owner": "Sales Manager"
            })
        
        # Extract warranty/penalty issues
        if "warranty" not in doc_lower and "guarantee" not in doc_lower:
            insights["red_flags"].append("Missing warranty or guarantee terms in deal documentation")
            insights["recommendations"].append({
                "priority": "Med",
                "action": "Include warranty and guarantee terms in all proposals",
                "impact": 6,
                "owner": "Sales Manager"
            })
        
        if "penalty" not in doc_lower and "consequence" not in doc_lower:
            insights["red_flags"].append("No penalty clauses defined for delays or non-compliance")
            insights["recommendations"].append({
                "priority": "Med",
                "action": "Define penalty clauses for delays in all contracts",
                "impact": 6,
                "owner": "Sales Manager"
            })
        
        # Extract timeline/date issues
        vague_date_patterns = ["q1", "q2", "q3", "q4", "sometime", "flexible", "tbd", "to be determined"]
        if any(pattern in doc_lower for pattern in vague_date_patterns):
            insights["red_flags"].append("Vague timeline references instead of specific dates")
        
        return insights
    
    def _generate_additional_root_causes(self, timeline: dict, comparative: dict, raw_document: str = "") -> list[str]:
        """Generate additional root causes based on timeline, comparative data, and document."""
        causes = []
        
        # Check for pricing issues
        if comparative.get("pricing_delta", 0) > 0.5:
            causes.append("Significant pricing gap between proposal and customer budget indicates unclear requirements gathering")
        
        # Check for competitor issues
        if comparative.get("competitor_risk", 0) > 0.6:
            causes.append("High competitive pressure suggests insufficient differentiation or value communication")
        
        # Check timeline for delays
        events = timeline.get("events", [])
        if events:
            negative_events = [e for e in events if isinstance(e, dict) and e.get("sentiment") == "negative"]
            if len(negative_events) > len(events) * 0.4:
                causes.append("High proportion of negative sentiment events indicates communication or expectation misalignment")
        
        # Check for escalation issues
        escalation_phases = [e for e in events if isinstance(e, dict) and "escalation" in e.get("phase", "").lower()]
        if escalation_phases:
            causes.append("Multiple escalation phases indicate unresolved issues that should have been addressed earlier")
        
        # Document-specific checks
        if raw_document:
            doc_lower = raw_document.lower()
            if "warranty" not in doc_lower and "guarantee" not in doc_lower:
                causes.append("Missing warranty or guarantee terms in deal documentation")
            if "penalty" not in doc_lower and "consequence" not in doc_lower:
                causes.append("No penalty clauses defined for delays or non-compliance")
            if "written" not in doc_lower or "documented" not in doc_lower:
                causes.append("Insufficient written documentation throughout the deal process")
        
        return causes
    
    def _generate_additional_red_flags(self, timeline: dict, comparative: dict, raw_document: str = "") -> list[str]:
        """Generate additional red flags based on analysis."""
        flags = []
        
        # Check for vague timelines
        events = timeline.get("events", [])
        if events:
            vague_timestamps = [e for e in events if isinstance(e, dict) and ("week" in str(e.get("timestamp", "")).lower() or "month" in str(e.get("timestamp", "")).lower())]
            if vague_timestamps:
                flags.append("Vague timeline references (weeks/months) instead of specific dates indicate planning uncertainty")
        
        # Check for pricing negotiations
        pricing_events = [e for e in events if isinstance(e, dict) and "pricing" in e.get("phase", "").lower()]
        if len(pricing_events) > 2:
            flags.append("Multiple pricing discussions indicate unclear initial pricing or scope creep")
        
        # Check communication quality
        comm_events = timeline.get("communication_events", [])
        if comm_events:
            negative_comm = [c for c in comm_events if isinstance(c, dict) and c.get("sentiment") == "negative"]
            if len(negative_comm) > len(comm_events) * 0.3:
                flags.append("High proportion of negative communication events suggests relationship deterioration")
        
        # Document-specific checks
        if raw_document:
            doc_lower = raw_document.lower()
            if "customer said" in doc_lower or "customer mentioned" in doc_lower:
                flags.append("Key information only mentioned verbally without written confirmation")
            if "tbd" in doc_lower or "to be determined" in doc_lower:
                flags.append("Multiple 'to be determined' items indicate incomplete planning")
            if "discount" in doc_lower and "verbal" in doc_lower:
                flags.append("Discounts mentioned verbally without written confirmation")
        
        return flags
    
    def _generate_additional_recommendations(self, timeline: dict, comparative: dict, raw_document: str = "") -> list[dict]:
        """Generate additional recommendations based on analysis."""
        recs = []
        
        if comparative.get("pricing_delta", 0) > 0.5:
            recs.append({
                "priority": "High",
                "action": "Implement budget qualification checklist in discovery phase",
                "impact": 9,
                "owner": "Sales Rep"
            })
        
        if comparative.get("competitor_risk", 0) > 0.6:
            recs.append({
                "priority": "High",
                "action": "Create competitive differentiation matrix and share early in sales cycle",
                "impact": 8,
                "owner": "Sales Manager"
            })
        
        events = timeline.get("events", [])
        if events:
            negative_count = len([e for e in events if isinstance(e, dict) and e.get("sentiment") == "negative"])
            if negative_count > 3:
                recs.append({
                    "priority": "Med",
                    "action": "Establish regular check-in cadence to catch issues early",
                    "impact": 7,
                    "owner": "Sales Rep"
                })
        
        # Document-specific recommendations
        if raw_document:
            doc_lower = raw_document.lower()
            if "discount" in doc_lower and "verbal" in doc_lower:
                recs.append({
                    "priority": "High",
                    "action": "Require written confirmation for all discount discussions",
                    "impact": 8,
                    "owner": "Sales Rep"
                })
            if "timeline" in doc_lower and ("vague" in doc_lower or "tbd" in doc_lower):
                recs.append({
                    "priority": "Med",
                    "action": "Define specific delivery dates with penalty clauses",
                    "impact": 7,
                    "owner": "Sales Manager"
                })
        
        return recs
    
    def _generate_additional_best_practices(self, raw_document: str = "") -> list[str]:
        """Generate additional best practices."""
        practices = [
            "Document all pricing discussions in CRM within 24 hours",
            "Require written confirmation for all verbal agreements",
            "Establish clear escalation paths before issues arise",
            "Conduct weekly deal reviews for deals over $200K",
            "Implement automated deal health scoring and alerts",
            "Create competitive battle cards for common competitors",
            "Establish standard pricing approval workflows",
            "Require technical validation before pricing commitment"
        ]
        
        # Add document-specific practices
        if raw_document:
            doc_lower = raw_document.lower()
            if "warranty" not in doc_lower:
                practices.append("Include warranty and guarantee terms in all proposals")
            if "penalty" not in doc_lower:
                practices.append("Define penalty clauses for delays in all contracts")
            if "crm" not in doc_lower:
                practices.append("Use CRM to track all deal communications and agreements")
        
        return practices
    
    def _get_default_what_went_wrong(self) -> list[str]:
        """Get default what went wrong items."""
        return [
            "Pricing ambiguity led to multiple renegotiations",
            "Communication breakdown between sales and customer",
            "Competitive pressure not addressed early enough",
            "Delivery timeline expectations were misaligned",
            "Missing written confirmations for key agreements",
            "Budget qualification occurred too late in sales cycle",
            "Technical requirements not fully understood before pricing",
            "Executive sponsorship was not secured early enough",
            "Insufficient competitive differentiation communicated",
            "Timeline delays caused resource conflicts"
        ]
    
    def _get_default_red_flags(self) -> list[str]:
        """Get default red flags."""
        return [
            "Multiple pricing discussions without written confirmation",
            "Vague timeline references instead of specific dates",
            "Customer mentioned evaluating alternatives",
            "Delayed responses to critical questions",
            "No documented approval process visible",
            "Verbal agreements without written follow-up",
            "Pricing negotiations stalled multiple times",
            "Competitor explicitly mentioned during negotiations",
            "Discounts mentioned verbally without confirmation",
            "Missing warranty or penalty clauses in documentation"
        ]
    
    def _get_default_recommendations(self) -> list[dict]:
        """Get default recommendations."""
        return [
            {"priority": "High", "action": "Implement budget qualification in discovery phase", "impact": 9, "owner": "Sales Rep"},
            {"priority": "High", "action": "Send written summary after each pricing discussion", "impact": 8, "owner": "Sales Rep"},
            {"priority": "High", "action": "Create competitive differentiation matrix", "impact": 8, "owner": "Sales Manager"},
            {"priority": "High", "action": "Establish executive sponsorship early in sales cycle", "impact": 8, "owner": "Sales Manager"},
            {"priority": "Med", "action": "Establish regular check-in cadence", "impact": 7, "owner": "Sales Rep"},
            {"priority": "Med", "action": "Define warranty and penalty clauses early", "impact": 7, "owner": "Sales Manager"},
            {"priority": "Med", "action": "Conduct technical validation before pricing commitment", "impact": 7, "owner": "Sales Engineer"},
            {"priority": "Low", "action": "Document all verbal agreements in CRM", "impact": 6, "owner": "Sales Rep"},
            {"priority": "Low", "action": "Create deal review checklist for high-value opportunities", "impact": 6, "owner": "Sales Manager"},
            {"priority": "Low", "action": "Require written confirmation for all discount discussions", "impact": 6, "owner": "Sales Rep"}
        ]
    
    def _get_default_best_practices(self) -> list[str]:
        """Get default best practices."""
        return [
            "Use CRM to track all deal communications and agreements",
            "Create standard contract templates with warranty clauses",
            "Establish documented approval flows for pricing exceptions",
            "Conduct regular deal reviews for high-value opportunities",
            "Reduce reliance on verbal commitments",
            "Implement early warning system for at-risk deals",
            "Require technical validation before pricing commitment",
            "Establish competitive intelligence gathering process",
            "Define penalty clauses for delays in all contracts",
            "Require written confirmation for all verbal agreements within 24 hours"
        ]
    
    def _generate_document_specific_playbook(self, timeline: dict, comparative: dict, raw_document: str) -> dict[str, Any]:
        """Generate document-specific playbook when LLM fails."""
        # Extract insights from document
        doc_insights = self._extract_document_insights(raw_document)
        
        # Build playbook from extracted insights
        what_went_wrong = doc_insights.get("what_went_wrong", [])
        what_went_wrong.extend(self._generate_additional_root_causes(timeline, comparative, raw_document))
        what_went_wrong.extend(self._get_default_what_went_wrong())
        
        red_flags = doc_insights.get("red_flags", [])
        red_flags.extend(self._generate_additional_red_flags(timeline, comparative, raw_document))
        red_flags.extend(self._get_default_red_flags())
        
        recommendations = doc_insights.get("recommendations", [])
        recommendations.extend(self._generate_additional_recommendations(timeline, comparative, raw_document))
        recommendations.extend(self._get_default_recommendations())
        
        best_practices = doc_insights.get("best_practices", [])
        best_practices.extend(self._generate_additional_best_practices(raw_document))
        best_practices.extend(self._get_default_best_practices())
        
        # Remove duplicates and ensure correct counts
        return {
            "what_went_wrong": list(dict.fromkeys(what_went_wrong))[:10],
            "red_flags": list(dict.fromkeys(red_flags))[:10],
            "recommendations": recommendations[:12],
            "best_practices": list(dict.fromkeys(best_practices))[:10]
        }
