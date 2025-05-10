"""
Component for displaying standards enhancement results.
"""

import streamlit as st
import re
import pandas as pd
import datetime

def display_results(results):
    """Display the enhancement results in a structured way."""
    if not results:
        st.error("No results to display")
        return
    
    # Create tabs for different sections
    tabs = st.tabs(["Overview", "Review Analysis", "Proposed Changes", "Diff View", "Validation"])
    
    # Check if we have the cross-standard analysis tab
    has_cross_standard = "cross_standard_analysis" in results and results["cross_standard_analysis"]
    
    # Overview Tab
    with tabs[0]:
        st.header(f"Standards Enhancement Results for FAS {results['standard_id']}")
        
        st.subheader("Trigger Scenario")
        st.write(results.get("trigger_scenario", "No trigger scenario provided"))
        
        if "enhanced_diff" in results and results["enhanced_diff"].get("stats"):
            stats = results["enhanced_diff"]["stats"]
            change_summary = results["enhanced_diff"].get("change_summary", "")
            
            if change_summary:
                st.info(f"**Change Summary**: {change_summary}")
                
            # Create columns for stats
            cols = st.columns(5)
            with cols[0]:
                st.metric("Words Added", stats.get("words_added", 0))
            with cols[1]:
                st.metric("Words Deleted", stats.get("words_deleted", 0))
            with cols[2]:
                st.metric("Words Unchanged", stats.get("words_unchanged", 0))
            with cols[3]:
                st.metric("Original Words", stats.get("total_words_original", 0))
            with cols[4]:
                pct = round(stats.get("percent_changed", 0), 1)
                st.metric("% Changed", f"{pct}%")
        else:
            st.warning("Diff statistics not available")
        
        st.subheader("Key Findings")
        
        # Extract and display key findings from review
        review_text = results.get("review", "")
        if review_text:
            # Extract bullet points or numbered lists
            bullets = re.findall(r'(?:^|\n)[\*\-\d\.]+\s+(.*?)(?=\n[\*\-\d\.]+\s+|\Z)', review_text, re.DOTALL)
            
            if bullets:
                for bullet in bullets[:3]:  # Show top 3 findings
                    st.markdown(f"- {bullet.strip()}")
                if len(bullets) > 3:
                    st.markdown(f"- *Plus {len(bullets) - 3} more findings...*")
            else:
                # If no bullet points, show first paragraph
                first_para = review_text.split('\n\n')[0] if '\n\n' in review_text else review_text
                st.write(first_para)
        else:
            st.info("No review findings available")
            
        # Add cross-standard summary if available
        if has_cross_standard:
            st.subheader("Cross-Standard Impact Summary")
            analysis_text = results["cross_standard_analysis"]
            summary = analysis_text.split("\n\n")[0] if "\n\n" in analysis_text else analysis_text[:200] + "..."
            st.write(summary)
    
    # Review Analysis Tab
    with tabs[1]:
        st.header("Review Findings")
        review_content = results.get("review", "No review findings available")
        st.markdown(f'<div class="review-container">{review_content}</div>', unsafe_allow_html=True)
    
    # Proposed Changes Tab
    with tabs[2]:
        st.header("Proposed Enhancements")
        proposal_content = results.get("proposal", "No proposed enhancements available")
        st.markdown(f'<div class="proposal-container">{proposal_content}</div>', unsafe_allow_html=True)
        
        # Show original vs proposed text if available
        original_text = results.get("original_text", "")
        proposed_text = results.get("proposed_text", "")
        
        if original_text or proposed_text:
            st.subheader("Original vs. Proposed Text")
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Original Text:**")
                st.markdown(f'<div class="diff-container">{original_text or "No original text extracted"}</div>', unsafe_allow_html=True)
            with col2:
                st.markdown("**Proposed Text:**")
                st.markdown(f'<div class="diff-container">{proposed_text or "No proposed text extracted"}</div>', unsafe_allow_html=True)
        elif proposal_content:
            st.info("Original and proposed text could not be extracted from the proposal. See the full proposal above.")
    
    # Diff View Tab
    with tabs[3]:
        st.header("Text Differences")
        
        # Check if we have enhanced diff
        has_enhanced_diff = "enhanced_diff" in results and isinstance(results["enhanced_diff"], dict)
        
        # If no diff information at all, show a message
        if not has_enhanced_diff and "simple_diff_html" not in results:
            st.warning("No diff information available. This could be because the original and proposed text extraction failed.")
            
            # Show original and proposed text anyway if available
            original_text = results.get("original_text", "")
            proposed_text = results.get("proposed_text", "")
            
            if original_text or proposed_text:
                st.subheader("Original vs. Proposed Text (No Diff Available)")
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**Original Text:**")
                    st.text_area("", original_text or "No original text extracted", height=300, key="original_text_nodiff")
                with col2:
                    st.markdown("**Proposed Text:**")
                    st.text_area("", proposed_text or "No proposed text extracted", height=300, key="proposed_text_nodiff")
            return
        
        if has_enhanced_diff:
            # Create tabs for different diff views
            diff_tabs = st.tabs(["Word-by-Word", "Inline View", "Sentence Level", "Standard Diff"])
            
            # Word-by-Word Diff Tab
            with diff_tabs[0]:
                st.markdown("### Word-by-Word Comparison")
                st.markdown("This view shows each word-level change with additions in green and deletions in red.")
                
                # Display diff stats if available
                if "stats" in results["enhanced_diff"]:
                    stats = results["enhanced_diff"]["stats"]
                    st.markdown(
                        f'<div class="diff-stats">'
                        f'<div class="diff-stat-item">'
                        f'<div class="diff-stat-value">{stats.get("words_added", 0)}</div>'
                        f'<div class="diff-stat-label">Words Added</div>'
                        f'</div>'
                        f'<div class="diff-stat-item">'
                        f'<div class="diff-stat-value">{stats.get("words_deleted", 0)}</div>'
                        f'<div class="diff-stat-label">Words Deleted</div>'
                        f'</div>'
                        f'<div class="diff-stat-item">'
                        f'<div class="diff-stat-value">{stats.get("words_unchanged", 0)}</div>'
                        f'<div class="diff-stat-label">Words Unchanged</div>'
                        f'</div>'
                        f'<div class="diff-stat-item">'
                        f'<div class="diff-stat-value">{round(stats.get("percent_changed", 0), 1)}%</div>'
                        f'<div class="diff-stat-label">Changed</div>'
                        f'</div>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
                
                # Display word diff
                word_diff_html = results["enhanced_diff"].get("word_diff_html", "<div>Word-by-word diff not available</div>")
                st.markdown(f'<div class="diff-container">{word_diff_html}</div>', unsafe_allow_html=True)
            
            # Inline View Tab
            with diff_tabs[1]:
                st.markdown("### Inline Diff")
                st.markdown("This view shows changes inline with character-level precision.")
                
                # Display inline diff
                inline_diff_html = results["enhanced_diff"].get("inline_diff_html", "<div>Inline diff not available</div>")
                st.markdown(f'<div class="diff-container">{inline_diff_html}</div>', unsafe_allow_html=True)
            
            # Sentence Level Tab
            with diff_tabs[2]:
                st.markdown("### Sentence-Level Comparison")
                st.markdown("This view compares entire sentences to show changes at a higher level.")
                
                # Display sentence diff
                sentence_diff_html = results["enhanced_diff"].get("sentence_diff_html", "<div>Sentence-level diff not available</div>")
                st.markdown(f'<div class="diff-container">{sentence_diff_html}</div>', unsafe_allow_html=True)
            
            # Standard Diff Tab
            with diff_tabs[3]:
                st.markdown("### Standard Diff")
                st.markdown("This is a traditional line-by-line diff format.")
                
                simple_diff_html = results.get("simple_diff_html", "<div>Standard diff not available</div>")
                st.markdown(f'<div class="diff-container">{simple_diff_html}</div>', unsafe_allow_html=True)
        
        else:
            # Fallback to simple diff if enhanced diff is not available
            if "simple_diff_html" in results:
                st.markdown("### Text Differences")
                st.markdown(f'<div class="diff-container">{results["simple_diff_html"]}</div>', unsafe_allow_html=True)
            else:
                st.warning("No diff visualization available")
    
    # Validation Tab
    with tabs[4]:
        st.header("Validation Results")
        
        # Try to extract validation decision
        decision = "Undetermined"
        decision_color = "gray"
        
        validation_text = results.get("validation", "")
        if validation_text:
            if "APPROVED" in validation_text:
                decision = "APPROVED"
                decision_color = "green"
            elif "REJECTED" in validation_text:
                decision = "REJECTED"
                decision_color = "red"
            elif "NEEDS REVISION" in validation_text:
                decision = "NEEDS REVISION"
                decision_color = "orange"
        
        # Display decision prominently
        st.markdown(
            f'<div style="background-color: {decision_color}; color: white; padding: 1rem; '
            f'border-radius: 0.5rem; font-weight: bold; text-align: center; margin-bottom: 1rem;">'
            f'Decision: {decision}'
            f'</div>',
            unsafe_allow_html=True
        )
        
        # Display full validation text
        st.markdown(f'<div class="validation-container">{validation_text or "No validation results available"}</div>', unsafe_allow_html=True)

def display_cross_standard_tab(results):
    """Display cross-standard analysis tab."""
    st.header("Cross-Standard Impact Analysis")
    
    # Display the full analysis
    if "cross_standard_analysis" in results:
        st.markdown(f'<div class="cross-standard-container">{results["cross_standard_analysis"]}</div>', unsafe_allow_html=True)
    else:
        st.info("No cross-standard analysis available")
        return
    
    # Show the compatibility matrix as a table
    if "compatibility_matrix" in results:
        st.subheader("Compatibility Matrix")
        
        matrix_df = pd.DataFrame(results["compatibility_matrix"])
        
        # Format the dataframe for display
        matrix_df = matrix_df.rename(columns={
            "standard_id": "Standard", 
            "impact_level": "Impact Level", 
            "impact_type": "Impact Type"
        })
        
        # Add FAS prefix to standard IDs
        matrix_df["Standard"] = "FAS " + matrix_df["Standard"]
        
        # Build HTML table with conditional formatting
        html_table = '<table class="compatibility-table"><tr><th>Standard</th><th>Impact Level</th><th>Impact Type</th></tr>'
        
        for _, row in matrix_df.iterrows():
            standard = row["Standard"]
            impact_level = row["Impact Level"]
            impact_type = row["Impact Type"]
            
            # Set CSS classes based on values
            impact_level_class = f"impact-{impact_level.lower()}"
            impact_type_class = impact_type.lower()
            
            html_table += f'<tr class="{impact_type_class}">'
            html_table += f'<td>{standard}</td>'
            html_table += f'<td class="{impact_level_class}">{impact_level}</td>'
            html_table += f'<td>{impact_type}</td>'
            html_table += '</tr>'
        
        html_table += '</table>'
        st.write(html_table, unsafe_allow_html=True)
        
        # Visual impact diagram
        st.subheader("Impact Visualization")
        
        # Create a visual representation of the compatibility matrix
        cols = st.columns(len(matrix_df))
        for i, (_, row) in enumerate(matrix_df.iterrows()):
            with cols[i]:
                # Set color based on impact type
                color = "#f8d7da"  # Red for contradictions
                text_color = "#721c24"
                if row["Impact Type"].lower() == "synergy":
                    color = "#d4edda"  # Green for synergies
                    text_color = "#155724"
                elif row["Impact Type"].lower() == "both":
                    color = "#fff3cd"  # Yellow for both
                    text_color = "#856404"
                elif row["Impact Type"].lower() == "none":
                    color = "#e2e3e5"  # Gray for none
                    text_color = "#383d41"
                    
                # Display the standard card
                st.markdown(
                    f"""
                    <div style="background-color: {color}; color: {text_color}; padding: 10px; 
                            border-radius: 5px; text-align: center; height: 120px;">
                        <h3>{row["Standard"]}</h3>
                        <p><b>Impact: {row["Impact Level"]}</b></p>
                        <p>{row["Impact Type"]}</p>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )

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