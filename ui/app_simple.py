import streamlit as st
import sys
import os
import time
import re
import json
import datetime
from pathlib import Path
from output_parser import OutputParser
from category_config import (
    ENHANCEMENT_CATEGORIES, 
    get_test_cases_by_category,
    get_default_output_file
)

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
        display: block;
        border-radius: 3px;
        margin: 2px 0;
    }
    .deletion {
        background-color: #fee2e2;
        color: #991b1b;
        display: block;
        border-radius: 3px;
        margin: 2px 0;
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
        
        # For debugging
        print("Parsing output file:")
        for key, value in results.items():
            if key != "standard_id":
                print(f"{key} length: {len(value)}")
        
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
    tabs = st.tabs(["Overview", "Review Analysis", "Proposed Changes", "Diff View", "Validation"])
    
    # Overview Tab
    with tabs[0]:
        st.header(f"Standards Enhancement Results for FAS {results['standard_id']}")
        
        st.subheader("Trigger Scenario")
        st.write(results['trigger_scenario'])
        
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
            original_text, proposed_text = OutputParser.extract_original_and_proposed(results['proposal'])
            if original_text and proposed_text:
                diff_lines = OutputParser.format_text_diff(original_text, proposed_text).count('\n')
                st.metric("Changes", f"{diff_lines} lines")
            else:
                st.metric("Changes", "Unknown")
    
    # Review Analysis Tab
    with tabs[1]:
        st.header("Review Analysis")
        st.markdown(f"""
        <div class="review-container">
            {results['review']}
        </div>
        """, unsafe_allow_html=True)
    
    # Proposed Changes Tab
    with tabs[2]:
        st.header("Proposed Enhancements")
        st.markdown(f"""
        <div class="proposal-container">
            {results['proposal']}
        </div>
        """, unsafe_allow_html=True)
    
    # Diff View Tab
    with tabs[3]:
        st.header("Visual Diff of Changes")
        original_text, proposed_text = OutputParser.extract_original_and_proposed(results['proposal'])
        if original_text and proposed_text:
            diff_text = OutputParser.format_text_diff(original_text, proposed_text)
            st.markdown(f"""
            <div class="diff-container">
                {OutputParser.format_diff_html(diff_text)}
            </div>
            """, unsafe_allow_html=True)
            
            # Side-by-side comparison
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
        st.markdown(f"""
        <div class="validation-container">
            {results['validation']}
        </div>
        """, unsafe_allow_html=True)
    
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
{results['validation']}
"""
            st.download_button(
                label="Download Markdown File",
                data=markdown_content,
                file_name=f"enhancement_fas{results['standard_id']}.md",
                mime="text/markdown",
            )
    
    with col2:
        if st.button("Export as HTML Report", key="export_html", type="primary"):
            original_text, proposed_text = OutputParser.extract_original_and_proposed(results['proposal'])
            
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
        .scenario-section {{ background-color: #f8fafc; padding: 15px; border-radius: 5px; border: 1px solid #e2e8f0; margin-bottom: 20px; }}
        pre {{ white-space: pre-wrap; }}
        .addition {{ color: #166534; background-color: #dcfce7; padding: 2px; }}
        .deletion {{ color: #991b1b; background-color: #fee2e2; padding: 2px; }}
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
            if original_text and proposed_text:
                html_content += f"""
    <h2>Text Comparison</h2>
    <div>
        <h3>Original Text</h3>
        <pre>{original_text}</pre>
        
        <h3>Proposed Text</h3>
        <pre>{proposed_text}</pre>
    </div>
    """
            
            # Complete the HTML
            html_content += f"""    
    <h2>Validation Results</h2>
    <div class="validation-section">
        {results['validation']}
    </div>
    
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