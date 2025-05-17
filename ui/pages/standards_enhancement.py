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
import asyncio
import logging

# Add the parent directory to the path so we can import from the main project
parent_dir = str(Path(__file__).parent.parent.parent)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Project imports - from main directory
from enhancement import run_standards_enhancement, ENHANCEMENT_TEST_CASES, find_test_case_by_keyword
from components.orchestration.enhancement_orchestrator import EnhancementOrchestrator  # Add this line

# Local imports
from ui.components.enhancement_results import display_results, display_cross_standard_tab, display_past_enhancement
from ui.states.session_state import init_enhancement_state, set_enhancement_results, get_enhancement_results
from ui.utils.enhancement_utils import save_enhancement, load_past_enhancements, create_export_markdown, create_export_html
from ui.styles.main import load_css
from ui.progress_monitor import run_enhancement_with_monitoring, create_progress_components

# Add some custom CSS for the standardized proposal format
def get_enhanced_css():
    """Add custom CSS for the standardized proposal format"""
    return """
    <style>
        /* Proposal formatting */
        .proposal-container h1 {
            background-color: #f0f7ff; 
            padding: 10px;
            border-left: 4px solid #3b82f6;
            margin-top: 25px;
        }
        
        .proposal-container h2 {
            color: #3b82f6;
            border-bottom: 1px solid #e5e7eb;
            padding-bottom: 5px;
            margin-top: 20px;
        }
        
        .proposal-container strong {
            color: #1e40af;
        }
        
        /* Styling for Original Text and Proposed Text */
        .proposal-container h2:contains("Original Text") + p,
        .proposal-container h2:contains("Proposed Modified Text") + p {
            background-color: #f9fafb;
            padding: 15px;
            border-radius: 5px;
            border: 1px solid #e5e7eb;
            font-family: 'Courier New', monospace;
        }
        
        /* Make diff visualization more readable */
        .diff-container {
            padding: 15px;
            border-radius: 5px;
            border: 1px solid #e5e7eb;
            font-family: 'Courier New', monospace;
            white-space: pre-wrap;
            overflow-x: auto;
        }
        
        .deletion {
            background-color: #fee2e2;
            text-decoration: line-through;
            color: #991b1b;
        }
        
        .addition {
            background-color: #dcfce7;
            color: #166534;
            font-weight: 500;
        }
        
        /* Stats boxes */
        .diff-stats {
            display: flex;
            justify-content: space-between;
            margin-bottom: 20px;
        }
        
        .diff-stat-item {
            text-align: center;
            background-color: #f9fafb;
            padding: 10px;
            border-radius: 5px;
            flex: 1;
            margin: 0 5px;
        }
        
        .diff-stat-value {
            font-size: 1.5rem;
            font-weight: bold;
            color: #3b82f6;
        }
        
        .diff-stat-label {
            font-size: 0.8rem;
            color: #4b5563;
        }
    </style>
    """

async def run_enhancement_process(orchestrator, standard_id, trigger_scenario, progress_callback, include_cross):
    """Run the enhancement process asynchronously."""
    try:
        results = await orchestrator.run_enhancement(
            standard_id=standard_id,
            trigger_scenario=trigger_scenario,
            progress_callback=progress_callback,
            include_cross_standard_analysis=include_cross
        )
        return results
    except Exception as e:
        logging.error(f"Error in enhancement process: {str(e)}")
        raise

def update_progress(phase: str, detail: str, components: dict):
    """Update progress components based on phase and detail."""
    if phase == "review_start":
        components["review"].info("🔍 Reviewing standard...")
        components["progress_bar"].progress(0.2)
    elif phase == "review_complete":
        components["review"].success("✅ Review complete")
        components["proposal"].info("✏️ Generating proposals...")
        components["progress_bar"].progress(0.4)
    elif phase == "proposal_complete":
        components["proposal"].success("✅ Proposals generated")
        components["validation"].info("⚖️ Validating changes...")
        components["progress_bar"].progress(0.6)
    elif phase == "validation_complete":
        components["validation"].success("✅ Validation complete")
        components["progress_bar"].progress(1.0)
        components["progress_status"].success("Enhancement process completed!")
    
    if detail:
        components["progress_status"].info(detail)

def render_standards_enhancement_page():
    st.title("Standards Enhancement")
    st.markdown(
        "This feature helps analyze and enhance AAOIFI Financial Accounting Standards "
        "to address new scenarios and challenges."
    )

    # Create two columns for settings
    settings_col1, settings_col2 = st.columns(2)

    # Left column: Test case selection
    with settings_col1:
        st.subheader("Select Test Case")
        test_cases = {case['name']: case for case in ENHANCEMENT_TEST_CASES}
        selected_case = st.selectbox(
            "Choose a test case or enter custom scenario below:",
            options=["Custom"] + list(test_cases.keys()),
            help="Select a predefined test case or choose 'Custom' to enter your own"
        )

        if selected_case == "Custom":
            st.session_state.standard_id = st.selectbox(
                "Standard ID",
                ["4", "7", "10", "28", "32"],
                help="Select the FAS standard to enhance"
            )
            st.session_state.trigger_scenario = st.text_area(
                "Trigger Scenario",
                help="Describe the situation that requires enhancing the standard"
            )
        else:
            case = test_cases[selected_case]
            st.session_state.standard_id = case['standard_id']
            st.session_state.trigger_scenario = case['trigger_scenario']
            st.markdown(f"**Selected FAS:** {case['standard_id']}")
            st.markdown("**Scenario:**")
            st.info(case['trigger_scenario'])

    # Right column: Analysis options
    with settings_col2:
        st.subheader("Enhancement Options")
        st.session_state.include_cross = st.checkbox(
            "Include cross-standard analysis",
            value=True,
            help="Analyze impact on related standards"
        )

    # Expert selection section
    st.subheader("Select Experts for Discussion")
    expert_cols = st.columns(3)
    
    # Initialize expert selection state if not exists
    if "selected_experts" not in st.session_state:
        st.session_state.selected_experts = {
            "shariah": True,     # Required
            "finance": True,     # Required
            "standards": True,   # Required
            "practical": True,   # Default enabled
            "risk": False,       # Default disabled
        }
    
    # Create checkboxes for each expert
    with expert_cols[0]:
        st.session_state.selected_experts["shariah"] = st.checkbox(
            "Shariah Expert", 
            value=st.session_state.selected_experts["shariah"],
            disabled=True,  # Always required
            help="Required: Reviews Shariah compliance and principles"
        )
        st.session_state.selected_experts["finance"] = st.checkbox(
            "Finance Expert", 
            value=st.session_state.selected_experts["finance"],
            disabled=True,  # Always required
            help="Required: Reviews accounting and financial implications"
        )
        
    with expert_cols[1]:
        st.session_state.selected_experts["standards"] = st.checkbox(
            "Standards Expert", 
            value=st.session_state.selected_experts["standards"],
            disabled=True,  # Always required
            help="Required: Reviews standards structure and consistency"
        )
        st.session_state.selected_experts["practical"] = st.checkbox(
            "Practical Expert", 
            value=st.session_state.selected_experts["practical"],
            help="Reviews implementation feasibility and industry practices"
        )
        
    with expert_cols[2]:
        st.session_state.selected_experts["risk"] = st.checkbox(
            "Risk Expert", 
            value=st.session_state.selected_experts["risk"],
            help="Reviews risk assessment and mitigation strategies"
        )

    # Validation before running
    if not st.session_state.standard_id or not st.session_state.trigger_scenario:
        st.warning("Please select a test case or enter custom scenario details")
        return

    # Handle enhancement process
    if st.button("Run Enhancement"):
        try:
            # Create orchestrator with selected experts
            orchestrator = EnhancementOrchestrator(selected_experts=st.session_state.selected_experts)
            
            # Create progress components
            progress_components = create_progress_components()
            
            # Set up asyncio event loop
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            # Run enhancement with progress monitoring
            results = loop.run_until_complete(
                run_enhancement_process(
                    orchestrator=orchestrator,
                    standard_id=st.session_state.standard_id,
                    trigger_scenario=st.session_state.trigger_scenario,
                    progress_callback=lambda phase, detail: update_progress(phase, detail, progress_components),
                    include_cross=st.session_state.include_cross
                )
            )

            if results:
                # Display results
                display_results(results)
                
                # Add export options
                st.subheader("Export Results")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.download_button(
                        "Export as Markdown",
                        create_export_markdown(results),
                        f"enhancement_fas{results['standard_id']}.md",
                        "text/markdown"
                    )
                
                with col2:
                    st.download_button(
                        "Export as HTML Report",
                        create_export_html(results),
                        f"enhancement_report_fas{results['standard_id']}.html",
                        "text/html"
                    )
            else:
                st.error("Enhancement process failed to return results")
                
        except Exception as e:
            st.error(f"Error during enhancement process: {str(e)}")
            logging.error(f"Enhancement error: {str(e)}", exc_info=True)

if __name__ == "__main__":
    render_standards_enhancement_page()