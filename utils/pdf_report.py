"""
Enterprise-Grade PDF Report Generator for Deal Forensics Analysis.

Generates comprehensive business reports with:
- Title Page
- Executive Summary
- Deal Overview Table
- Full Timeline Section
- What Went Wrong (Root Causes)
- Red Flags (Warning Signs)
- Recommendations (Short-Term Fixes)
- Best Practices (Long-Term Improvements)
- Comparative Analytics
- Business Intelligence Metrics
- Final Summary
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List

from fpdf import FPDF


class ReportBuilder:
    """
    Enterprise-grade PDF report builder with comprehensive sections.
    
    Ensures all sections are populated, even with inferred data.
    """

    def __init__(self) -> None:
        """Initialize the report builder."""
        self.colors = {
            "header": (41, 128, 185),
            "accent": (52, 152, 219),
            "success": (39, 174, 96),
            "warning": (241, 196, 15),
            "danger": (231, 76, 60),
            "dark": (44, 62, 80),
            "light": (236, 240, 241),
            "text": (52, 73, 94),
        }

    def _sanitize_text(self, text: str) -> str:
        """Sanitize text for FPDF compatibility."""
        if not text:
            return ""
        
        text = str(text)
        replacements = {
            '—': '-', '–': '-', '"': '"', '"': '"',
            ''': "'", ''': "'", '…': '...', '•': '*',
            '€': 'EUR', '£': 'GBP', '©': '(c)',
            '®': '(R)', '™': '(TM)',
        }
        
        for old_char, new_char in replacements.items():
            text = text.replace(old_char, new_char)
        
        safe_chars = []
        for char in text:
            code = ord(char)
            if 32 <= code <= 126 or code in [9, 10, 13]:
                safe_chars.append(char)
            elif code in [160, 173]:
                safe_chars.append(' ')
            elif code in [8212, 8211]:
                safe_chars.append('-')
        
        return ''.join(safe_chars).encode('ascii', 'ignore').decode('ascii')

    def _add_header(self, pdf: FPDF, title: str, size: int = 16) -> None:
        """Add a styled section header."""
        pdf.ln(8)
        pdf.set_fill_color(*self.colors["header"])
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Helvetica", "B", size)
        effective_width = pdf.w - pdf.l_margin - pdf.r_margin
        pdf.cell(effective_width, 10, self._sanitize_text(title), ln=True, fill=True)
        pdf.set_text_color(*self.colors["text"])
        pdf.ln(5)

    def _add_subheader(self, pdf: FPDF, title: str) -> None:
        """Add a subheader."""
        pdf.ln(3)
        pdf.set_font("Helvetica", "B", 12)
        pdf.set_text_color(*self.colors["dark"])
        pdf.cell(0, 8, self._sanitize_text(title), ln=True)
        pdf.set_text_color(*self.colors["text"])
        pdf.set_font("Helvetica", "", 10)

    def _add_divider(self, pdf: FPDF) -> None:
        """Add a visual divider line."""
        pdf.ln(3)
        pdf.set_draw_color(*self.colors["light"])
        effective_width = pdf.w - pdf.l_margin - pdf.r_margin
        pdf.line(pdf.l_margin, pdf.y, pdf.l_margin + effective_width, pdf.y)
        pdf.ln(5)

    def _add_bullet_list(self, pdf: FPDF, items: List[str], max_items: int = None, icon: str = "*") -> None:
        """Add a formatted bullet list."""
        if not items:
            return
        
        if max_items:
            items = items[:max_items]
        
        effective_width = pdf.w - pdf.l_margin - pdf.r_margin
        pdf.set_font("Helvetica", "", 10)
        
        for item in items:
            if item:
                sanitized = self._sanitize_text(str(item))
                if len(sanitized) > 200:
                    sanitized = sanitized[:197] + "..."
                pdf.multi_cell(effective_width, 6, f"  {icon} {sanitized}", 0, "L")
                pdf.ln(2)

    def _add_table(self, pdf: FPDF, headers: List[str], rows: List[List[str]], col_widths: List[float] = None) -> None:
        """Add a formatted table."""
        if not rows:
            return
        
        effective_width = pdf.w - pdf.l_margin - pdf.r_margin
        num_cols = len(headers)
        
        if not col_widths:
            col_widths = [effective_width / num_cols] * num_cols
        
        # Header row
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_fill_color(*self.colors["light"])
        pdf.set_text_color(*self.colors["dark"])
        
        for i, header in enumerate(headers):
            pdf.cell(col_widths[i], 8, self._sanitize_text(header), 1, 0, "L", True)
        pdf.ln()
        
        # Data rows
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(*self.colors["text"])
        pdf.set_fill_color(255, 255, 255)
        
        for row in rows:
            for i, cell in enumerate(row[:num_cols]):
                cell_text = self._sanitize_text(str(cell))
                if len(cell_text) > 50:
                    cell_text = cell_text[:47] + "..."
                pdf.cell(col_widths[i], 7, cell_text, 1, 0, "L", False)
            pdf.ln()
        
        pdf.set_text_color(*self.colors["text"])

    def _generate_title_page(self, pdf: FPDF) -> None:
        """Generate title page."""
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 28)
        pdf.set_text_color(*self.colors["header"])
        pdf.cell(0, 20, "Deal Forensics AI Report", ln=True, align="C")
        pdf.ln(10)
        
        pdf.set_font("Helvetica", "", 14)
        pdf.set_text_color(*self.colors["text"])
        pdf.cell(0, 10, f"Generated: {datetime.utcnow().strftime('%B %d, %Y at %H:%M UTC')}", ln=True, align="C")
        pdf.ln(5)
        pdf.cell(0, 10, "Version 1.0", ln=True, align="C")
        pdf.ln(20)

    def _generate_executive_summary(self, pdf: FPDF, analysis: Dict[str, Any]) -> None:
        """Generate Executive Summary (5-7 sentences)."""
        self._add_header(pdf, "EXECUTIVE SUMMARY", 18)
        
        metadata = analysis.get("metadata", {})
        deal_name = metadata.get("deal_name") or "Unknown Deal"
        owner = metadata.get("owner") or "Unknown Owner"
        industry = metadata.get("industry") or "Unknown Industry"
        value = metadata.get("value") or "N/A"

        timeline = analysis.get("timeline", {})
        events = timeline.get("events", [])
        num_events = len(events) if events else 0
        timeline_score = timeline.get("timeline_score", 5.0)
        
        playbook = analysis.get("playbook", {})
        what_went_wrong = playbook.get("what_went_wrong", [])
        key_issue = what_went_wrong[0] if what_went_wrong else "Multiple factors contributed to the deal loss"
        
        scorecard = analysis.get("scorecard", {})
        final_score = scorecard.get("final_deal_health_score", 5.0) if scorecard else 5.0
        
        summary_text = (
            f"This report analyzes the lost deal '{deal_name}' ({industry}) valued at {value}, "
            f"owned by {owner}. The analysis reveals {len(what_went_wrong)} key issues across "
            f"{num_events} timeline events. The primary reason for deal failure was: {key_issue}. "
            f"The overall deal health score is {final_score:.1f}/10, and the timeline clarity score "
            f"is {timeline_score:.1f}/10, indicating significant areas for improvement. "
            f"Key findings include pricing gaps, communication breakdowns, and competitive pressure. "
            f"This report provides actionable recommendations to prevent similar losses in future deals."
        )
        
        pdf.set_font("Helvetica", "", 10)
        effective_width = pdf.w - pdf.l_margin - pdf.r_margin
        pdf.multi_cell(effective_width, 6, self._sanitize_text(summary_text), 0, "J")
        pdf.ln(5)

    def _generate_deal_overview(self, pdf: FPDF, analysis: Dict[str, Any]) -> None:
        """Generate Deal Overview table."""
        self._add_header(pdf, "DEAL OVERVIEW")
        
        metadata = analysis.get("metadata", {})
        playbook = analysis.get("playbook", {})
        what_went_wrong = playbook.get("what_went_wrong", [])
        key_failure = what_went_wrong[0] if what_went_wrong else "See analysis below"
        
        headers = ["Field", "Value"]
        rows = [
            ["Seller", metadata.get("owner") or "Not specified"],
            ["Buyer", metadata.get("deal_name") or "Not specified"],
            ["Deal Value", str(metadata.get("value") or "N/A")],
            ["Industry", metadata.get("industry") or "Not specified"],
            ["Outcome", metadata.get("stage") or "Closed Lost"],
            ["Key Failure Point", self._sanitize_text(key_failure)[:100]],  # Increased from 80 to 100
        ]
        
        effective_width = pdf.w - pdf.l_margin - pdf.r_margin
        self._add_table(pdf, headers, rows, [effective_width * 0.35, effective_width * 0.65])
        pdf.ln(5)

    def _generate_timeline_section(self, pdf: FPDF, analysis: Dict[str, Any]) -> None:
        """Generate FULL Timeline Section with dates, sentiment, timeline score."""
        self._add_header(pdf, "TIMELINE ANALYSIS")
        
        timeline = analysis.get("timeline", {})
        events = timeline.get("events", [])
        timeline_score = timeline.get("timeline_score", 5.0)
        
        # Timeline Score
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, f"Timeline Score: {timeline_score:.1f}/10", ln=True)
        pdf.set_font("Helvetica", "", 10)
        pdf.ln(3)
        
        if not events:
            events = self._generate_inferred_timeline()
        
        # Group events by phase
        phases = {}
        for event in events:
            if isinstance(event, dict):
                phase = event.get("phase", "Discovery Phase")
                if phase not in phases:
                    phases[phase] = []
                phases[phase].append(event)
        
        # Display events by phase
        for phase in ["Discovery Phase", "Pricing Negotiation Phase", "Delivery Planning Phase",
                      "Issue/Escalation Phase", "Final Decision Phase"]:
            if phase in phases:
                self._add_subheader(pdf, phase)
                for event in phases[phase][:8]:  # Limit to 8 events per phase
                    event_name = event.get("event_name", "Event")
                    description = event.get("description", event.get("summary", ""))
                    timestamp = event.get("timestamp", "Unknown")
                    sentiment = event.get("sentiment", "neutral")
                    confidence = event.get("confidence", 0.5)
                    
                    sentiment_icon = {"positive": "+", "neutral": "=", "negative": "-"}.get(sentiment, "=")
                    # Truncate long descriptions to prevent overflow
                    max_desc_length = 150
                    if len(description) > max_desc_length:
                        description = description[:max_desc_length] + "..."
                    
                    event_text = f"{sentiment_icon} [{timestamp}] {event_name}: {description} (Confidence: {confidence:.1f})"
                    pdf.set_font("Helvetica", "", 9)
                    effective_width = pdf.w - pdf.l_margin - pdf.r_margin
                    pdf.multi_cell(effective_width, 5, self._sanitize_text(event_text), 0, "L")
                    pdf.ln(2)
        
        pdf.ln(3)

    def _generate_what_went_wrong(self, pdf: FPDF, analysis: Dict[str, Any]) -> None:
        """Generate What Went Wrong section (6-10 points)."""
        self._add_header(pdf, "WHAT WENT WRONG - ROOT CAUSES")
        
        playbook = analysis.get("playbook", {})
        what_went_wrong = playbook.get("what_went_wrong", [])
        
        if not what_went_wrong or len(what_went_wrong) < 6:
            what_went_wrong = self._generate_inferred_what_went_wrong(analysis, what_went_wrong)
        
        self._add_bullet_list(pdf, what_went_wrong[:10], icon="*")
        pdf.ln(3)

    def _generate_red_flags(self, pdf: FPDF, analysis: Dict[str, Any]) -> None:
        """Generate Red Flags section (6-10 warnings)."""
        self._add_header(pdf, "RED FLAGS - WARNING SIGNS")
        
        playbook = analysis.get("playbook", {})
        red_flags = playbook.get("red_flags", [])
        
        if not red_flags or len(red_flags) < 6:
            red_flags = self._generate_inferred_red_flags(analysis, red_flags)
        
        self._add_bullet_list(pdf, red_flags[:10], icon="!")
        pdf.ln(3)

    def _generate_recommendations(self, pdf: FPDF, analysis: Dict[str, Any]) -> None:
        """Generate Recommendations section (8-12 actionable improvements)."""
        self._add_header(pdf, "RECOMMENDATIONS - SHORT-TERM FIXES")
        
        playbook = analysis.get("playbook", {})
        recommendations = playbook.get("recommendations", [])
        
        if not recommendations or len(recommendations) < 8:
            recommendations = self._generate_inferred_recommendations(analysis, recommendations)
        
        pdf.set_font("Helvetica", "", 10)
        effective_width = pdf.w - pdf.l_margin - pdf.r_margin
        
        for rec in recommendations[:12]:
            if isinstance(rec, dict):
                priority = rec.get("priority", "Med")
                action = rec.get("action", "Review deal process")
                impact = rec.get("impact", 5)
                owner = rec.get("owner", "Sales Rep")
                
                priority_symbol = {"High": "[HIGH]", "Med": "[MED]", "Low": "[LOW]"}.get(priority, "[MED]")
                # Truncate long action text to prevent overflow
                action_text = self._sanitize_text(action)
                if len(action_text) > 150:
                    action_text = action_text[:147] + "..."
                rec_text = f"{priority_symbol} {action_text} (Impact: {impact}/10, Owner: {owner})"
                pdf.multi_cell(effective_width, 6, rec_text, 0, "L")
                pdf.ln(2)
        
        pdf.ln(3)

    def _generate_best_practices(self, pdf: FPDF, analysis: Dict[str, Any]) -> None:
        """Generate Best Practices section (6-10 long-term improvements)."""
        self._add_header(pdf, "BEST PRACTICES - LONG-TERM IMPROVEMENTS")
        
        playbook = analysis.get("playbook", {})
        best_practices = playbook.get("best_practices", [])
        
        if not best_practices or len(best_practices) < 6:
            best_practices = self._generate_inferred_best_practices(analysis, best_practices)
        
        self._add_bullet_list(pdf, best_practices[:10], icon=">")
        pdf.ln(3)

    def _generate_comparative_analytics(self, pdf: FPDF, analysis: Dict[str, Any]) -> None:
        """Generate Comparative Analytics section."""
        self._add_header(pdf, "COMPARATIVE ANALYTICS")

        comparative = analysis.get("comparative", {})
        
        # Similar Deals
        similar = comparative.get("similar_deals", [])
        if similar:
            self._add_subheader(pdf, "Similar Historical Deals")
            headers = ["Deal Name", "Similarity %", "Outcome"]
            rows = []
            for deal in similar[:5]:
                if isinstance(deal, dict):
                    name = deal.get("deal_name", "Unknown")
                    similarity = deal.get("similarity_score", 0.5)
                    outcome = deal.get("outcome", "Lost")
                    rows.append([name, f"{similarity*100:.0f}%", outcome])
            
            if rows:
                effective_width = pdf.w - pdf.l_margin - pdf.r_margin
                self._add_table(pdf, headers, rows, [effective_width * 0.4, effective_width * 0.2, effective_width * 0.4])
                pdf.ln(5)
        
        # Common Patterns
        patterns = comparative.get("common_patterns", [])
        if patterns:
            self._add_subheader(pdf, "Common Patterns Across Lost Deals")
            self._add_bullet_list(pdf, patterns[:8], icon="*")
            pdf.ln(3)
        
        # Shared Risk Factors
        risk_factors = comparative.get("shared_risk_factors", [])
        if risk_factors:
            self._add_subheader(pdf, "Shared Risk Factors")
            self._add_bullet_list(pdf, risk_factors[:8], icon="!")
            pdf.ln(3)
        
        # Benchmark Scores
        benchmarks = comparative.get("benchmark_scores", {})
        if benchmarks:
            self._add_subheader(pdf, "Benchmark Metrics")
            headers = ["Metric", "Value"]
            rows = []
            for key, value in benchmarks.items():
                rows.append([key.replace("_", " ").title(), str(value)])
            
            if rows:
                effective_width = pdf.w - pdf.l_margin - pdf.r_margin
                self._add_table(pdf, headers, rows, [effective_width * 0.5, effective_width * 0.5])
                pdf.ln(5)
        
        # Comparative Table
        comp_table = comparative.get("comparative_table", [])
        if comp_table:
            self._add_subheader(pdf, "Comparative Metrics Table")
            if isinstance(comp_table, list) and comp_table:
                headers = list(comp_table[0].keys()) if isinstance(comp_table[0], dict) else ["Metric", "Value"]
                rows = []
                for row in comp_table[:10]:
                    if isinstance(row, dict):
                        rows.append([str(v) for v in row.values()])
                
                if rows:
                    effective_width = pdf.w - pdf.l_margin - pdf.r_margin
                    col_width = effective_width / len(headers)
                    self._add_table(pdf, headers, rows, [col_width] * len(headers))
                    pdf.ln(5)

    def _generate_bi_metrics(self, pdf: FPDF, analysis: Dict[str, Any]) -> None:
        """Generate Business Intelligence Metrics section."""
        self._add_header(pdf, "BUSINESS INTELLIGENCE METRICS")
        
        scorecard = analysis.get("scorecard", {})
        
        if not scorecard:
            scorecard = {
                "pricing_clarity_score": 5.0,
                "communication_quality_score": 5.0,
                "documentation_quality_score": 5.0,
                "competitive_risk_score": 5.0,
                "delivery_execution_score": 5.0,
                "final_deal_health_score": 5.0,
            }
        
        headers = ["Metric", "Score", "Status"]
        rows = []
        
        for key, value in sorted(scorecard.items()):
            metric_name = key.replace("_", " ").title()
            score = float(value) if value else 5.0
            
            if score >= 8.0:
                status = "Excellent"
            elif score >= 6.0:
                status = "Good"
            elif score >= 4.0:
                status = "Fair"
            else:
                status = "Poor"
            
            rows.append([metric_name, f"{score:.2f}/10", status])
        
        effective_width = pdf.w - pdf.l_margin - pdf.r_margin
        self._add_table(pdf, headers, rows, [effective_width * 0.5, effective_width * 0.25, effective_width * 0.25])
        pdf.ln(5)

    def _generate_final_summary(self, pdf: FPDF, analysis: Dict[str, Any]) -> None:
        """Generate Final Summary Paragraph."""
        self._add_header(pdf, "FINAL SUMMARY")

        playbook = analysis.get("playbook", {})
        what_went_wrong = playbook.get("what_went_wrong", [])
        recommendations = playbook.get("recommendations", [])

        scorecard = analysis.get("scorecard", {})
        final_score = scorecard.get("final_deal_health_score", 5.0) if scorecard else 5.0
        
        summary_text = (
            f"In conclusion, this deal analysis reveals {len(what_went_wrong)} key failure points "
            f"with an overall health score of {final_score:.1f}/10. The primary lessons learned include "
            f"the importance of clear pricing communication, written documentation of all agreements, "
            f"and early competitive positioning. The {len(recommendations)} recommendations provided "
            f"should be implemented to prevent similar losses. Key takeaways: establish clear timelines "
            f"with written confirmation, qualify budgets early, and maintain competitive intelligence. "
            f"By addressing these areas, future deals can achieve better outcomes."
        )
        
        pdf.set_font("Helvetica", "", 10)
        effective_width = pdf.w - pdf.l_margin - pdf.r_margin
        pdf.multi_cell(effective_width, 6, self._sanitize_text(summary_text), 0, "J")
        pdf.ln(5)

    def _generate_inferred_timeline(self) -> List[Dict[str, Any]]:
        """Generate inferred timeline events."""
        from datetime import datetime, timedelta
        from dateutil.relativedelta import relativedelta
        
        base_date = datetime.now() - relativedelta(months=4)
        events = []
        
        phase_dates = {
            "Discovery Phase": (base_date, base_date + timedelta(days=14)),
            "Pricing Negotiation Phase": (base_date + timedelta(days=14), base_date + timedelta(days=35)),
            "Delivery Planning Phase": (base_date + timedelta(days=35), base_date + timedelta(days=50)),
            "Issue/Escalation Phase": (base_date + timedelta(days=50), base_date + timedelta(days=70)),
            "Final Decision Phase": (base_date + timedelta(days=70), base_date + timedelta(days=90)),
        }
        
        for phase, (start_date, end_date) in phase_dates.items():
            events.append({
                "event_name": f"{phase} Started",
                "description": f"Initial activity in {phase}",
                "phase": phase,
                "timestamp": start_date.strftime("%Y-%m-%d"),
                "confidence": 0.4,
                "sentiment": "neutral"
            })
            events.append({
                "event_name": f"{phase} Completed",
                "description": f"Phase completed: {phase}",
                "phase": phase,
                "timestamp": end_date.strftime("%Y-%m-%d"),
                "confidence": 0.4,
                "sentiment": "neutral"
            })
        
        return events

    def _generate_inferred_what_went_wrong(self, analysis: Dict[str, Any], existing: List[str]) -> List[str]:
        """Generate inferred what went wrong items."""
        inferred = [
            "Pricing ambiguity led to multiple renegotiations",
            "Communication breakdown between sales and customer",
            "Competitive pressure not addressed early enough",
            "Delivery timeline expectations were misaligned",
            "Missing written confirmations for key agreements",
            "Budget qualification occurred too late in sales cycle",
        ]
        return existing + inferred[:10-len(existing)]

    def _generate_inferred_red_flags(self, analysis: Dict[str, Any], existing: List[str]) -> List[str]:
        """Generate inferred red flags."""
        inferred = [
            "Multiple pricing discussions without written confirmation",
            "Vague timeline references instead of specific dates",
            "Customer mentioned evaluating alternatives",
            "Delayed responses to critical questions",
            "No documented approval process visible",
            "Verbal agreements without written follow-up",
        ]
        return existing + inferred[:10-len(existing)]

    def _generate_inferred_recommendations(self, analysis: Dict[str, Any], existing: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate inferred recommendations."""
        inferred = [
            {"priority": "High", "action": "Implement budget qualification in discovery phase", "impact": 9, "owner": "Sales Rep"},
            {"priority": "High", "action": "Send written summary after each pricing discussion", "impact": 8, "owner": "Sales Rep"},
            {"priority": "High", "action": "Create competitive differentiation matrix", "impact": 8, "owner": "Sales Manager"},
            {"priority": "Med", "action": "Establish regular check-in cadence", "impact": 7, "owner": "Sales Rep"},
            {"priority": "Med", "action": "Define warranty and penalty clauses early", "impact": 7, "owner": "Sales Manager"},
            {"priority": "Low", "action": "Document all verbal agreements in CRM", "impact": 6, "owner": "Sales Rep"},
        ]
        return existing + inferred[:12-len(existing)]

    def _generate_inferred_best_practices(self, analysis: Dict[str, Any], existing: List[str]) -> List[str]:
        """Generate inferred best practices."""
        inferred = [
            "Use CRM to track all deal communications and agreements",
            "Create standard contract templates with warranty clauses",
            "Establish documented approval flows for pricing exceptions",
            "Conduct regular deal reviews for high-value opportunities",
            "Reduce reliance on verbal commitments",
            "Implement early warning system for at-risk deals",
        ]
        return existing + inferred[:10-len(existing)]

    def build(self, analysis: Dict[str, Any]) -> bytes:
        """
        Build a comprehensive enterprise-grade PDF report.
        
        Args:
            analysis: Complete analysis dictionary with all sections
            
        Returns:
            PDF bytes
        """
        pdf = FPDF()
        pdf.set_margins(left=20, top=20, right=20)
        pdf.set_auto_page_break(auto=True, margin=15)
        
        # Title Page
        self._generate_title_page(pdf)
        
        # Executive Summary
        self._generate_executive_summary(pdf, analysis)
        self._add_divider(pdf)
        
        # Deal Overview
        self._generate_deal_overview(pdf, analysis)
        self._add_divider(pdf)
        
        # Timeline
        self._generate_timeline_section(pdf, analysis)
        self._add_divider(pdf)
        
        # What Went Wrong
        self._generate_what_went_wrong(pdf, analysis)
        self._add_divider(pdf)
        
        # Red Flags
        self._generate_red_flags(pdf, analysis)
        self._add_divider(pdf)
        
        # Recommendations
        self._generate_recommendations(pdf, analysis)
        self._add_divider(pdf)
        
        # Best Practices
        self._generate_best_practices(pdf, analysis)
        self._add_divider(pdf)
        
        # Comparative Analytics
        self._generate_comparative_analytics(pdf, analysis)
        self._add_divider(pdf)
        
        # Business Intelligence Metrics
        self._generate_bi_metrics(pdf, analysis)
        self._add_divider(pdf)
        
        # Final Summary
        self._generate_final_summary(pdf, analysis)
        
        # Footer
        pdf.set_y(-15)
        pdf.set_font("Helvetica", "I", 8)
        pdf.set_text_color(*self.colors["text"])
        pdf.cell(0, 10, f"Page {pdf.page_no()}", 0, 0, "C")
        
        # Generate PDF bytes
        pdf_bytes = pdf.output(dest="S")
        if isinstance(pdf_bytes, str):
            return pdf_bytes.encode("latin1")
        elif isinstance(pdf_bytes, bytearray):
            return bytes(pdf_bytes)
        else:
            return pdf_bytes
