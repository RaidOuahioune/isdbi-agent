import streamlit as st
import sys
import os
import time
import re
import json
import datetime
from pathlib import Path
from output_parser import OutputParser
from word_diff import generate_complete_diff
from category_config import (
    ENHANCEMENT_CATEGORIES, 
    get_test_cases_by_category,
    get_default_output_file
)
import pandas as pd

# Set page configuration
st.set_page_config(
    page_title="AAOIFI Standards Enhancement (Simple Demo)",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main {
        background-color: #f5f7f9;
    }
    .stTabs [data-baseweb="tab-panel"] {
        padding-top: 1rem;
    }
    .stMarkdown h1 {
        color: #1e3a8a;
    }
    .stMarkdown h2 {
        color: #2563eb;
        padding-top: 0.5rem;
    }
    .stMarkdown h3 {
        color: #3b82f6;
    }
    .review-container {
        background-color: #f0f9ff;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #3b82f6;
        margin-bottom: 1rem;
    }
    .proposal-container {
        background-color: #f0fdf4;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #22c55e;
        margin-bottom: 1rem;
    }
    .validation-container {
        background-color: #fff7ed;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #f59e0b;
        margin-bottom: 1rem;
    }
    .diff-container {
        font-family: monospace;
        white-space: pre-wrap;
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        padding: 1rem;
        border-radius: 0.5rem;
        overflow-x: auto;
    }
    .addition {
        background-color: #dcfce7;
        color: #166534;
        display: inline;
        border-radius: 3px;
        padding: 0 2px;
    }
    .deletion {
        background-color: #fee2e2;
        color: #991b1b;
        display: inline;
        border-radius: 3px;
        padding: 0 2px;
    }
    .diff-stats {
        display: flex;
        justify-content: space-between;
        margin-bottom: 1rem;
        background-color: #f1f5f9;
        padding: 0.75rem;
        border-radius: 0.5rem;
    }
    .diff-stat-item {
        text-align: center;
        padding: 0 0.5rem;
    }
    .diff-stat-value {
        font-size: 1.25rem;
        font-weight: bold;
    }
    .diff-stat-label {
        font-size: 0.875rem;
        color: #64748b;
    }
    .diff-header {
        font-weight: bold;
        color: #64748b;
        margin-bottom: 0.5rem;
    }
    .diff-tabs {
        margin-bottom: 1rem;
    }
    .loading-text {
        color: #4b5563;
        font-style: italic;
    }
    .result-container {
        margin-top: 2rem;
        padding: 1rem;
        background-color: white;
        border-radius: 0.5rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }
    .export-button {
        margin-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)

def simulate_enhancement_process(standard_id, trigger_scenario, category=None, output_file=None):
    """Simulate the enhancement process using the pre-generated output file."""
    # Create placeholders for progress updates
    review_placeholder = st.empty()
    proposal_placeholder = st.empty()
    validation_placeholder = st.empty()
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Show initial status
    review_placeholder.info("🔍 Reviewing standard and identifying enhancement areas...")
    proposal_placeholder.info("🔄 Waiting for review to complete...")
    validation_placeholder.info("🔄 Waiting for proposal generation...")
    status_text.text("Starting enhancement process...")
    
    # Simulate review phase
    for i in range(10):
        progress = i / 30  # First third for review
        progress_bar.progress(progress)
        status_text.text(f"Analyzing standard... ({i+1}/10 steps)")
        time.sleep(0.5)  # Simulate processing time
    
    review_placeholder.success("✅ Review complete!")
    proposal_placeholder.info("✏️ Generating enhancement proposals...")
    
    # Simulate proposal phase
    for i in range(10):
        progress = (i + 10) / 30  # Second third for proposal
        progress_bar.progress(progress)
        status_text.text(f"Generating proposals... ({i+1}/10 steps)")
        time.sleep(0.5)  # Simulate processing time
    
    proposal_placeholder.success("✅ Proposals generated!")
    validation_placeholder.info("⚖️ Validating proposals against Shariah principles...")
    
    # Simulate validation phase
    for i in range(10):
        progress = (i + 20) / 30  # Final third for validation
        progress_bar.progress(progress)
        status_text.text(f"Validating against Shariah principles... ({i+1}/10 steps)")
        time.sleep(0.5)  # Simulate processing time
    
    validation_placeholder.success("✅ Validation complete!")
    progress_bar.progress(1.0)
    status_text.text("Enhancement process completed!")
    
    # Choose the appropriate output file
    if not output_file:
        output_file = get_default_output_file(category)
    
    # Load the pre-generated output
    output_file_path = Path(__file__).parent.parent / output_file
    
    try:
        with open(output_file_path, 'r') as f:
            output_text = f.read()
        
        # Parse the output file to get the results
        results = OutputParser.parse_markdown_sections(output_text)
        
        # Extract original and proposed text for diff visualization
        original_text, proposed_text = OutputParser.extract_original_and_proposed(results['proposal'])
        
        # Generate both simple and enhanced diffs
        results["original_text"] = original_text
        results["proposed_text"] = proposed_text
        results["simple_diff"] = OutputParser.format_text_diff(original_text, proposed_text)
        results["simple_diff_html"] = OutputParser.format_diff_html(results["simple_diff"])
        
        # Generate enhanced diff using the word_diff module
        results["enhanced_diff"] = OutputParser.generate_enhanced_diff(original_text, proposed_text)
        
        # For debugging
        print("Parsing output file:")
        for key, value in results.items():
            if key not in ["standard_id", "enhanced_diff", "simple_diff", "simple_diff_html"]:
                print(f"{key} length: {len(str(value))}")
        
        return results
    except Exception as e:
        st.error(f"Error loading output file: {e}")
        return {
            "standard_id": standard_id,
            "trigger_scenario": trigger_scenario,
            "review": f"Error loading output file: {e}",
            "proposal": "No proposals available due to error",
            "validation": "No validation available due to error"
        }

def display_results(results):
    """Display the enhancement results in a structured way."""
    if not results:
        st.error("No results to display")
        return
    
    # Create tabs for different sections
    tabs = st.tabs(["Overview", "Review Analysis", "Proposed Changes", "Diff View", "Validation", "Cross-Standard Impact"])
    
    # Overview Tab
    with tabs[0]:
        st.header(f"Standards Enhancement Results for FAS {results['standard_id']}")
        
        st.subheader("Trigger Scenario")
        st.write(results["trigger_scenario"])
        
        if "enhanced_diff" in results and results["enhanced_diff"]["stats"]:
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
            # Fallback to traditional metrics
            st.subheader("Summary")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Standard", f"FAS {results['standard_id']}")
            with col2:
                # Extract validator decision
                validation_text = results['validation']
                decision = "PENDING"
                if "APPROVED" in validation_text:
                    decision = "APPROVED ✅"
                elif "REJECTED" in validation_text:
                    decision = "REJECTED ❌"
                elif "NEEDS REVISION" in validation_text:
                    decision = "NEEDS REVISION ⚠️"
                st.metric("Decision", decision)
            with col3:
                # Count the number of proposed changes
                original_text, proposed_text = results.get("original_text", ""), results.get("proposed_text", "")
                if original_text and proposed_text:
                    diff_lines = len(results.get("simple_diff", "").split('\n'))
                    st.metric("Changes", f"{diff_lines} lines")
                else:
                    st.metric("Changes", "Unknown")
        
        st.subheader("Key Findings")
        
        # Extract and display key findings from review
        if "review" in results:
            review_text = results["review"]
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
                
        # Show cross-standard impact summary if available
        if "cross_standard_analysis" in results and "compatibility_matrix" in results:
            st.subheader("Cross-Standard Impact Summary")
            
            # Try to extract a short summary from the analysis
            analysis_text = results["cross_standard_analysis"]
            summary_text = analysis_text.split("\n\n")[0] if "\n\n" in analysis_text else analysis_text
            
            st.write(summary_text[:300] + "..." if len(summary_text) > 300 else summary_text)
            
            # Display a visual representation of the compatibility matrix
            st.subheader("Compatibility Matrix")
            
            matrix = results["compatibility_matrix"]
            if matrix:
                # Create a color-coded matrix display
                cols = st.columns(len(matrix))
                for i, standard in enumerate(matrix):
                    with cols[i]:
                        # Set color based on impact level
                        color = "#f8d7da"  # Red for contradictions
                        text_color = "#721c24"
                        if standard["impact_type"].lower() == "synergy":
                            color = "#d4edda"  # Green for synergies
                            text_color = "#155724"
                        elif standard["impact_type"].lower() == "both":
                            color = "#fff3cd"  # Yellow for both
                            text_color = "#856404"
                        elif standard["impact_type"].lower() == "none":
                            color = "#e2e3e5"  # Gray for none
                            text_color = "#383d41"
                            
                        # Display the standard card
                        st.markdown(
                            f"""
                            <div style="background-color: {color}; color: {text_color}; padding: 10px; 
                                  border-radius: 5px; text-align: center; height: 120px;">
                                <h3>FAS {standard['standard_id']}</h3>
                                <p><b>Impact: {standard['impact_level']}</b></p>
                                <p>{standard['impact_type']}</p>
                            </div>
                            """, 
                            unsafe_allow_html=True
                        )
    
    # Review Analysis Tab
    with tabs[1]:
        st.header("Review Findings")
        st.markdown(f'<div class="review-container">{results["review"]}</div>', unsafe_allow_html=True)
    
    # Proposed Changes Tab
    with tabs[2]:
        st.header("Proposed Enhancements")
        st.markdown(f'<div class="proposal-container">{results["proposal"]}</div>', unsafe_allow_html=True)
        
        if "original_text" in results and "proposed_text" in results:
            st.subheader("Original vs. Proposed Text")
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Original Text:**")
                st.markdown(f'<div class="diff-container">{results["original_text"]}</div>', unsafe_allow_html=True)
            with col2:
                st.markdown("**Proposed Text:**")
                st.markdown(f'<div class="diff-container">{results["proposed_text"]}</div>', unsafe_allow_html=True)
    
    # Diff View Tab
    with tabs[3]:
        st.header("Text Differences")
        
        if "enhanced_diff" in results:
            # Create tabs for different diff views
            diff_tabs = st.tabs(["Word-by-Word", "Inline View", "Sentence Level", "Standard Diff"])
            
            # Word-by-Word Diff Tab
            with diff_tabs[0]:
                st.markdown("### Word-by-Word Comparison")
                st.markdown("This view shows each word-level change with additions in green and deletions in red.")
                
                # Display diff stats
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
                if "word_diff_html" in results["enhanced_diff"]:
                    st.markdown(
                        f'<div class="diff-container">{results["enhanced_diff"]["word_diff_html"]}</div>',
                        unsafe_allow_html=True
                    )
                else:
                    st.warning("Word-by-word diff not available")
            
            # Inline View Tab
            with diff_tabs[1]:
                st.markdown("### Inline Diff")
                st.markdown("This view shows changes inline with character-level precision.")
                
                # Display inline diff
                if "inline_diff_html" in results["enhanced_diff"]:
                    st.markdown(
                        f'<div class="diff-container">{results["enhanced_diff"]["inline_diff_html"]}</div>',
                        unsafe_allow_html=True
                    )
                else:
                    st.warning("Inline diff not available")
            
            # Sentence Level Tab
            with diff_tabs[2]:
                st.markdown("### Sentence-Level Comparison")
                st.markdown("This view compares entire sentences to show changes at a higher level.")
                
                # Display sentence diff
                if "sentence_diff_html" in results["enhanced_diff"]:
                    st.markdown(
                        f'<div class="diff-container">{results["enhanced_diff"]["sentence_diff_html"]}</div>',
                        unsafe_allow_html=True
                    )
                else:
                    st.warning("Sentence-level diff not available")
            
            # Standard Diff Tab
            with diff_tabs[3]:
                st.markdown("### Standard Diff")
                st.markdown("This is a traditional line-by-line diff format.")
                
                if "simple_diff_html" in results:
                    st.markdown(
                        f'<div class="diff-container">{results["simple_diff_html"]}</div>',
                        unsafe_allow_html=True
                    )
                else:
                    st.warning("Standard diff not available")
        
        else:
            # Fallback to simple diff if enhanced diff is not available
            original_text = results.get("original_text", "")
            proposed_text = results.get("proposed_text", "")
            
            if original_text and proposed_text:
                # Generate diff on-the-fly if not already present
                if "simple_diff_html" not in results:
                    simple_diff = OutputParser.format_text_diff(original_text, proposed_text)
                    simple_diff_html = OutputParser.format_diff_html(simple_diff)
                else:
                    simple_diff_html = results["simple_diff_html"]
                
                st.markdown(f"""
                <div class="diff-container">
                    {simple_diff_html}
                </div>
                """, unsafe_allow_html=True)
                
                # Side-by-side comparison (can be kept for compatibility)
                st.subheader("Side-by-Side Comparison")
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("#### Original Text")
                    st.text_area("", original_text, height=300, key="original_text", disabled=True)
                with col2:
                    st.markdown("#### Proposed Text")
                    st.text_area("", proposed_text, height=300, key="proposed_text", disabled=True)
            else:
                st.warning("Could not extract clear original and proposed text sections for visualization. Please check the Proposed Changes tab for the full enhancement details.")
    
    # Validation Tab
    with tabs[4]:
        st.header("Validation Results")
        
        # Try to extract validation decision
        decision = "Undetermined"
        decision_color = "gray"
        if "validation" in results:
            validation_text = results["validation"]
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
        st.markdown(f'<div class="validation-container">{results["validation"]}</div>', unsafe_allow_html=True)
    
    # Cross-Standard Impact Tab
    with tabs[5]:
        st.header("Cross-Standard Impact Analysis")
        
        if "cross_standard_analysis" in results:
            # Display the full analysis
            st.markdown(f'<div class="cross-standard-container">{results["cross_standard_analysis"]}</div>', unsafe_allow_html=True)
            
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
                
                # Display the table with conditional formatting
                st.dataframe(
                    matrix_df, 
                    hide_index=True,
                    column_config={
                        "Standard": st.column_config.TextColumn("Standard"),
                        "Impact Level": st.column_config.TextColumn("Impact Level"),
                        "Impact Type": st.column_config.TextColumn("Impact Type")
                    }
                )
        else:
            st.info("Cross-standard impact analysis was not performed for this enhancement.")
            st.markdown("""
            Cross-standard impact analysis helps identify:
            - How changes to one standard might affect other standards
            - Potential contradictions between standards
            - Opportunities for synergy across standards
            - Areas where consistency can be improved
            
            To get this analysis, re-run the enhancement with cross-standard analysis enabled.
            """)
    
    # Add export functionality
    st.subheader("Export Results")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Export as Markdown", key="export_md", type="primary"):
            markdown_content = f"""# Standards Enhancement Results for FAS {results['standard_id']}

## Trigger Scenario
{results['trigger_scenario']}

## Review Findings
{results['review']}

## Proposed Enhancements
{results['proposal']}

## Validation Results
{results['validation']}"""

            # Add cross-standard analysis if available
            if "cross_standard_analysis" in results:
                markdown_content += f"""

## Cross-Standard Impact Analysis
{results['cross_standard_analysis']}"""
            
            st.download_button(
                label="Download Markdown File",
                data=markdown_content,
                file_name=f"enhancement_fas{results['standard_id']}.md",
                mime="text/markdown",
            )
    
    with col2:
        if st.button("Export as HTML Report", key="export_html", type="primary"):
            original_text = results.get("original_text", "")
            proposed_text = results.get("proposed_text", "")
            
            # Create a simple HTML report
            html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Standards Enhancement Report - FAS {results['standard_id']}</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; margin: 20px; }}
        h1 {{ color: #1e3a8a; }}
        h2 {{ color: #2563eb; margin-top: 20px; }}
        .review-section {{ background-color: #f0f9ff; padding: 15px; border-radius: 5px; border-left: 5px solid #3b82f6; margin-bottom: 20px; }}
        .proposal-section {{ background-color: #f0fdf4; padding: 15px; border-radius: 5px; border-left: 5px solid #22c55e; margin-bottom: 20px; }}
        .validation-section {{ background-color: #fff7ed; padding: 15px; border-radius: 5px; border-left: 5px solid #f59e0b; margin-bottom: 20px; }}
        .cross-standard-section {{ background-color: #eef2ff; padding: 15px; border-radius: 5px; border-left: 5px solid #818cf8; margin-bottom: 20px; }}
        .scenario-section {{ background-color: #f8fafc; padding: 15px; border-radius: 5px; border: 1px solid #e2e8f0; margin-bottom: 20px; }}
        pre {{ white-space: pre-wrap; }}
        .addition {{ color: #166534; background-color: #dcfce7; padding: 2px; }}
        .deletion {{ color: #991b1b; background-color: #fee2e2; padding: 2px; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th, td {{ border: 1px solid #e2e8f0; padding: 8px; text-align: left; }}
        th {{ background-color: #f1f5f9; }}
    </style>
</head>
<body>
    <h1>Standards Enhancement Report - FAS {results['standard_id']}</h1>
    
    <h2>Trigger Scenario</h2>
    <div class="scenario-section">
        <p>{results['trigger_scenario']}</p>
    </div>
    
    <h2>Review Findings</h2>
    <div class="review-section">
        {results['review']}
    </div>
    
    <h2>Proposed Enhancements</h2>
    <div class="proposal-section">
        {results['proposal']}
    </div>
    """
    
            # Add comparison section if we have original and proposed text
            if original_text and proposed_text and "enhanced_diff" in results:
                html_content += f"""
    <h2>Text Comparison</h2>
    <div>
        <h3>Word-by-Word Diff</h3>
        <div style="font-family: monospace; white-space: pre-wrap; background-color: #f8fafc; border: 1px solid #e2e8f0; padding: 1rem; border-radius: 0.5rem;">
            {results["enhanced_diff"].get("inline_diff_html", "Diff not available")}
        </div>
        
        <h3>Original Text</h3>
        <pre>{original_text}</pre>
        
        <h3>Proposed Text</h3>
        <pre>{proposed_text}</pre>
    </div>
    """
            elif original_text and proposed_text:
                html_content += f"""
    <h2>Text Comparison</h2>
    <div>
        <h3>Original Text</h3>
        <pre>{original_text}</pre>
        
        <h3>Proposed Text</h3>
        <pre>{proposed_text}</pre>
    </div>
    """
            
            # Add validation section
            html_content += f"""    
    <h2>Validation Results</h2>
    <div class="validation-section">
        {results['validation']}
    </div>
    """
    
            # Add cross-standard analysis if available
            if "cross_standard_analysis" in results:
                html_content += f"""
    <h2>Cross-Standard Impact Analysis</h2>
    <div class="cross-standard-section">
        {results['cross_standard_analysis']}
    </div>
    """
                
                # Add compatibility matrix if available
                if "compatibility_matrix" in results:
                    html_content += """
    <h3>Compatibility Matrix</h3>
    <table>
        <tr>
            <th>Standard</th>
            <th>Impact Level</th>
            <th>Impact Type</th>
        </tr>
    """
                    
                    for item in results["compatibility_matrix"]:
                        html_content += f"""
        <tr>
            <td>FAS {item['standard_id']}</td>
            <td>{item['impact_level']}</td>
            <td>{item['impact_type']}</td>
        </tr>
    """
                    
                    html_content += """
    </table>
    """
            
            # Complete the HTML
            html_content += f"""    
    <hr>
    <footer>
        <p><small>Generated by AAOIFI Standards Enhancement System (Demo) - {datetime.datetime.now().strftime("%Y-%m-%d")}</small></p>
    </footer>
</body>
</html>"""
            
            st.download_button(
                label="Download HTML Report",
                data=html_content,
                file_name=f"enhancement_report_fas{results['standard_id']}.html",
                mime="text/html",
            )

def main():
    """Main Streamlit app function."""
    st.title("AAOIFI Standards Enhancement System (Demo Version)")
    st.subheader("Improving Islamic Finance Standards with AI")
    
    # Add a notice that this is a demo version
    st.info("⚠️ This is a lightweight demo version using pre-generated results. No actual AI processing is performed.")
    
    # Sidebar for selecting enhancement method and category
    st.sidebar.title("Enhancement Options")
    
    # Category selection
    category = st.sidebar.selectbox(
        "Select Category",
        list(ENHANCEMENT_CATEGORIES.keys()),
        format_func=lambda x: ENHANCEMENT_CATEGORIES[x]
    )
    
    enhancement_method = st.sidebar.radio(
        "Enhancement Method",
        ["Select from Test Cases", "Custom Enhancement"]
    )
    
    # Filter test cases by selected category
    category_test_cases = get_test_cases_by_category(category)
    
    if enhancement_method == "Select from Test Cases":
        if category_test_cases:
            # Create a dropdown for test cases
            test_case_names = [f"{case['name']} (FAS {case['standard_id']})" for case in category_test_cases]
            selected_case_idx = st.sidebar.selectbox("Select a Test Case", range(len(test_case_names)), 
                                                format_func=lambda i: test_case_names[i])
            
            selected_case = category_test_cases[selected_case_idx]
            standard_id = selected_case['standard_id']
            trigger_scenario = selected_case['trigger_scenario']
            output_file = selected_case.get('output_file')
            
            # Display the selected case details
            st.sidebar.markdown("### Selected Case")
            st.sidebar.markdown(f"**Standard:** FAS {standard_id}")
            st.sidebar.markdown(f"**Scenario:** {trigger_scenario[:100]}...")
        else:
            st.sidebar.warning(f"No test cases available for {ENHANCEMENT_CATEGORIES[category]}")
            standard_id = ""
            trigger_scenario = ""
            output_file = None
            
    else:  # Custom Enhancement
        st.sidebar.markdown("### Custom Enhancement")
        standard_id = st.sidebar.selectbox(
            "Select Standard",
            ["4", "7", "10", "28", "32"],
            format_func=lambda x: f"FAS {x}"
        )
        
        trigger_scenario = st.sidebar.text_area(
            "Describe the Trigger Scenario",
            height=150,
            help="Describe a situation that might require enhancing the standard"
        )
        
        # For custom, use default output file for the category
        output_file = get_default_output_file(category)
    
    # Main content
    if 'results' not in st.session_state:
        st.session_state.results = None
    
    # Button to start enhancement
    run_enhancement = st.button("Simulate Enhancement Process", type="primary")
    
    if run_enhancement:
        if not trigger_scenario:
            st.error("Please provide a trigger scenario before starting the enhancement process.")
        else:
            with st.spinner("Simulating enhancement process..."):
                # Use the category's output file if available
                results = simulate_enhancement_process(standard_id, trigger_scenario, category, output_file)
                st.session_state.results = results
                
                # Success message
                st.success("Enhancement process completed successfully!")
    
    # Display results if available
    if st.session_state.results:
        display_results(st.session_state.results)

if __name__ == "__main__":
    main() 