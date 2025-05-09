import streamlit as st
import sys
import os
import time
import re
import json
import datetime
from pathlib import Path
import pandas as pd

# Add the parent directory to the path so we can import from the main project
sys.path.append(str(Path(__file__).parent.parent))

from enhancement import run_standards_enhancement, ENHANCEMENT_TEST_CASES, find_test_case_by_keyword
from ui.progress_monitor import create_progress_components, run_enhancement_with_monitoring
from ui.output_parser import OutputParser

# Set page configuration
st.set_page_config(
    page_title="AAOIFI Standards Enhancement",
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
    .past-enhancement {
        background-color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        border-left: 5px solid #6366f1;
    }
    .cross-standard-container {
        background-color: #eef2ff;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #818cf8;
        margin-bottom: 1rem;
    }
    .compatibility-table {
        width: 100%;
        border-collapse: collapse;
        margin: 20px 0;
        font-family: Arial, sans-serif;
    }
    .compatibility-table th {
        background-color: #f1f5f9;
        padding: 12px 15px;
        text-align: left;
        border: 1px solid #e2e8f0;
    }
    .compatibility-table td {
        padding: 12px 15px;
        border: 1px solid #e2e8f0;
    }
    .impact-high {
        font-weight: bold;
        color: #dc2626;
    }
    .impact-medium {
        font-weight: bold;
        color: #d97706;
    }
    .impact-low {
        font-weight: bold;
        color: #059669;
    }
    .impact-none {
        color: #6b7280;
    }
    .contradiction {
        background-color: #fee2e2;
    }
    .synergy {
        background-color: #d1fae5;
    }
    .both {
        background-color: #fff7ed;
    }
    .none {
        background-color: #f3f4f6;
    }
</style>
""", unsafe_allow_html=True)

# Create directory for storing past enhancements if it doesn't exist
ENHANCEMENTS_DIR = Path(__file__).parent.parent / "past_enhancements"
ENHANCEMENTS_DIR.mkdir(exist_ok=True)

def save_enhancement(results):
    """Save enhancement results to a file for future reference."""
    if not results:
        return False
    
    # Create a unique filename with timestamp and standard ID
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"fas{results['standard_id']}_{timestamp}.json"
    filepath = ENHANCEMENTS_DIR / filename
    
    # Create metadata
    metadata = {
        "timestamp": timestamp,
        "standard_id": results['standard_id'],
        "trigger_scenario": results['trigger_scenario'],
        "decision": "APPROVED" if "APPROVED" in results['validation'] else 
                    "REJECTED" if "REJECTED" in results['validation'] else "NEEDS REVISION"
    }
    
    # Save the full results
    enhancement_data = {
        "metadata": metadata,
        "results": results
    }
    
    try:
        with open(filepath, 'w') as f:
            json.dump(enhancement_data, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving enhancement: {e}")
        return False

def load_past_enhancements():
    """Load all saved enhancement results."""
    enhancements = []
    
    # List all JSON files in the directory
    for file in ENHANCEMENTS_DIR.glob("*.json"):
        try:
            with open(file, 'r') as f:
                data = json.load(f)
                # Add the filename for reference
                data["filename"] = file.name
                enhancements.append(data)
        except Exception as e:
            print(f"Error loading {file}: {e}")
    
    # Sort by timestamp (newest first)
    enhancements.sort(key=lambda x: x["metadata"]["timestamp"], reverse=True)
    return enhancements

def run_enhancement_with_progress(standard_id, trigger_scenario):
    """Run the enhancement process with progress updates."""
    
    # Create progress components
    components = create_progress_components()
    
    # Run enhancement with monitoring
    results = run_enhancement_with_monitoring(
        standard_id, 
        trigger_scenario, 
        run_standards_enhancement,
        components
    )
    
    # Save successful enhancement
    save_enhancement(results)
    
    return results

def display_results(results):
    """Display the enhancement results in a structured way."""
    if not results:
        st.error("No results to display")
        return
    
    # Create tabs for different sections
    tabs = st.tabs(["Overview", "Review Analysis", "Proposed Changes", "Diff View", "Validation"])
    
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
            if "simple_diff_html" in results:
                st.markdown("### Text Differences")
                st.markdown(
                    f'<div class="diff-container">{results["simple_diff_html"]}</div>',
                    unsafe_allow_html=True
                )
            else:
                st.warning("No diff visualization available")
    
    # Validation Tab
    with tabs[4]:
        st.header("Validation Results")
        
        # Try to extract validation decision
        decision = "Undetermined"
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

def main():
    """Main Streamlit app function."""
    st.title("AAOIFI Standards Enhancement System")
    
    # Sidebar for navigation
    st.sidebar.title("Enhancement Options")
    
    # Add cross-standard impact analysis parameter to the sidebar
    include_cross_standard = st.sidebar.checkbox(
        "Include Cross-Standard Impact Analysis", 
        value=True, 
        help="Analyze how the enhancement might impact other related standards"
    )
    
    # Choose between new enhancement and past enhancements
    mode = st.sidebar.radio(
        "Mode",
        ["New Enhancement", "View Past Enhancements"]
    )
    
    if mode == "New Enhancement":
        enhancement_method = st.sidebar.radio(
            "Enhancement Method",
            ["Select from Test Cases", "Custom Enhancement"]
        )
        
        if enhancement_method == "Select from Test Cases":
            # Create a dropdown for test cases
            test_case_names = [f"{case['name']} (FAS {case['standard_id']})" for case in ENHANCEMENT_TEST_CASES]
            selected_case_idx = st.sidebar.selectbox("Select a Test Case", range(len(test_case_names)), 
                                                format_func=lambda i: test_case_names[i])
            
            selected_case = ENHANCEMENT_TEST_CASES[selected_case_idx]
            standard_id = selected_case['standard_id']
            trigger_scenario = selected_case['trigger_scenario']
            
            # Display the selected case details
            st.sidebar.markdown("### Selected Case")
            st.sidebar.markdown(f"**Standard:** FAS {standard_id}")
            st.sidebar.markdown(f"**Scenario:** {trigger_scenario[:100]}...")
            
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
        
        # Main content
        if 'results' not in st.session_state:
            st.session_state.results = None
        
        # Button to start enhancement
        run_enhancement = st.button("Start Enhancement Process", type="primary")
        
        if run_enhancement:
            if not trigger_scenario:
                st.error("Please provide a trigger scenario before starting the enhancement process.")
            else:
                with st.spinner("Running enhancement process..."):
                    # Create progress container
                    progress_container = st.empty()
                    status_text = st.empty()
                    
                    # Define progress callback
                    def progress_callback(phase, detail=None):
                        if phase == "review_start":
                            progress_container.progress(0.1)
                            status_text.text("Reviewing standard and identifying enhancement areas...")
                        elif phase == "review_complete":
                            progress_container.progress(0.3)
                            status_text.text("Generating enhancement proposals...")
                        elif phase == "proposal_complete":
                            progress_container.progress(0.5)
                            status_text.text("Validating proposals against Shariah principles...")
                        elif phase == "validation_complete":
                            progress_container.progress(0.7)
                            status_text.text("Validation complete")
                            if include_cross_standard:
                                status_text.text("Analyzing cross-standard impacts...")
                        elif phase == "cross_analysis_start":
                            progress_container.progress(0.8)
                            status_text.text("Analyzing impacts on other standards...")
                        elif phase == "cross_analysis_complete":
                            progress_container.progress(1.0)
                            status_text.text("Enhancement process completed!")
                    
                    # Run the enhancement process
                    results = run_standards_enhancement(
                        standard_id, 
                        trigger_scenario, 
                        progress_callback=progress_callback,
                        include_cross_standard_analysis=include_cross_standard
                    )
                    
                    # Complete the progress bar
                    progress_container.progress(1.0)
                    status_text.text("Enhancement process completed!")
                    time.sleep(0.5)
                    
                    # Clear progress indicators
                    progress_container.empty()
                    status_text.empty()
                    
                    # Update the session state
                    st.session_state.results = results
                    
                    # Success message
                    st.success("Standards enhancement completed successfully!")
        
        # Display results if available
        if st.session_state.results:
            results = st.session_state.results
            
            # Create tabs for displaying results
            tabs = ["Overview", "Review Analysis", "Proposed Changes", "Diff View", "Validation"]
            
            # Add cross-standard impact tab if the analysis is available
            if "cross_standard_analysis" in results:
                tabs.append("Cross-Standard Impact")
            
            tab_overview, tab_review, tab_proposal, tab_validation, *extra_tabs = st.tabs(tabs)
            
            # Overview Tab
            with tab_overview:
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
                
                # Add cross-standard impact summary to overview if available
                if "cross_standard_analysis" in results and "compatibility_matrix" in results:
                    st.subheader("Cross-Standard Impact Summary")
                    
                    # Try to extract a summary from the analysis
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
                                # Set color based on impact type
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
            with tab_review:
                st.header("Review Findings")
                st.markdown(f'<div class="review-container">{results["review"]}</div>', unsafe_allow_html=True)
            
            # Proposed Changes Tab
            with tab_proposal:
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
            with tab_validation:
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
                
            # Add the cross-standard impact tab
            if "cross_standard_analysis" in results and extra_tabs:
                tab_cross_standard = extra_tabs[0]
                with tab_cross_standard:
                    st.header("Cross-Standard Impact Analysis")
                    
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
            
            # Export section
            st.subheader("Export Results")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("Export as Markdown", key="export_md"):
                    # Build markdown content
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
                    
                    # Create download button
                    st.download_button(
                        label="Download Markdown",
                        data=markdown_content,
                        file_name=f"enhancement_fas{results['standard_id']}.md",
                        mime="text/markdown"
                    )
            
            with col2:
                if st.button("Export as HTML Report", key="export_html"):
                    # Create HTML report
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
        <p><small>Generated by AAOIFI Standards Enhancement System - {datetime.datetime.now().strftime("%Y-%m-%d")}</small></p>
    </footer>
</body>
</html>"""
                    
                    # Create download button
                    st.download_button(
                        label="Download HTML Report",
                        data=html_content,
                        file_name=f"enhancement_report_fas{results['standard_id']}.html",
                        mime="text/html",
                    )
            
    else:  # View Past Enhancements
        st.subheader("Past Enhancement Results")
        
        # Load past enhancements
        enhancements = load_past_enhancements()
        
        if not enhancements:
            st.info("No past enhancements found.")
        else:
            # Create a dropdown for selecting a past enhancement
            enhancement_options = [
                f"FAS {e['metadata']['standard_id']} - {datetime.datetime.strptime(e['metadata']['timestamp'], '%Y%m%d_%H%M%S').strftime('%Y-%m-%d %H:%M')}"
                for e in enhancements
            ]
            
            selected_idx = st.selectbox(
                "Select a past enhancement to view:",
                range(len(enhancement_options)),
                format_func=lambda i: enhancement_options[i]
            )
            
            # Display the selected enhancement
            display_past_enhancement(enhancements[selected_idx])

if __name__ == "__main__":
    main() 