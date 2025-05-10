"""
Standards Enhancement page for the Streamlit application.
"""

import streamlit as st
import sys
import os
import time
import datetime
from pathlib import Path
import re

# Add the parent directory to the path so we can import from the main project
parent_dir = str(Path(__file__).parent.parent.parent)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Project imports - from main directory
from enhancement import run_standards_enhancement, ENHANCEMENT_TEST_CASES, find_test_case_by_keyword

# Local imports
from ui.components.enhancement_results import display_results, display_cross_standard_tab, display_past_enhancement
from ui.states.session_state import init_enhancement_state, set_enhancement_results, get_enhancement_results
from ui.utils.enhancement_utils import save_enhancement, load_past_enhancements, create_export_markdown, create_export_html
from ui.styles.main import load_css

def render_standards_enhancement_page():
    """Render the Standards Enhancement page."""
    # Initialize session state
    init_enhancement_state()
    
    # Set page configuration
    st.set_page_config(
        page_title="AAOIFI Standards Enhancement",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Apply CSS
    st.markdown(load_css(), unsafe_allow_html=True)
    
    # Page title
    st.title("📊 AAOIFI Standards Enhancement System")
    
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
                    try:
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
                        
                        # Pre-process the results to ensure diffs are generated
                        from ui.output_parser import OutputParser
                        
                        # Ensure results is a dictionary
                        if not isinstance(results, dict):
                            results = {"raw_output": str(results)}
                        
                        processed_results = OutputParser.parse_results_from_agents(results)
                        
                        # Save results to session state
                        set_enhancement_results(processed_results)
                        
                        # Save enhancement to file
                        save_enhancement(processed_results)
                        
                        # Success message
                        st.success("Standards enhancement completed successfully!")
                    except Exception as e:
                        progress_container.empty()
                        status_text.empty()
                        st.error(f"An error occurred during the enhancement process: {str(e)}")
        
        # Display results if available
        results = get_enhancement_results()
        if results:
            # Create tabs for displaying results
            tab_names = ["Overview", "Review Analysis", "Proposed Changes", "Diff View", "Validation"]
            
            # Add cross-standard impact tab if the analysis is available
            has_cross_standard = "cross_standard_analysis" in results and results["cross_standard_analysis"]
            if has_cross_standard:
                tab_names.append("Cross-Standard Impact")
            
            tabs = st.tabs(tab_names)
            
            # Display the results in the Overview tab
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
                    st.warning("Diff statistics not available. This might be because the original and proposed text extraction failed.")
                
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
                has_simple_diff = "simple_diff_html" in results and results["simple_diff_html"]
                
                # If no diff information at all, show a message
                if not has_enhanced_diff and not has_simple_diff:
                    st.warning("No diff visualization available. This could be because the original and proposed text extraction failed or the texts are identical.")
                    
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
                        
                        # Provide a reason why diff might not be available
                        if original_text and proposed_text:
                            if original_text == proposed_text:
                                st.info("The original and proposed texts are identical, so no differences to display.")
                            else:
                                st.info("Diff generation failed but original and proposed texts are available for comparison.")
                        elif not original_text and not proposed_text:
                            st.error("Both original and proposed texts are missing. Cannot generate diff.")
                        else:
                            st.warning("One of the texts is missing, making diff generation incomplete.")
                else:
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
                            if word_diff_html and len(word_diff_html) > 10:  # Simple check to avoid empty diffs
                                st.markdown(f'<div class="diff-container">{word_diff_html}</div>', unsafe_allow_html=True)
                            else:
                                st.warning("Word-by-word diff visualization could not be generated.")
                        
                        # Inline View Tab
                        with diff_tabs[1]:
                            st.markdown("### Inline Diff")
                            st.markdown("This view shows changes inline with character-level precision.")
                            
                            # Display inline diff
                            inline_diff_html = results["enhanced_diff"].get("inline_diff_html", "<div>Inline diff not available</div>")
                            if inline_diff_html and len(inline_diff_html) > 10:
                                st.markdown(f'<div class="diff-container">{inline_diff_html}</div>', unsafe_allow_html=True)
                            else:
                                st.warning("Inline diff visualization could not be generated.")
                        
                        # Sentence Level Tab
                        with diff_tabs[2]:
                            st.markdown("### Sentence-Level Comparison")
                            st.markdown("This view compares entire sentences to show changes at a higher level.")
                            
                            # Display sentence diff
                            sentence_diff_html = results["enhanced_diff"].get("sentence_diff_html", "<div>Sentence-level diff not available</div>")
                            if sentence_diff_html and len(sentence_diff_html) > 10:
                                st.markdown(f'<div class="diff-container">{sentence_diff_html}</div>', unsafe_allow_html=True)
                            else:
                                st.warning("Sentence-level diff visualization could not be generated.")
                        
                        # Standard Diff Tab
                        with diff_tabs[3]:
                            st.markdown("### Standard Diff")
                            st.markdown("This is a traditional line-by-line diff format.")
                            
                            simple_diff_html = results.get("simple_diff_html", "<div>Standard diff not available</div>")
                            if simple_diff_html and len(simple_diff_html) > 10:
                                st.markdown(f'<div class="diff-container">{simple_diff_html}</div>', unsafe_allow_html=True)
                            else:
                                st.warning("Standard diff visualization could not be generated.")
                    
                    else:
                        # Fallback to simple diff if enhanced diff is not available
                        if has_simple_diff:
                            st.markdown("### Text Differences")
                            st.markdown(f'<div class="diff-container">{results["simple_diff_html"]}</div>', unsafe_allow_html=True)
                        else:
                            st.warning("No diff visualization available.")
            
            # Validation Tab
            with tabs[4]:
                st.header("Validation Results")
                
                # Try to extract validation decision
                decision = "Undetermined"
                decision_color = "gray"
                
                validation_text = results.get("validation", "")
                if validation_text:
                    # Look for direct decision words with word boundaries
                    if re.search(r'\bAPPROVED\b', validation_text, re.IGNORECASE):
                        decision = "APPROVED"
                        decision_color = "green"
                    elif re.search(r'\bREJECTED\b', validation_text, re.IGNORECASE):
                        decision = "REJECTED"
                        decision_color = "red"
                    elif re.search(r'\bNEEDS REVISION\b', validation_text, re.IGNORECASE):
                        decision = "NEEDS REVISION"
                        decision_color = "orange"
                    # Look for additional phrasings that might indicate approval/rejection
                    elif re.search(r'the proposed enhancement[s]? (?:is|are) approved', validation_text, re.IGNORECASE):
                        decision = "APPROVED"
                        decision_color = "green"
                    elif re.search(r'proposal[s]? (?:is|are) valid', validation_text, re.IGNORECASE):
                        decision = "APPROVED" 
                        decision_color = "green"
                    elif re.search(r'enhancement[s]? (?:is|are) rejected', validation_text, re.IGNORECASE):
                        decision = "REJECTED"
                        decision_color = "red"
                    elif re.search(r'require[s]? further revision', validation_text, re.IGNORECASE):
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
            
            # Cross-Standard Impact tab - fixed tab index logic
            if has_cross_standard and len(tab_names) > 5:  # Using tab_names length to get correct index
                with tabs[5]:  # Cross-standard tab will be at index 5 if it exists
                    st.header("Cross-Standard Impact Analysis")
                    cross_standard_text = results.get("cross_standard_analysis", "")
                    st.markdown(f'<div class="cross-standard-container">{cross_standard_text}</div>', unsafe_allow_html=True)
                    
                    # If there's a compatibility matrix, display it
                    if "compatibility_matrix" in results:
                        st.subheader("Compatibility Matrix")
                        try:
                            matrix_data = results["compatibility_matrix"]
                            # Check if it's a valid data structure for a table
                            if isinstance(matrix_data, list) and len(matrix_data) > 0:
                                st.table(matrix_data)
                            else:
                                st.info("Compatibility matrix data is not in a suitable format for display.")
                        except Exception as e:
                            st.error(f"Error displaying compatibility matrix: {str(e)}")
            
            # Export section
            st.subheader("Export Results")
            
            col1, col2 = st.columns(2)
            
            with col1:
                markdown_content = create_export_markdown(results)
                st.download_button(
                    label="Export as Markdown",
                    data=markdown_content,
                    file_name=f"enhancement_fas{results['standard_id']}.md",
                    mime="text/markdown"
                )
            
            with col2:
                html_content = create_export_html(results)
                st.download_button(
                    label="Export as HTML Report",
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
    render_standards_enhancement_page() 