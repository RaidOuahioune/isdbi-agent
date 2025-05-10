"""
Standards Enhancement page for the Streamlit application.
"""

import streamlit as st
import sys
import os
import time
import datetime
from pathlib import Path

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
                    
                    # Save results to session state
                    set_enhancement_results(results)
                    
                    # Save enhancement to file
                    save_enhancement(results)
                    
                    # Success message
                    st.success("Standards enhancement completed successfully!")
        
        # Display results if available
        results = get_enhancement_results()
        if results:
            # Create tabs for displaying results
            tabs = ["Overview", "Review Analysis", "Proposed Changes", "Diff View", "Validation"]
            
            # Add cross-standard impact tab if the analysis is available
            if "cross_standard_analysis" in results:
                tabs.append("Cross-Standard Impact")
            
            selected_tab = st.tabs(tabs)
            
            # Display the results using the results component
            display_results(results)
            
            # Add the cross-standard impact tab
            if "cross_standard_analysis" in results and len(selected_tab) > 5:
                with selected_tab[5]:
                    display_cross_standard_tab(results)
            
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