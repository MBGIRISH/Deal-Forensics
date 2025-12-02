"Streamlit dashboard for the Deal Forensics system."

from __future__ import annotations

from typing import Any, Dict
from pathlib import Path
import sys

import pandas as pd
import plotly.express as px
import streamlit as st

# Ensure project root is on sys.path so we can import `app`
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app import DealForensicsOrchestrator


@st.cache_resource(show_spinner=False)
def get_orchestrator() -> DealForensicsOrchestrator:
    return DealForensicsOrchestrator()


st.set_page_config(
    page_title="Deal Forensics AI",
    layout="wide",
    page_icon="📉",
)

if "theme" not in st.session_state:
    st.session_state["theme"] = "dark"  # Default to dark mode

with st.sidebar:
    st.header("Settings")
    theme_choice = st.toggle("Dark mode", value=st.session_state["theme"] == "dark")
    st.session_state["theme"] = "dark" if theme_choice else "light"
    st.markdown(
        """
**Tips**
- Use detailed post-mortem write-ups for best results.
- Add competitive intel in the document to improve comparative analysis.
        """
    )

current_theme = st.session_state["theme"]

# Theme colors - Light mode (default) and Dark mode
if current_theme == "dark":
    bg_color = "#111827"
    text_color = "#f3f4f6"
    sidebar_bg = "#020617"
    card_bg = "rgba(79, 70, 229, 0.15)"
    border_color = "#374151"
else:
    # Light mode (default)
    bg_color = "#ffffff"
    text_color = "#111827"
    sidebar_bg = "#f4f4f5"
    card_bg = "rgba(79, 70, 229, 0.08)"
    border_color = "#e5e7eb"

st.markdown(
    f"""
    <style>
    .stApp {{
        background-color: {bg_color} !important;
        color: {text_color} !important;
    }}
    .main .block-container {{
        background-color: {bg_color};
        color: {text_color};
    }}
    section[data-testid="stSidebar"] {{
        background-color: {sidebar_bg} !important;
    }}
    .report-card {{
        padding: 1rem;
        border-radius: 12px;
        background: {card_bg};
        margin-bottom: 0.75rem;
        border: 1px solid {border_color};
    }}
    /* Ensure text is readable in both themes */
    h1, h2, h3, h4, h5, h6 {{
        color: {text_color} !important;
    }}
    p, div, span {{
        color: {text_color};
    }}
    /* Style Streamlit components for theme */
    .stMetric {{
        color: {text_color};
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🔎 Multi-Agent Deal Forensics AI")
st.caption("Upload a financial/deal PDF to uncover failure points, benchmarks, and a recovery playbook.")

# File upload with strict validation
uploaded_file = st.file_uploader(
    "Upload Financial/Deal Document",
    type=["pdf", "docx", "doc", "txt"],
    help="Upload only deal-related documents: valuation reports, term sheets, M&A docs, financial contracts (PDF, DOCX, or TXT)."
)

# Show validation message
if uploaded_file is None:
    st.info(
        "📋 **Upload Requirements:**\n\n"
        "✅ **Accepted:** Financial/deal documents (PDF, DOCX, or TXT)\n"
        "- Valuation reports and term sheets\n"
        "- M&A documents and acquisition agreements\n"
        "- Investment proposals and deal summaries\n"
        "- Lost sales deal post-mortems (with financial context)\n\n"
        "❌ **Rejected:**\n"
        "- Text files, images, compressed files\n"
        "- Blank documents or image-only PDFs\n"
        "- Unrelated documents (recipes, novels, invoices, etc.)\n\n"
        "**File Size:** Maximum 100 MB"
    )

# Disable analyze button if no file uploaded
analyze_button = st.button(
    "Analyze Deal",
    type="primary",
    use_container_width=True,
    disabled=(uploaded_file is None)
)

if "analysis_result" not in st.session_state:
    st.session_state["analysis_result"] = None

if analyze_button:
    if not uploaded_file:
        st.error("❌ Please upload a PDF file.")
    else:
        with st.spinner("Validating document and running multi-agent analysis..."):
            try:
                orchestrator = get_orchestrator()
                file_bytes = uploaded_file.getvalue()
                analysis_result = orchestrator.analyze_file(file_bytes, uploaded_file.name)
                
                # Check if result contains error
                if analysis_result.get("error", False):
                    error_msg = analysis_result.get("error_message", "Unknown error")
                    st.error(f"❌ **Document Validation Failed**\n\n{error_msg}")
                    st.session_state["analysis_result"] = None
                else:
                    st.session_state["analysis_result"] = analysis_result
                    st.success("✅ Analysis complete!")
                    
            except ValueError as e:
                error_msg = str(e)
                st.error(f"❌ **Document Validation Failed**\n\n{error_msg}")
                
                # Show helpful information
                with st.expander("ℹ️ What documents are accepted?", expanded=False):
                    st.markdown(
                        "**✅ Accepted Documents:**\n"
                        "- Financial contracts and agreements (PDF, DOCX, or TXT)\n"
                        "- Valuation reports and term sheets\n"
                        "- M&A documents and acquisition agreements\n"
                        "- Investment proposals and deal summaries\n"
                        "- Lost sales deal post-mortems (with financial context)\n"
                        "- Deal failure analysis with financial terms\n\n"
                        "**❌ Rejected Documents:**\n"
                        "- Text files, images, compressed files\n"
                        "- Blank documents or image-only PDFs\n"
                        "- Random PDFs/DOCX, invoices, receipts (unless deal-related)\n"
                        "- Academic papers, research documents\n"
                        "- Novels, stories, or fiction\n"
                        "- Recipes, cooking guides\n"
                        "- Medical records or prescriptions\n"
                        "- General business documents without financial/deal context"
                    )
                
                st.session_state["analysis_result"] = None
                
            except Exception as e:
                st.error(f"❌ **Analysis Error:** {str(e)}")
                st.session_state["analysis_result"] = None

analysis_result: Dict[str, Any] | None = st.session_state.get("analysis_result")
if analysis_result:
    timeline = analysis_result.get("timeline", {})
    comparative = analysis_result.get("comparative", {})
    playbook = analysis_result.get("playbook", {})
    scorecard = analysis_result.get("scorecard", {})
    metadata = analysis_result.get("metadata", {})
    
    # ========== DEAL SUMMARY CARD ==========
    st.divider()
    st.subheader("📊 Deal Summary")
    summary_cols = st.columns(5)
    with summary_cols[0]:
        st.metric("Seller/Owner", metadata.get("owner", "Unknown"))
    with summary_cols[1]:
        st.metric("Buyer/Deal", metadata.get("deal_name", "Unknown Deal"))
    with summary_cols[2]:
        st.metric("Deal Value", str(metadata.get("value", "N/A")))
    with summary_cols[3]:
        st.metric("Industry", metadata.get("industry", "Unknown"))
    with summary_cols[4]:
        outcome = metadata.get("stage", "Closed Lost")
        st.metric("Outcome", outcome)
    
    # Key Issue
    what_went_wrong = playbook.get("what_went_wrong", [])
    if what_went_wrong:
        key_issue = what_went_wrong[0] if what_went_wrong else "See analysis below"
        st.info(f"🔑 **Key Issue:** {key_issue}")
    
    # Win Probability Score (inverse of final health score)
    final_health = scorecard.get("final_deal_health_score", 5.0) if scorecard else 5.0
    win_probability = final_health * 10  # Convert 0-10 to 0-100%
    
    st.divider()
    col_prob, col_drivers = st.columns([1, 2])
    
    with col_prob:
        st.subheader("🎯 Win Probability Score")
        st.metric("Probability", f"{win_probability:.1f}%", delta=f"{win_probability - 50:.1f}%")
        # Progress bar
        st.progress(win_probability / 100)
        if win_probability < 30:
            st.error("Very Low - Deal was at high risk")
        elif win_probability < 50:
            st.warning("Low - Multiple issues identified")
        elif win_probability < 70:
            st.info("Medium - Some concerns present")
        else:
            st.success("High - Deal had good potential")
    
    with col_drivers:
        st.subheader("📉 Loss Driver Analysis")
        if scorecard:
            # Create loss driver chart
            drivers = {
                "Pricing Issues": 10 - scorecard.get("pricing_clarity_score", 5.0),
                "Communication": 10 - scorecard.get("communication_quality_score", 5.0),
                "Documentation": 10 - scorecard.get("documentation_quality_score", 5.0),
                "Competitive Risk": 10 - scorecard.get("competitive_risk_score", 5.0),
                "Delivery/Execution": 10 - scorecard.get("delivery_execution_score", 5.0),
            }
            drivers_df = pd.DataFrame(list(drivers.items()), columns=["Driver", "Risk Score"])
            drivers_df = drivers_df.sort_values("Risk Score", ascending=True)
            
            fig_drivers = px.bar(
                drivers_df,
                x="Risk Score",
                y="Driver",
                orientation="h",
                title="Risk Scores by Category (Higher = More Risk)",
                color="Risk Score",
                color_continuous_scale="Reds"
            )
            fig_drivers.update_layout(showlegend=False, height=300)
            st.plotly_chart(fig_drivers, use_container_width=True)

    st.divider()
    st.subheader("📅 Timeline Visualization")
    
    # Timeline Score
    timeline_score = timeline.get("timeline_score", 5.0)
    col_timeline_score, _ = st.columns([1, 3])
    with col_timeline_score:
        st.metric("Timeline Score", f"{timeline_score:.1f}/10", 
                 delta="Good" if timeline_score >= 7 else "Needs Improvement" if timeline_score >= 5 else "Poor")
    
    events = timeline.get("events", [])
    # Always show timeline - use fallback if empty
    if not events:
        # Create minimal timeline from available data
        events = [{
            "phase": "Discovery",
            "timestamp": "Week 1",
            "summary": "Deal engagement started",
            "sentiment": "neutral",
            "blockers": []
        }]
        st.warning("Timeline data limited - showing inferred timeline")
    
    # Process events for timeline visualization
    processed_events = []
    for event in events:
        if isinstance(event, dict):
            processed_events.append({
                "phase": event.get("phase", "Discovery Phase"),
                "timestamp": event.get("timestamp", ""),
                "event_name": event.get("event_name", event.get("summary", "Event")),
                "sentiment": event.get("sentiment", "neutral"),
                "description": event.get("description", event.get("summary", ""))
            })
    
    if processed_events:
        df_timeline = pd.DataFrame(processed_events)
        
        # Convert timestamps to datetime for proper timeline
        try:
            df_timeline["date"] = pd.to_datetime(df_timeline["timestamp"], errors="coerce")
            df_timeline = df_timeline.dropna(subset=["date"])
            if not df_timeline.empty:
                df_timeline["start"] = df_timeline["date"]
                df_timeline["end"] = df_timeline["date"] + pd.Timedelta(days=1)
            else:
                df_timeline["start"] = range(len(df_timeline))
                df_timeline["end"] = df_timeline["start"] + 1
        except Exception:
            df_timeline["start"] = range(len(df_timeline))
            df_timeline["end"] = df_timeline["start"] + 1
        
        # Sentiment color mapping
        sentiment_colors = {
            "positive": "#10b981",  # Green
            "neutral": "#6b7280",   # Gray
            "negative": "#ef4444"   # Red
        }
        
        fig_timeline = px.timeline(
            df_timeline,
            x_start="start",
            x_end="end",
            y="phase",
            color="sentiment",
            color_discrete_map=sentiment_colors,
            hover_data=["event_name", "description"],
            title="Deal Timeline by Phase (Color = Sentiment)"
        )
        fig_timeline.update_yaxes(autorange="reversed")
        fig_timeline.update_layout(height=400)
        st.plotly_chart(fig_timeline, use_container_width=True)
        
        # Sentiment distribution
        sentiment_counts = df_timeline["sentiment"].value_counts()
        if not sentiment_counts.empty:
            col_sent1, col_sent2, col_sent3 = st.columns(3)
            with col_sent1:
                positive_pct = (sentiment_counts.get("positive", 0) / len(df_timeline)) * 100
                st.metric("😊 Positive Events", f"{positive_pct:.1f}%", delta=f"{sentiment_counts.get('positive', 0)} events")
            with col_sent2:
                neutral_pct = (sentiment_counts.get("neutral", 0) / len(df_timeline)) * 100
                st.metric("😐 Neutral Events", f"{neutral_pct:.1f}%", delta=f"{sentiment_counts.get('neutral', 0)} events")
            with col_sent3:
                negative_pct = (sentiment_counts.get("negative", 0) / len(df_timeline)) * 100
                st.metric("😞 Negative Events", f"{negative_pct:.1f}%", delta=f"{sentiment_counts.get('negative', 0)} events")

    st.divider()
    st.subheader("Business Intelligence Metrics")
    if scorecard:
        # Display in 2 columns for better layout
        col1, col2, col3 = st.columns(3)
        metrics_list = list(scorecard.items())
        for idx, (metric, value) in enumerate(metrics_list):
            col = [col1, col2, col3][idx % 3]
            with col:
                st.metric(metric.replace("_", " ").title(), f"{value:.2f}/10")
    else:
        st.info("Scorecard not available")

    st.divider()
    st.subheader("🔍 Comparative Analytics")
    if comparative:
        # Competitor Intelligence Section
        competitor_risk = comparative.get("competitor_risk", 0.5)
        if competitor_risk > 0.3:
            st.markdown("### 🎯 Competitor Intelligence")
            comp_col1, comp_col2 = st.columns(2)
            with comp_col1:
                st.metric("Competitive Risk", f"{competitor_risk*100:.0f}%", 
                         delta="High" if competitor_risk > 0.6 else "Medium" if competitor_risk > 0.4 else "Low")
            with comp_col2:
                pricing_delta = comparative.get("pricing_delta", 0.5)
                st.metric("Pricing Gap", f"{pricing_delta*100:.0f}%", 
                         delta="Significant" if pricing_delta > 0.5 else "Moderate")
            
            # Competitor mentions
            similar = comparative.get("similar_deals", [])
            competitor_names = []
            for deal in similar:
                if isinstance(deal, dict) and "outcome" in deal.get("outcome", "").lower():
                    outcome = deal.get("outcome", "")
                    if "lost to" in outcome.lower() or "competitor" in outcome.lower():
                        competitor_names.append(outcome)
            
            if competitor_names:
                st.markdown("**Competitor Activity Detected:**")
                for comp in competitor_names[:3]:
                    st.write(f"⚠️ {comp}")
            st.divider()
        
        # Similarity Chart
        # Similar Deals with similarity percentages
        similar = comparative.get("similar_deals", [])
        if similar:
            st.markdown("**📊 Similar Historical Deals**")
            sim_df = pd.DataFrame(similar)
            if "similarity_score" not in sim_df.columns:
                sim_df["similarity_score"] = 0.6
            sim_df["similarity_pct"] = sim_df["similarity_score"] * 100
            sim_df = sim_df.sort_values("similarity_pct", ascending=False)
            
            sim_fig = px.bar(
                sim_df,
                x="similarity_pct",
                y="deal_name",
                orientation="h",
                hover_data=["similarity_reason", "outcome"],
                title="Similarity Percentage to Historical Deals",
                labels={"similarity_pct": "Similarity %", "deal_name": "Deal Name"},
                color="similarity_pct",
                color_continuous_scale="Blues"
            )
            sim_fig.update_layout(height=300, showlegend=False)
            st.plotly_chart(sim_fig, use_container_width=True)
            
            # Risk Distribution Pie Chart
            if len(similar) > 0:
                risk_factors = comparative.get("shared_risk_factors", [])
                if risk_factors:
                    st.markdown("**📈 Risk Distribution**")
                    risk_df = pd.DataFrame({"Risk Factor": risk_factors[:5], "Count": [1]*min(5, len(risk_factors))})
                    risk_fig = px.pie(
                        risk_df,
                        values="Count",
                        names="Risk Factor",
                        title="Top Risk Factors Distribution"
                    )
                    st.plotly_chart(risk_fig, use_container_width=True)
        
        # Common Patterns
        patterns = comparative.get("common_patterns", [])
        if patterns:
            st.markdown("**Common Patterns Across Lost Deals**")
            for pattern in patterns[:8]:
                st.write(f"• {pattern}")
        
        # Shared Risk Factors
        risk_factors = comparative.get("shared_risk_factors", [])
        if risk_factors:
            st.markdown("**Shared Risk Factors**")
            for risk in risk_factors[:8]:
                st.write(f"⚠️ {risk}")
        
        # Benchmark Scores
        benchmarks = comparative.get("benchmark_scores", {})
        if benchmarks:
            st.markdown("**Benchmark Scores**")
            bench_cols = st.columns(len(benchmarks) or 1)
            for idx, (metric, value) in enumerate(benchmarks.items()):
                bench_cols[idx % len(bench_cols)].metric(metric.replace("_", " ").title(), str(value))
        
        # Comparative Table
        table_df = pd.DataFrame(comparative.get("comparative_table", []))
        if not table_df.empty:
            st.markdown("**Comparative Metrics Table**")
            st.dataframe(table_df, use_container_width=True)
        
        # Insights Summary
        insights = comparative.get("insights_summary", "")
        if insights:
            st.markdown("**Key Insights**")
            st.info(insights)
    else:
        st.info("Comparative insights unavailable.")

    st.divider()
    st.subheader("📚 Playbook Generator")
    
    # What Went Wrong with chips/tags (theme-aware)
    what_went_wrong = playbook.get("what_went_wrong", [])
    st.markdown(f"**❌ What Went Wrong (Root Causes)** - *{len(what_went_wrong)} items*")
    if what_went_wrong:
        # Theme-aware styling
        wrong_bg = "rgba(239, 68, 68, 0.15)" if current_theme == "dark" else "rgba(239, 68, 68, 0.1)"
        wrong_text = "#fca5a5" if current_theme == "dark" else text_color
        # Display as chips/tags - show ALL items (up to 10) with proper text wrapping
        for item in what_went_wrong[:10]:
            st.markdown(f'<div style="padding: 0.5rem; margin: 0.25rem 0; background: {wrong_bg}; border-left: 4px solid #ef4444; border-radius: 4px; color: {wrong_text}; word-wrap: break-word; overflow-wrap: break-word;">❌ {item}</div>', unsafe_allow_html=True)
    else:
        st.info("No root causes identified. Analyzing document...")
    
    st.divider()
    
    # Red Flags with chips (theme-aware)
    red_flags = playbook.get("red_flags", [])
    st.markdown(f"**⚠️ Red Flags (Warning Signs)** - *{len(red_flags)} items*")
    if red_flags:
        flag_bg = "rgba(245, 158, 11, 0.15)" if current_theme == "dark" else "rgba(245, 158, 11, 0.1)"
        flag_text = "#fcd34d" if current_theme == "dark" else text_color
        # Display ALL items (up to 10) with proper text wrapping
        for flag in red_flags[:10]:
            st.markdown(f'<div style="padding: 0.5rem; margin: 0.25rem 0; background: {flag_bg}; border-left: 4px solid #f59e0b; border-radius: 4px; color: {flag_text}; word-wrap: break-word; overflow-wrap: break-word;">⚠️ {flag}</div>', unsafe_allow_html=True)
    else:
        st.info("No red flags identified. Analyzing document...")
    
    st.divider()
    
    # Recommendations and Best Practices in columns
    col1, col2 = st.columns(2)
    
    with col1:
        recommendations = playbook.get("recommendations", [])
        st.markdown(f"**✔️ Recommendations (Short-Term Actions)** - *{len(recommendations)} items*")
        if recommendations:
            rec_bg = "rgba(79, 70, 229, 0.15)" if current_theme == "dark" else "rgba(79, 70, 229, 0.05)"
            # Display ALL items (up to 12)
            for rec in recommendations[:12]:
                if isinstance(rec, dict):
                    priority_emoji = {"High": "🔴", "Med": "🟡", "Low": "🟢"}.get(rec.get("priority", "Med"), "🟡")
                    impact = rec.get("impact", 5)
                    impact_color = "#10b981" if impact >= 8 else "#f59e0b" if impact >= 6 else "#6b7280"
                    action_text = rec.get("action", "N/A")
                    # Ensure text wraps properly
                    st.markdown(
                        f'<div style="padding: 0.75rem; margin: 0.5rem 0; background: {rec_bg}; border-left: 4px solid {impact_color}; border-radius: 4px; color: {text_color}; word-wrap: break-word; overflow-wrap: break-word;">'
                        f'<strong>{priority_emoji} [{rec.get("priority", "Med")}]</strong> {action_text}<br>'
                        f'<small style="color: {text_color};">Impact: <strong style="color: {impact_color}">{impact}/10</strong> | Owner: {rec.get("owner", "Sales Rep")}</small>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
                elif isinstance(rec, str):
                    # Handle string recommendations with proper text wrapping
                    st.markdown(
                        f'<div style="padding: 0.75rem; margin: 0.5rem 0; background: {rec_bg}; border-left: 4px solid #6366f1; border-radius: 4px; color: {text_color}; word-wrap: break-word; overflow-wrap: break-word;">'
                        f'✔️ {rec}'
                        f'</div>',
                        unsafe_allow_html=True
                    )
        else:
            st.info("No recommendations available. Analyzing document...")
    
    with col2:
        best_practices = playbook.get("best_practices", [])
        st.markdown(f"**⭐ Best Practices (Long-Term Improvements)** - *{len(best_practices)} items*")
        if best_practices:
            bp_bg = "rgba(16, 185, 129, 0.15)" if current_theme == "dark" else "rgba(16, 185, 129, 0.05)"
            bp_text = "#6ee7b7" if current_theme == "dark" else text_color
            # Display ALL items (up to 10) with proper text wrapping
            for bp in best_practices[:10]:
                st.markdown(
                    f'<div style="padding: 0.75rem; margin: 0.5rem 0; background: {bp_bg}; border-left: 4px solid #10b981; border-radius: 4px; color: {bp_text}; word-wrap: break-word; overflow-wrap: break-word;">⭐ {bp}</div>',
                    unsafe_allow_html=True
                )
        else:
            st.info("No best practices available. Analyzing document...")

    st.divider()
    st.subheader("Downloadable Report")
    st.download_button(
        label="Download PDF Report",
        data=analysis_result["report"],
        file_name="deal_forensics_report.pdf",
        mime="application/pdf",
        use_container_width=True,
    )

    st.divider()
    st.subheader("Raw JSON")
    json_safe = {k: v for k, v in analysis_result.items() if k != "report"}
    st.json(json_safe)

