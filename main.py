"""
Main entry point for Deal Forensics AI system.

This module provides a CLI interface for running deal analysis.
For the Streamlit UI, use: streamlit run ui/dashboard.py
"""

from __future__ import annotations

import sys
from pathlib import Path

from app import DealForensicsOrchestrator


def main() -> None:
    """
    CLI entry point for deal analysis.
    
    Usage:
        python main.py <path_to_deal_document>
    """
    if len(sys.argv) < 2:
        print("Usage: python main.py <path_to_deal_document>")
        print("\nFor Streamlit UI, use: streamlit run ui/dashboard.py")
        sys.exit(1)
    
    file_path = Path(sys.argv[1])
    if not file_path.exists():
        print(f"Error: File not found: {file_path}")
        sys.exit(1)
    
    print(f"Analyzing deal document: {file_path}")
    
    try:
        orchestrator = DealForensicsOrchestrator()
        
        with file_path.open("rb") as f:
            file_bytes = f.read()
        
        result = orchestrator.analyze_file(file_bytes, file_path.name)
        
        print("\n" + "="*60)
        print("DEAL FORENSICS ANALYSIS COMPLETE")
        print("="*60)
        
        # Print timeline
        timeline = result.get("timeline", {})
        events = timeline.get("events", [])
        print(f"\nTimeline Events: {len(events)}")
        for i, event in enumerate(events[:5], 1):
            print(f"  {i}. [{event.get('phase', 'Unknown')}] {event.get('summary', 'N/A')}")
        
        # Print scores
        scorecard = result.get("scorecard", {})
        print(f"\nBusiness Intelligence Scores:")
        for metric, value in scorecard.items():
            print(f"  {metric.replace('_', ' ').title()}: {value:.2f}")
        
        # Print playbook highlights
        playbook = result.get("playbook", {})
        what_went_wrong = playbook.get("what_went_wrong", [])
        if what_went_wrong:
            print(f"\nKey Issues Identified:")
            for issue in what_went_wrong[:3]:
                print(f"  - {issue}")
        
        print(f"\nFull report saved to: {result.get('metadata', {}).get('deal_name', 'report')}.pdf")
        print("\nFor detailed analysis, use the Streamlit UI: streamlit run ui/dashboard.py")
        
    except Exception as e:
        print(f"Error during analysis: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

