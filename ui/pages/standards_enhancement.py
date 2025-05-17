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
import tempfile

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
    from enhancement import (
        ENHANCEMENT_TEST_CASES, 
        generate_enhanced_pdf, 
        check_pdf_api_availability,
        PDF_CONFIG
    )
except ImportError as e:
    logging.warning(
        f"Error importing from enhancement.py: {e}"
    )
    ENHANCEMENT_TEST_CASES = []
    # Define fallback functions if imports fail
    def generate_enhanced_pdf(*args, **kwargs):
        logging.error("generate_enhanced_pdf function not available")
        return None
        
    def check_pdf_api_availability(*args, **kwargs):
        logging.error("check_pdf_api_availability function not available")
        return False
        
    PDF_CONFIG = {"enabled": False}

from components.orchestration.enhancement_orchestrator import EnhancementOrchestrator
import json
from podcast_generator import generator

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


def generate_and_download_podcast(markdown_content, enhancement_data=None):
    """Generate a podcast from markdown content and return the file path"""
    try:
        # Create a temporary file to store the markdown
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as temp_md:
            temp_md.write(markdown_content)
            temp_md_path = temp_md.name
        
        # Generate a unique output filename
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Get standard ID from enhancement data if available
        standard_id = "Unknown"
        if enhancement_data and 'standard_id' in enhancement_data:
            standard_id = enhancement_data['standard_id']
            
        output_filename = f"enhancement_podcast_FAS{standard_id}_{timestamp}.mp3"
        
        # Create podcast generator and generate podcast
        api_key = os.getenv("ELEVEN_LABS_API_KEY", "sk_ebc9b70b7d7ee7cee2a0e21ea9c0694cbbd1b81d170f1680")
        
        # Create output directory if it doesn't exist
        Path("podcast_output").mkdir(exist_ok=True)
        
        # Generate the podcast
        generator.create_podcast(temp_md_path, output_filename)
        
        # Get the full path to the generated podcast
        podcast_path = f"podcast_output/{output_filename}"
        
        # Clean up the temporary markdown file
        os.unlink(temp_md_path)
        
        return podcast_path
    
    except Exception as e:
        logging.error(f"Error generating podcast: {str(e)}", exc_info=True)
        return None


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
        
        # PDF Generation Configuration
        st.subheader("PDF Generation")
        
        # Initialize PDF config in session state if not present
        if "pdf_config" not in st.session_state:
            st.session_state.pdf_config = PDF_CONFIG.copy()
        
        # Enable/disable PDF generation
        pdf_enabled = st.checkbox(
            "Enable PDF Generation",
            value=st.session_state.pdf_config.get("enabled", True),
            help="Generate enhanced PDFs with proposed changes"
        )
        
        # Update the config
        st.session_state.pdf_config["enabled"] = pdf_enabled
        PDF_CONFIG["enabled"] = pdf_enabled
        
        # Show additional options if enabled
        if pdf_enabled:
            # Auto-disable on failure
            auto_disable = st.checkbox(
                "Auto-disable on failure",
                value=st.session_state.pdf_config.get("auto_disable_on_failure", True),
                help="Automatically disable PDF generation if the API is unreachable"
            )
            st.session_state.pdf_config["auto_disable_on_failure"] = auto_disable
            PDF_CONFIG["auto_disable_on_failure"] = auto_disable
            
            # Max retries slider
            max_retries = st.slider(
                "Max API retries",
                min_value=1,
                max_value=5,
                value=st.session_state.pdf_config.get("max_retries", 3),
                help="Maximum number of retry attempts for API calls"
            )
            st.session_state.pdf_config["max_retries"] = max_retries
            PDF_CONFIG["max_retries"] = max_retries
            
            # API status indicator
            st.caption("API Status:")
            if check_pdf_api_availability():
                st.success("PDF API is available", icon="✅")
            else:
                st.error("PDF API is unavailable", icon="❌")
        
        # Save the PDF config
        try:
            from enhancement import save_pdf_config
            save_pdf_config()
        except ImportError:
            pass

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
            
            # Add PDF Export tab
            tab_names.append("PDF Export")

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
                
                # Add PDF generation button in the Overview tab
                if PDF_CONFIG.get("enabled", True):
                    st.markdown("---")
                    st.markdown("### Generate Enhanced PDF")
                    st.markdown("Generate a professional PDF document with the proposed changes to the standard.")
                    
                    pdf_col1, pdf_col2 = st.columns([1, 2])
                    if pdf_col1.button("📄 Generate Enhanced PDF", key="pdf_btn_overview", use_container_width=True):
                        # Create a placeholder for status messages
                        pdf_status_placeholder = pdf_col2.empty()
                        pdf_status_placeholder.info("Generating PDF...")
                        
                        # Check API availability
                        if not check_pdf_api_availability():
                            pdf_status_placeholder.error("PDF API is not available. Please try again later.")
                        else:
                            # Generate the PDF
                            pdf_path = generate_enhanced_pdf(
                                enhancement_results_data, 
                                enhancement_results_data.get('standard_id', 'NA')
                            )
                            
                            if pdf_path and os.path.exists(pdf_path):
                                # Read the PDF file for download
                                with open(pdf_path, "rb") as f:
                                    pdf_data = f.read()
                                
                                # Show success message
                                pdf_status_placeholder.success("PDF generated successfully!")
                                
                                # Display download button
                                st.download_button(
                                    label="⬇️ Download Enhanced PDF",
                                    data=pdf_data,
                                    file_name=os.path.basename(pdf_path),
                                    mime="application/pdf",
                                )
                                
                                # Show PDF preview if possible
                                st.markdown(f"**PDF saved to:** `{pdf_path}`")
                            else:
                                pdf_status_placeholder.error("Failed to generate PDF. Please check logs for details.")
                else:
                    st.info("PDF generation is disabled. You can enable it in the sidebar configuration.")

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

            # PDF Export tab
            with tabs[tab_names.index("PDF Export")]:
                st.header("Enhanced PDF Export")
                
                # Check if PDF generation is enabled
                if not PDF_CONFIG.get("enabled", True):
                    st.warning("PDF generation is currently disabled. Enable it in the sidebar configuration.")
                else:
                    # Check API availability
                    api_available = check_pdf_api_availability()
                    if api_available:
                        st.success("✅ PDF Generation API is available")
                    else:
                        st.error("❌ PDF Generation API is not available. Please try again later.")
                    
                    # Display standard information
                    st.subheader("Standard Information")
                    standard_id = enhancement_results_data.get('standard_id', 'N/A')
                    
                    # Get standard name from mapping if available
                    try:
                        from enhancement import STANDARD_ID_TO_NAME
                        standard_name = STANDARD_ID_TO_NAME.get(standard_id, "Unknown")
                    except ImportError:
                        standard_name = "Unknown"
                    
                    col1, col2 = st.columns(2)
                    col1.metric("Standard ID", f"FAS {standard_id}")
                    col2.metric("Standard Name", standard_name)
                    
                    # Display extracted clauses
                    st.subheader("Extracted Clauses")
                    st.markdown("The following clauses will be included in the PDF:")
                    
                    # Extract clauses using the agent
                    from components.agents import clause_extractor_agent
                    extracted_clauses = clause_extractor_agent.extract_clauses(enhancement_results_data)
                    
                    if extracted_clauses:
                        # Display clauses in an expander
                        with st.expander("View Extracted Clauses", expanded=True):
                            for i, clause in enumerate(extracted_clauses, 1):
                                st.markdown(f"**Clause {i}: ID {clause['clause_id']}**")
                                st.text_area(
                                    f"Proposed Text for Clause {clause['clause_id']}",
                                    value=clause['proposed_text'],
                                    height=100,
                                    key=f"clause_{i}",
                                    disabled=True
                                )
                    else:
                        st.warning("No clauses could be extracted from the enhancement proposal.")
                    
                    # PDF generation button
                    st.subheader("Generate PDF")
                    
                    # Disable button if API is not available
                    generate_btn_disabled = not api_available
                    
                    if st.button("📄 Generate Enhanced PDF Document", 
                                 disabled=generate_btn_disabled,
                                 type="primary",
                                 use_container_width=True):
                        
                        # Create status container
                        status_container = st.empty()
                        status_container.info("Generating enhanced PDF...")
                        
                        # Generate the PDF
                        pdf_path = generate_enhanced_pdf(
                            enhancement_results_data, 
                            standard_id
                        )
                        
                        if pdf_path and os.path.exists(pdf_path):
                            # Read the PDF file for download
                            with open(pdf_path, "rb") as f:
                                pdf_data = f.read()
                            
                            # Show success message
                            status_container.success("✅ PDF generated successfully!")
                            
                            # Display file information
                            file_size_kb = round(len(pdf_data) / 1024, 2)
                            st.metric("PDF File Size", f"{file_size_kb} KB")
                            st.markdown(f"**File path:** `{pdf_path}`")
                            
                            # Display download button
                            st.download_button(
                                label="⬇️ Download Enhanced PDF",
                                data=pdf_data,
                                file_name=os.path.basename(pdf_path),
                                mime="application/pdf",
                                use_container_width=True
                            )
                            
                            # Display PDF preview if possible
                            st.subheader("PDF Preview")
                            st.markdown("PDF preview is not available in Streamlit. Please download the file to view it.")
                            
                        else:
                            status_container.error("❌ Failed to generate PDF. Please check logs for details.")
                    
                    # Display additional information about the PDF generation process
                    with st.expander("About PDF Generation"):
                        st.markdown("""
                        ### How It Works
                        
                        1. The system extracts clauses from the enhancement proposal using an LLM-powered agent
                        2. The extracted clauses are sent to a specialized PDF generation API
                        3. The API generates a professional PDF document with the proposed changes
                        4. The PDF is saved to the `enhancement_results` directory
                        
                        ### Troubleshooting
                        
                        If PDF generation fails:
                        - Check if the API is available (indicator above)
                        - Ensure the standard ID is one of the supported standards
                        - Try again later if the API is temporarily unavailable
                        """)

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
            
            # Add PDF generation button
            pdf_col1, pdf_col2 = st.sidebar.columns(2)
            if pdf_col1.button("📄 Generate PDF", use_container_width=True):
                # Create a placeholder for the download button
                pdf_download_placeholder = pdf_col2.empty()
                
                # Show generation progress
                with st.sidebar.status("Generating enhanced PDF...") as status:
                    status.update(label="Checking API availability...", state="running")
                    
                    # Check if the API is available
                    if not check_pdf_api_availability():
                        status.update(label="PDF API is not available", state="error")
                        st.sidebar.error("PDF generation API is not available. Please try again later.")
                    else:
                        status.update(label="Extracting clauses...", state="running")
                        time.sleep(0.5)  # Small delay for UI update
                        
                        status.update(label="Generating enhanced PDF with API...", state="running")
                        # Generate the PDF
                        pdf_path = generate_enhanced_pdf(enhancement_results_data, enhancement_results_data.get('standard_id', 'NA'))
                        
                        if pdf_path and os.path.exists(pdf_path):
                            # Read the PDF file for download
                            with open(pdf_path, "rb") as f:
                                pdf_data = f.read()
                            
                            status.update(label="PDF ready for download!", state="complete")
                            
                            # Provide download button for the PDF
                            pdf_download_placeholder.download_button(
                                label="⬇️ Download",
                                data=pdf_data,
                                file_name=os.path.basename(pdf_path),
                                mime="application/pdf",
                                use_container_width=True,
                            )
                            
                            # Add a success message with file size info
                            file_size_kb = round(len(pdf_data) / 1024, 2)
                            st.sidebar.success(f"Enhanced PDF generated successfully! ({file_size_kb} KB)")
                            
                            # Add a link to open the PDF
                            pdf_rel_path = os.path.relpath(pdf_path, os.getcwd())
                            st.sidebar.markdown(f"[Open PDF]({pdf_rel_path})")
                        else:
                            status.update(label="Failed to generate PDF", state="error")
                            st.sidebar.error("Failed to generate enhanced PDF. Please check logs for details.")
            
            # Add podcast generation button
            podcast_col1, podcast_col2 = st.sidebar.columns(2)
            if podcast_col1.button("🎙️ Generate Podcast", use_container_width=True):
                # Create a placeholder for the download button
                podcast_download_placeholder = podcast_col2.empty()
                
                # Show generation progress
                with st.sidebar.status("Generating podcast...") as status:
                    status.update(label="Preparing markdown content...", state="running")
                    time.sleep(0.5)  # Small delay for UI update
                    
                    status.update(label="Generating audio segments with ElevenLabs API...", state="running")
                    podcast_path = generate_and_download_podcast(markdown_content, enhancement_data=enhancement_results_data)
                    
                    if podcast_path and os.path.exists(podcast_path):
                        # Read the podcast file for download
                        with open(podcast_path, "rb") as f:
                            podcast_data = f.read()
                        
                        status.update(label="Podcast ready for download!", state="complete")
                        
                        # Provide download button for the podcast
                        podcast_download_placeholder.download_button(
                            label="⬇️ Download",
                            data=podcast_data,
                            file_name=os.path.basename(podcast_path),
                            mime="audio/mpeg",
                            use_container_width=True,
                        )
                        
                        # Add a success message with file size info
                        file_size_mb = round(len(podcast_data) / (1024 * 1024), 2)
                        st.sidebar.success(f"Podcast generated successfully! ({file_size_mb} MB)")
                        
                        # Add a player to preview the podcast
                        st.sidebar.audio(podcast_data, format="audio/mp3")
                    else:
                        status.update(label="Failed to generate podcast", state="error")
                        st.sidebar.error("Failed to generate podcast. Please check logs for details.")


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
