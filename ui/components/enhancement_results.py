"""
Component for displaying standards enhancement results.
"""

import streamlit as st
import re
import pandas as pd
import datetime
from typing import Dict, Any, List

def display_results(results: Dict[str, Any]):
    """Display enhancement results in a structured way."""
    if not results:
        st.error("No results to display")
        return

    tabs = st.tabs(["Overview", "Expert Discussion", "Review Analysis", "Proposed Changes", "Validation"])
    
    # Overview Tab
    with tabs[0]:
        st.header(f"Standards Enhancement Results - FAS {results['standard_id']}")
        
        # Trigger Scenario in a nice box
        st.subheader("Trigger Scenario")
        st.info(results.get("trigger_scenario", ""))
        
        # Status and Key Metrics in columns
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Status")
            validation_text = str(results.get("validation", ""))
            if "APPROVED" in validation_text:
                st.success("✅ Enhancement Approved")
            elif "REJECTED" in validation_text:
                st.error("❌ Enhancement Rejected")
            elif "NEEDS REVISION" in validation_text:
                st.warning("⚠️ Needs Revision")
            
            # Expert Participation in a clean list
            st.subheader("Expert Participation")
            if results.get("discussion_history"):
                expert_stats = {}
                for entry in results["discussion_history"]:
                    expert = entry.get("agent", "Unknown").replace("_", " ").title()
                    expert_stats[expert] = expert_stats.get(expert, 0) + 1
                
                for expert, count in expert_stats.items():
                    st.markdown(
                        f'<div style="padding: 5px 10px; margin: 2px 0; border-radius: 5px; '
                        f'background-color: {get_expert_bg_color(expert)}; '
                        f'border-left: 4px solid {get_expert_color(expert)};">'
                        f'{expert}: {count} contribution{"s" if count > 1 else ""}'
                        f'</div>', 
                        unsafe_allow_html=True
                    )
        
        with col2:
            st.subheader("Key Areas Identified")
            if "analysis" in results and isinstance(results["analysis"], dict):
                areas = results["analysis"].get("enhancement_areas", [])
                if areas:
                    for area in areas:
                        st.markdown(f"- {area}")
        
        # Key Recommendations in a clean format
        st.subheader("Key Recommendations")
        if results.get("proposal"):
            proposal = results["proposal"]
            if isinstance(proposal, dict):
                proposal = proposal.get("proposal", "")
            
            # Better regex to extract actual recommendations
            recommendations = re.findall(
                r'(?:Enhancement [0-9]+:|Recommendation [0-9]+:|\*\*Recommendation:\*\*)\s*(.*?)(?=(?:Enhancement [0-9]+:|Recommendation [0-9]+:|\*\*Recommendation:\*\*)|$)', 
                proposal, 
                re.DOTALL
            )
            
            if recommendations:
                for i, rec in enumerate(recommendations, 1):
                    # Clean up the recommendation text
                    clean_rec = re.sub(r'\s+', ' ', rec).strip()
                    # Display in a nice box
                    st.markdown(
                        f'<div style="padding: 10px; margin: 5px 0; border-radius: 5px; '
                        f'background-color: #f8fafc; border-left: 4px solid #3b82f6;">'
                        f'<strong>Recommendation {i}:</strong><br>{clean_rec}'
                        f'</div>',
                        unsafe_allow_html=True
                    )
            else:
                st.info("No specific recommendations found in the proposal")

    # Expert Discussion Tab
    with tabs[1]:
        st.header("Expert Discussions")
        display_expert_discussions(results.get("discussion_history", []))
    
    # Review Analysis Tab
    with tabs[2]:
        st.header("Review Analysis")
        if "review" in results:
            display_review_analysis(results["review"])
    
    # Proposed Changes Tab
    with tabs[3]:
        st.header("Proposed Changes")
        display_proposed_changes(results)
    
    # Validation Tab
    with tabs[4]:
        st.header("Validation Results")
        display_validation_results(results.get("validation", {}))

def display_enhancement_metrics(diff_data: Dict):
    """Display enhancement metrics in a clean format."""
    stats = diff_data.get("stats", {})
    cols = st.columns(4)
    
    with cols[0]:
        st.metric("Words Added", stats.get("words_added", 0))
    with cols[1]:
        st.metric("Words Deleted", stats.get("words_deleted", 0))
    with cols[2]:
        st.metric("Words Unchanged", stats.get("words_unchanged", 0))
    with cols[3]:
        pct = round(stats.get("percent_changed", 0), 1)
        st.metric("Changes", f"{pct}%")

def display_review_analysis(review_data: Dict):
    """Display review analysis with key findings."""
    if isinstance(review_data, dict):
        analysis = review_data.get("review_analysis", "")
        findings = review_data.get("enhancement_areas", [])
        
        st.markdown(analysis)
        
        if findings:
            st.subheader("Key Findings")
            for finding in findings:
                st.markdown(f"- {finding}")
    else:
        st.markdown(str(review_data))

def display_proposed_changes(results: Dict):
    """Display proposed changes with original vs modified text."""
    proposal = results.get("proposal", "")
    if isinstance(proposal, dict):
        proposal = proposal.get("proposal", "")
    
    st.markdown("### Enhancement Proposals")
    st.markdown(proposal)
    
    # Show original vs proposed text comparison
    original = results.get("original_text", "")
    proposed = results.get("proposed_text", "")
    
    if original or proposed:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Original Text:**")
            st.code(original or "No original text available")
        with col2:
            st.markdown("**Proposed Text:**")
            st.code(proposed or "No proposed text available")

def display_validation_results(validation: Dict):
    """Display validation results with decision highlighting."""
    if not validation:
        st.warning("No validation results available")
        return
        
    validation_text = ""
    if isinstance(validation, dict):
        validation_text = validation.get("text", "") or str(validation)
    else:
        validation_text = str(validation)
    
    # Extract decision
    if "APPROVED" in validation_text:
        st.success("✅ APPROVED")
    elif "REJECTED" in validation_text:
        st.error("❌ REJECTED")
    elif "NEEDS REVISION" in validation_text:
        st.warning("⚠️ NEEDS REVISION")
    
    # Display full validation analysis
    st.markdown(validation_text)

def display_expert_discussions(discussions: List[Dict]):
    """Display expert discussions in a structured format."""
    
    if not discussions:
        st.info("No expert discussions available")
        return
        
    # Group discussions by round
    discussions_by_round = {}
    for entry in discussions:
        round_num = entry.get("round", 0)
        if round_num not in discussions_by_round:
            discussions_by_round[round_num] = []
        discussions_by_round[round_num].append(entry)
    
    # For each round, show participating experts and contributions
    for round_num in sorted(discussions_by_round.keys()):
        with st.expander(f"Discussion Round {round_num}", expanded=round_num == 1):
            # Show participating experts for this round
            experts_in_round = [entry.get("agent", "Unknown").replace("_", " ").title() 
                              for entry in discussions_by_round[round_num]]
            st.markdown("**Participating Experts:**")
            for expert in experts_in_round:
                st.markdown(
                    f'<div style="display: inline-block; padding: 4px 8px; margin: 2px; '
                    f'border-radius: 15px; background-color: {get_expert_bg_color(expert)}; '
                    f'border: 2px solid {get_expert_color(expert)};">'
                    f'{expert}</div>',
                    unsafe_allow_html=True
                )
            st.markdown("---")
            
            # Show contributions
            for entry in discussions_by_round[round_num]:
                # Rest of existing display code...
                expert_name = entry.get("agent", "Unknown Expert").replace("_", " ").title()
                content = entry.get("content", {})
                
                # Create a colored box for each expert's contribution
                st.markdown(f"""
                    <div style="border-left: 4px solid {get_expert_color(expert_name)};
                              padding: 10px;
                              margin: 10px 0;
                              background-color: {get_expert_bg_color(expert_name)}">
                        <h3 style="color: {get_expert_color(expert_name)};">{expert_name}</h3>
                    </div>
                """, unsafe_allow_html=True)
                
                # Display Analysis
                if isinstance(content.get("analysis"), dict):
                    st.markdown("**Analysis:**")
                    st.markdown(content["analysis"].get("text", ""))
                elif content.get("analysis"):
                    st.markdown("**Analysis:**")
                    st.markdown(str(content["analysis"]))
                
                # Display Concerns in a red-tinted box
                if content.get("concerns"):
                    st.markdown("""
                        <div style="background-color: #fff5f5; 
                                  border-left: 4px solid #f56565;
                                  padding: 10px;
                                  margin: 10px 0;">
                            <strong>Concerns:</strong>
                        </div>
                    """, unsafe_allow_html=True)
                    for concern in content["concerns"]:
                        if isinstance(concern, dict):
                            st.markdown(f"- {concern.get('description', '')}")
                        else:
                            st.markdown(f"- {concern}")
                
                # Display Recommendations in a green-tinted box
                if content.get("recommendations"):
                    st.markdown("""
                        <div style="background-color: #f0fff4;
                                  border-left: 4px solid #48bb78;
                                  padding: 10px;
                                  margin: 10px 0;">
                            <strong>Recommendations:</strong>
                        </div>
                    """, unsafe_allow_html=True)
                    for rec in content["recommendations"]:
                        if isinstance(rec, dict):
                            st.markdown(f"- {rec.get('description', '')}")
                        else:
                            st.markdown(f"- {rec}")
                
                st.markdown("---")

def get_expert_color(expert_name: str) -> str:
    """Get color for expert based on their domain."""
    colors = {
        "Shariah Expert": "#2563eb",  # Blue
        "Finance Expert": "#059669",   # Green
        "Standards Expert": "#7c3aed", # Purple
        "Practical Expert": "#d97706", # Orange
        "Risk Expert": "#dc2626"       # Red
    }
    return colors.get(expert_name, "#6b7280")  # Default gray

def get_expert_bg_color(expert_name: str) -> str:
    """Get background color for expert based on their domain."""
    bg_colors = {
        "Shariah Expert": "#eff6ff",   # Light blue
        "Finance Expert": "#f0fdf4",   # Light green
        "Standards Expert": "#f5f3ff",  # Light purple
        "Practical Expert": "#fff7ed",  # Light orange
        "Risk Expert": "#fef2f2"       # Light red
    }
    return bg_colors.get(expert_name, "#f9fafb")  # Default light gray

def display_cross_standard_tab(results):
    """Display cross-standard analysis tab."""
    print("Starting cross-standard analysis display...") # Debug print
    st.header("Cross-Standard Impact Analysis")
    
    # Add progress indication
    with st.spinner("Loading cross-standard analysis..."):
        if "cross_standard_analysis" in results:
            st.markdown(f'<div class="cross-standard-container">{results["cross_standard_analysis"]}</div>', 
                       unsafe_allow_html=True)
            print("Cross-standard analysis content loaded") # Debug print
        else:
            st.info("No cross-standard analysis available")
            return
    
        if "compatibility_matrix" in results:
            print("Processing compatibility matrix...") # Debug print
            st.subheader("Compatibility Matrix")
            
            matrix_df = pd.DataFrame(results["compatibility_matrix"])
            print(f"Matrix shape: {matrix_df.shape}") # Debug matrix size

def display_past_enhancement(enhancement_data):
    """Display a past enhancement from loaded data."""
    results = enhancement_data["results"]
    metadata = enhancement_data["metadata"]
    
    st.header(f"Enhancement for FAS {metadata['standard_id']}")
    
    # Show metadata
    st.markdown(f"**Date:** {datetime.datetime.strptime(metadata['timestamp'], '%Y%m%d_%H%M%S').strftime('%Y-%m-%d %H:%M:%S')}")
    st.markdown(f"**Decision:** {metadata['decision']}")
    
    # Display the full results
    display_results(results)

def display_enhancement_summary(enhancements: List[str]):
    """Display a summary of proposed enhancements."""
    st.subheader("Enhancement Summary")
    
    for i, enhancement in enumerate(enhancements, 1):
        # Extract title and key points
        title = enhancement.split(":")[0].strip()
        points = re.findall(r'\*\s+(.*?)(?=\n\*|\Z)', enhancement, re.DOTALL)
        
        with st.expander(f"Enhancement {i}: {title}", expanded=i == 1):
            if points:
                for point in points[:3]:  # Show top 3 points
                    st.markdown(f"• {point.strip()}")
                if len(points) > 3:
                    st.markdown(f"*... and {len(points) - 3} more points*")