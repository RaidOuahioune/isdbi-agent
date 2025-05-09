import streamlit as st
import sys
import os
import time
import re
import json
import datetime
from pathlib import Path

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
    .past-enhancement {
        background-color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        border-left: 5px solid #6366f1;
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
        <p><small>Generated by AAOIFI Standards Enhancement System - {datetime.datetime.now().strftime("%Y-%m-%d")}</small></p>
    </footer>
</body>
</html>"""
            
            st.download_button(
                label="Download HTML Report",
                data=html_content,
                file_name=f"enhancement_report_fas{results['standard_id']}.html",
                mime="text/html",
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

def main():
    """Main Streamlit app function."""
    st.title("AAOIFI Standards Enhancement System")
    
    # Sidebar for navigation
    st.sidebar.title("Enhancement Options")
    
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
                    results = run_enhancement_with_progress(standard_id, trigger_scenario)
                    st.session_state.results = results
                    
                    # Success message
                    st.success("Enhancement process completed successfully!")
        
        # Display results if available
        if st.session_state.results:
            display_results(st.session_state.results)
            
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