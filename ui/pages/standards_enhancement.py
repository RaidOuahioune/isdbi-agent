"""
Standards Enhancement page for the Streamlit application.
"""

import streamlit as st
import sys
import os
import time  # Keep for potential delays if needed
import datetime  # Keep for formatting timestamps
from pathlib import Path
import re
import asyncio
import logging
import dataclasses  # For converting dataclass to dict if needed
from typing import Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Add the parent directory to the path so we can import from the main project
parent_dir = str(Path(__file__).resolve().parent.parent.parent)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Project imports
try:
    # Assuming enhancement.py might contain ENHANCEMENT_TEST_CASES
    from enhancement import ENHANCEMENT_TEST_CASES
except ImportError:
    logging.warning(
        "enhancement.py not found or ENHANCEMENT_TEST_CASES not defined. Test cases will be unavailable."
    )
    ENHANCEMENT_TEST_CASES = []

from components.orchestration.enhancement_orchestrator import EnhancementOrchestrator
import json

# Local imports
from ui.components.enhancement_results import (
    display_results,
    display_past_enhancement,
)  # display_cross_standard_tab might be part of display_results
from ui.states.session_state import (
    init_enhancement_state,
    set_enhancement_results,
    get_enhancement_results,
    get_committee_edit_text,
    set_committee_edit_text,
    get_committee_validation_result,
    set_committee_validation_result,
    set_active_committee_tab,
    get_active_committee_tab,
)
from ui.utils.enhancement_utils import (
    save_enhancement,
    load_past_enhancements,
    create_export_markdown,
    create_export_html,
)
from ui.styles.main import load_css  # Assuming this loads general styles
# from ui.progress_monitor import run_enhancement_with_monitoring, create_progress_components # Will simplify progress handling

# Initialize session state keys if they don't exist
init_enhancement_state()  # Call this to ensure all session state variables are initialized


# Custom CSS
def get_custom_enhancement_css():
    return """
    <style>
        /* Proposal formatting */
        .proposal-container h1 { /* Assuming proposal has H1 for title */
            background-color: #f0f7ff; 
            padding: 10px;
            border-left: 4px solid #3b82f6;
            margin-top: 25px;
            font-size: 1.5em; /* Adjust size */
        }
        
        .proposal-container h2 { /* For sections like "Issue Identified" */
            color: #3b82f6;
            border-bottom: 1px solid #e5e7eb;
            padding-bottom: 5px;
            margin-top: 20px;
            font-size: 1.25em; /* Adjust size */
        }
        
        .proposal-container strong { /* For "Original Text:", "Proposed Text:" */
            color: #1e40af;
        }

        /* Styling for Original Text and Proposed Text blocks */
        /* Use more specific classes if possible, or style based on structure */
        .original-text-block, .proposed-text-block {
            background-color: #f9fafb;
            padding: 15px;
            border-radius: 5px;
            border: 1px solid #e5e7eb;
            font-family: 'Courier New', monospace;
            margin-top: 5px;
            white-space: pre-wrap;
        }
        
        .diff-container {
            padding: 10px;
            border-radius: 5px;
            border: 1px solid #e5e7eb;
            font-family: 'Courier New', monospace;
            white-space: pre-wrap;
            overflow-x: auto;
            background-color: #fdfdfd;
        }
        
        .committee-editor-section { /* Renamed for clarity */
            border: 1px solid #cbd5e1; /* Softer border */
            border-radius: 8px;
            padding: 20px;
            margin-top: 25px;
            background-color: #f9fafb;
        }
                
        .validation-result-container { /* Renamed for clarity */
            padding: 15px;
            border-radius: 5px;
            margin-top: 20px;
            border-width: 1px;
            border-style: solid;
        }
        
        .validation-approved {
            background-color: #dcfce7; border-color: #166534; color: #14532d;
        }
        
        .validation-rejected {
            background-color: #fee2e2; border-color: #991b1b; color: #7f1d1d;
        }
        
        .validation-revision {
            background-color: #ffedd5; border-color: #9a3412; color: #7c2d12;
        }
        
        .diff-stats {
            display: flex;
            justify-content: space-around; /* Better spacing */
            margin-bottom: 20px;
            gap: 10px; /* Gap between items */
        }
        
        .diff-stat-item {
            text-align: center;
            background-color: #f3f4f6; /* Slightly different background */
            padding: 15px;
            border-radius: 8px;
            flex: 1;
            border: 1px solid #e5e7eb;
        }
        
        .diff-stat-value {
            font-size: 1.75rem; /* Larger value */
            font-weight: bold;
            color: #3b82f6;
        }
        
        .diff-stat-label {
            font-size: 0.85rem; /* Slightly larger label */
            color: #4b5563;
            margin-top: 5px;
        }
        
        /* Committee tab styling - st.radio is already horizontal by default with horizontal=True */
    </style>
    """


# --- Async Helper ---
async def run_enhancement_process_async(
    orchestrator,
    standard_id,
    trigger_scenario,
    progress_callback_wrapper,
    include_cross,
):
    """Helper to run the orchestrator's async method."""
    try:
        results = await orchestrator.run_enhancement_workflow(
            standard_id=standard_id,
            trigger_scenario=trigger_scenario,
            progress_callback=progress_callback_wrapper,  # Pass the wrapper
            include_cross_standard_analysis=include_cross,
        )
        return results
    except Exception as e:
        logging.error(f"Error in async enhancement process: {e}", exc_info=True)
        # Propagate the error so Streamlit can catch it
        raise


# --- Main Page Rendering Function ---
def render_standards_enhancement_page():
    load_css()  # Load general CSS
    st.markdown(
        get_custom_enhancement_css(), unsafe_allow_html=True
    )  # Load page-specific CSS

    st.title("⚖️ Standards Enhancement Workbench")
    st.markdown(
        "Analyze and enhance AAOIFI Financial Accounting Standards (FAS) "
        "to address new scenarios, identify ambiguities, and propose improvements."
    )
    st.markdown("---")

    # --- Input Configuration Section ---
    with st.sidebar:  # Move inputs to sidebar for cleaner layout
        st.header("⚙️ Configuration")

        # Test Case Selection
        test_case_options = {case["name"]: case for case in ENHANCEMENT_TEST_CASES}
        available_test_cases = ["Custom"] + list(test_case_options.keys())

        selected_case_name = st.selectbox(
            "Select Test Case or 'Custom'",
            options=available_test_cases,
            index=0,  # Default to 'Custom'
            help="Choose a predefined scenario or define your own.",
        )

        if selected_case_name == "Custom":
            st.session_state.standard_id = st.selectbox(
                "Target Standard (FAS ID)",
                options=["4", "7", "10", "28", "32"],  # Ensure these are strings
                index=st.session_state.get("standard_id_index", 2),  # Default to FAS 10
            )
            st.session_state.trigger_scenario = st.text_area(
                "Trigger Scenario",
                value=st.session_state.get("trigger_scenario", ""),
                height=150,
                help="Describe the situation requiring standard enhancement.",
            )
        else:
            case_data = test_case_options[selected_case_name]
            st.session_state.standard_id = str(
                case_data["standard_id"]
            )  # Ensure string
            st.session_state.trigger_scenario = case_data["trigger_scenario"]
            st.caption(f"Selected: FAS {st.session_state.standard_id}")
            st.info(f"Scenario: {st.session_state.trigger_scenario}")

        # Enhancement Options
        st.session_state.include_cross = st.checkbox(
            "Include Cross-Standard Analysis",
            value=st.session_state.get("include_cross", True),
            help="Analyze impact on related AAOIFI standards.",
        )

        # Expert Selection
        st.subheader("Expert Panel Configuration")
        default_experts = {
            "shariah": True,
            "finance": True,
            "standards": True,  # Required
            "practical": True,
            "risk": False,  # Optional defaults
        }
        if "selected_experts" not in st.session_state:
            st.session_state.selected_experts = default_experts.copy()

        # Display checkboxes for experts (required ones are disabled)
        st.session_state.selected_experts["shariah"] = st.checkbox(
            "Shariah Expert",
            value=True,
            disabled=True,
            help="Required for Shariah compliance review.",
        )
        st.session_state.selected_experts["finance"] = st.checkbox(
            "Finance Expert",
            value=True,
            disabled=True,
            help="Required for financial implications review.",
        )
        st.session_state.selected_experts["standards"] = st.checkbox(
            "Standards Expert",
            value=True,
            disabled=True,
            help="Required for standards consistency review.",
        )
        st.session_state.selected_experts["practical"] = st.checkbox(
            "Practical Expert",
            value=st.session_state.selected_experts.get("practical", True),
            help="Reviews implementation feasibility.",
        )
        st.session_state.selected_experts["risk"] = st.checkbox(
            "Risk Expert",
            value=st.session_state.selected_experts.get("risk", False),
            help="Reviews risk assessment and mitigation.",
        )

        # Main Action Button
        run_button_disabled = not (
            st.session_state.get("standard_id")
            and st.session_state.get("trigger_scenario")
        )
        if st.button(
            "🚀 Run Enhancement Process",
            type="primary",
            disabled=run_button_disabled,
            use_container_width=True,
        ):
            st.session_state.run_enhancement_triggered = True
            set_enhancement_results(None)  # Clear previous results

        if run_button_disabled:
            st.warning("Please select/enter a Standard ID and Trigger Scenario.")

    # --- Main Content Area (Progress and Results) ---
    if st.session_state.get("run_enhancement_triggered"):
        st.session_state.run_enhancement_triggered = False  # Reset trigger

        # Progress display area
        st.subheader("📈 Enhancement Progress")
        progress_bar = st.progress(0)
        status_text_area = st.empty()  # For detailed status messages

        # Wrapper for progress callback to update Streamlit components
        def progress_callback_wrapper(phase: str, detail: Optional[str] = None):
            logging.info(f"Orchestrator Progress: Phase='{phase}', Detail='{detail}'")
            # Map orchestrator phases to progress bar values and messages
            # This mapping needs to be robust based on actual phases from orchestrator
            phase_progress_map = {
                "WorkflowStart": (0.05, "Initializing workflow..."),
                "ReviewPhase": (0.1, detail or "Reviewing standard..."),
                "ReviewPhaseComplete": (0.2, "Review complete."),
                "ProposalPhase": (0.25, detail or "Generating initial proposal..."),
                "ProposalPhaseComplete": (0.35, "Initial proposal generated."),
                "DiscussionPhase": (0.4, detail or "Starting expert discussion..."),
                "DiscussionRoundStart": (
                    0.4
                    + (st.session_state.get("current_round_for_progress", 1) - 1) * 0.1,
                    detail
                    or f"Discussion round {st.session_state.get('current_round_for_progress', 1)} starting...",
                ),
                "ProposalRefinement_R": (
                    0.45
                    + (st.session_state.get("current_round_for_progress", 1) - 1) * 0.1,
                    detail or "Refining proposal...",
                ),
                "DiscussionRoundFeedback_R": (
                    0.5
                    + (st.session_state.get("current_round_for_progress", 1) - 1) * 0.1,
                    detail or "Feedback collected.",
                ),
                "DiscussionPhaseComplete": (0.7, "Expert discussion finished."),
                "ValidationPhase": (0.75, detail or "Validating proposal..."),
                "ValidationPhaseComplete": (0.85, "Validation complete."),
                "CrossStandardAnalysisPhase": (
                    0.9,
                    detail or "Analyzing cross-standard impact...",
                ),
                "CrossStandardAnalysisPhaseComplete": (
                    0.95,
                    "Cross-standard analysis complete.",
                ),
                "WorkflowComplete": (1.0, "Enhancement workflow completed!"),
                "WorkflowError": (1.0, f"Error: {detail}"),  # Show error
            }

            # Extract base phase for mapping (e.g., "ProposalRefinement_R1" -> "ProposalRefinement_R")
            base_phase = phase.split("_R")[0] + ("_R" if "_R" in phase else "")
            if "DiscussionRoundFeedback_R" in phase:
                base_phase = "DiscussionRoundFeedback_R"
            if "DiscussionRoundStart" in phase:
                try:
                    round_num_match = re.search(r"round (\d+)", detail or "")
                    if round_num_match:
                        st.session_state.current_round_for_progress = int(
                            round_num_match.group(1)
                        )
                except:
                    pass  # Ignore if parsing fails

            progress_value, message = phase_progress_map.get(
                base_phase, (progress_bar.value, detail or phase)
            )  # Use current progress if phase not mapped

            progress_bar.progress(progress_value)
            status_text_area.info(
                message
            )  # Use st.info, st.success, st.error as appropriate

        with st.spinner("Processing... Please wait."):
            try:
                orchestrator = EnhancementOrchestrator(
                    selected_experts_config=st.session_state.selected_experts
                )
                # Get or create event loop
                try:
                    loop = asyncio.get_running_loop()
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)

                results_data = loop.run_until_complete(
                    run_enhancement_process_async(
                        orchestrator,
                        st.session_state.standard_id,
                        st.session_state.trigger_scenario,
                        progress_callback_wrapper,
                        st.session_state.include_cross,
                    )
                )

                if results_data and not results_data.get("error"):
                    set_enhancement_results(results_data)
                    # save_enhancement(results_data)  # Save successful results
                    status_text_area.success(
                        "Enhancement process completed successfully!"
                    )
                    st.balloons()
                elif results_data and results_data.get("error"):
                    status_text_area.error(
                        f"Workflow failed: {results_data.get('error')}"
                    )
                    set_enhancement_results(
                        results_data
                    )  # Save error state for debugging
                else:
                    status_text_area.error(
                        "Enhancement process did not return expected results."
                    )
                    set_enhancement_results(
                        {"error": "No results returned from orchestrator."}
                    )

            except Exception as e:
                logging.error(
                    f"Unhandled error during Streamlit enhancement run: {e}",
                    exc_info=True,
                )
                status_text_area.error(f"An unexpected error occurred: {e}")
                set_enhancement_results(
                    {
                        "error": str(e),
                        "standard_id": st.session_state.standard_id,
                        "trigger_scenario": st.session_state.trigger_scenario,
                    }
                )
            finally:
                progress_bar.progress(1.0)  # Ensure progress bar completes

    # --- Display Results Section (if available) ---
    enhancement_results_data = get_enhancement_results()
    if enhancement_results_data:
        if "error" in enhancement_results_data:
            st.error(
                f"Displaying results from a failed run: {enhancement_results_data['error']}"
            )
            st.json(enhancement_results_data)
        else:
            st.subheader(
                f"📊 Enhancement Results for FAS {enhancement_results_data.get('standard_id', 'N/A')}"
            )

            tab_names = [
                "Overview",
                "Reviewer Analysis",
                "Proposal Evolution",
                "Final Validation",
            ]
            if enhancement_results_data.get("cross_standard_analysis_summary"):
                tab_names.append("Cross-Standard Impact")
            if enhancement_results_data.get("discussion_history"):
                tab_names.append("Expert Discussion Log")

            tabs = st.tabs(tab_names)

            with tabs[0]:  # Overview
                st.markdown(
                    f"**Trigger Scenario:** {enhancement_results_data.get('trigger_scenario', 'N/A')}"
                )
                st.markdown(f"**Initial Reviewer Retrieved Context:**")
                st.text_area(
                    "Reviewer Context",
                    value=enhancement_results_data.get(
                        "reviewer_retrieved_context", "N/A"
                    ),
                    height=150,
                    disabled=True,
                )
                st.markdown(f"**Final Proposed Structured Text:**")
                st.text_area(
                    "Final Proposal",
                    value=enhancement_results_data.get(
                        "final_proposal_structured", "N/A"
                    ),
                    height=200,
                    disabled=True,
                )
                st.metric(
                    "Final Agreement Score (Placeholder)",
                    f"{enhancement_results_data.get('final_agreement_score', 0.0):.2f}",
                )

            with tabs[1]:  # Reviewer Analysis
                st.markdown("**Reviewer's Analysis Summary:**")
                st.markdown(
                    enhancement_results_data.get("reviewer_analysis_summary", "N/A")
                )
                st.markdown("**Identified Enhancement Areas:**")
                areas = enhancement_results_data.get("reviewer_enhancement_areas", [])
                if areas:
                    for area in areas:
                        st.markdown(f"- {area}")
                else:
                    st.info("No specific enhancement areas pre-identified by reviewer.")

            with tabs[2]:  # Proposal Evolution
                st.markdown("**Initial Proposal (Structured):**")
                st.markdown(
                    f"```markdown\n{enhancement_results_data.get('initial_proposal_structured', 'N/A')}\n```"
                )
                st.markdown("---")
                st.markdown(
                    "**Final Proposal (Structured - after expert feedback and refinement):**"
                )
                st.markdown(
                    f"```markdown\n{enhancement_results_data.get('final_proposal_structured', 'N/A')}\n```"
                )

            with tabs[3]:  # Final Validation
                st.markdown("**Validation Summary:**")
                validation_data = enhancement_results_data.get("validation_summary", {})
                ## print the type of validation_data
                logging.info(f"Validation data type: {type(validation_data)}")
                print(type(validation_data))
                if isinstance(validation_data, dict):
                    validation_summary = validation_data.get(
                        "validation_result", 
                        "Validation not performed or no result available."
                    )
                elif isinstance(validation_data, str):
                    # Try to parse the string as JSON if it looks like a JSON object
                    if validation_data.strip().startswith('{') and validation_data.strip().endswith('}'):
                        print("Parsing validation data as JSON")
                        try:
                            # Properly handle JSON string to ensure it's valid before parsing
                            # First try to sanitize the string to handle common JSON errors
                            if validation_data.strip().startswith("'") and validation_data.strip().endswith("'"):
                                # Handle JSON wrapped in single quotes instead of double quotes
                                validation_data = validation_data.strip()[1:-1]
                                
                            # Replace escaped newlines with actual newlines for better formatting
                            cleaned_validation_data = validation_data.replace('\\n', '\n').replace('\\r', '\r')
                            # Try to parse the JSON
                            parsed_data = json.loads(cleaned_validation_data)
                            print(f"Parsed validation data: {parsed_data}")
                            logging.info(f"Successfully parsed validation data: {parsed_data}")
                            validation_summary = parsed_data.get(
                                "validation_result",
                                "Validation result not found in parsed JSON."
                            )
                        except json.JSONDecodeError as e:
                            logging.error(f"JSON parsing error: {e}")
                            print(f"Error parsing JSON: {e}")
                            validation_summary = validation_data
                    else:
                        validation_summary = validation_data
                else:
                    validation_summary = "Validation not performed or no summary available."

                decision_class = "validation-result-container"
                if "APPROVED" in validation_summary.upper():
                    decision_class += " validation-approved"
                elif "REJECTED" in validation_summary.upper():
                    decision_class += " validation-rejected"
                elif "NEEDS REVISION" in validation_summary.upper():
                    decision_class += " validation-revision"
                st.markdown(
                    f'<div class="{decision_class}">{validation_summary}</div>',
                    unsafe_allow_html=True,
                )

            if enhancement_results_data.get("cross_standard_analysis_summary"):
                with tabs[tab_names.index("Cross-Standard Impact")]:
                    st.markdown("**Cross-Standard Impact Analysis Summary:**")
                    st.markdown(
                        enhancement_results_data.get(
                            "cross_standard_analysis_summary", "N/A"
                        )
                    )

            if enhancement_results_data.get("discussion_history"):
                with tabs[tab_names.index("Expert Discussion Log")]:
                    st.markdown("**Full Expert Discussion Log:**")
                    st.json(enhancement_results_data.get("discussion_history", []))

            # Export section
            st.sidebar.subheader("⬇️ Export Results")
            markdown_content = create_export_markdown(enhancement_results_data)
            st.sidebar.download_button(
                label="Export as Markdown",
                data=markdown_content,
                file_name=f"enhancement_FAS{enhancement_results_data.get('standard_id', 'NA')}_{datetime.datetime.now().strftime('%Y%m%d%H%M')}.md",
                mime="text/markdown",
                use_container_width=True,
            )


    # --- View Past Enhancements Section ---
    st.sidebar.markdown("---")
    st.sidebar.subheader("🗂️ Past Enhancements")
    past_enhancements = load_past_enhancements()
    if not past_enhancements:
        st.sidebar.info("No past enhancements found.")
    else:
        enhancement_options = [
            f"FAS {e.get('standard_id', e.get('metadata', {}).get('standard_id', '?'))} - {e.get('trigger_scenario', e.get('metadata', {}).get('trigger_scenario', '?'))[:30]}... ({e.get('timestamp', e.get('metadata', {}).get('timestamp', ''))})"
            for e in past_enhancements
        ]
        selected_past_enh_idx = st.sidebar.selectbox(
            "View a past result:",
            options=range(len(enhancement_options)),
            format_func=lambda i: enhancement_options[i],
            index=None,
            placeholder="Select a past enhancement...",
        )
        if selected_past_enh_idx is not None:
            set_enhancement_results(past_enhancements[selected_past_enh_idx])
            if st.sidebar.button(
                "Load Selected Past Enhancement for Viewing", use_container_width=True
            ):
                st.rerun()


if __name__ == "__main__":
    st.set_page_config(layout="wide", page_title="Standards Enhancement Workbench")
    render_standards_enhancement_page()
