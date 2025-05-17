"""
Session state management for the Streamlit application.
"""

import streamlit as st
from typing import Dict, Any, List, Optional
import json
import os
from datetime import datetime

def init_enhancement_state():
    """Initialize the session state for standards enhancement."""
    if 'enhancement_results' not in st.session_state:
        st.session_state.enhancement_results = None
    
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "home"
        
    # Initialize committee edit state
    init_committee_edit_state()

def set_enhancement_results(results: Dict[str, Any]):
    """Set the enhancement results in the session state."""
    st.session_state.enhancement_results = results

def get_enhancement_results() -> Optional[Dict[str, Any]]:
    """Get the enhancement results from the session state."""
    return st.session_state.enhancement_results

def set_current_page(page: str):
    """Set the current page in the session state."""
    st.session_state.current_page = page

def get_current_page() -> str:
    """Get the current page from the session state."""
    return st.session_state.current_page

def init_transaction_analysis_state():
    """Initialize the session state for transaction analysis."""
    if 'transaction_analysis_results' not in st.session_state:
        st.session_state.transaction_analysis_results = None
    # Add dual answer support
    if 'transaction_analysis_results_1' not in st.session_state:
        st.session_state.transaction_analysis_results_1 = None
    if 'transaction_analysis_results_2' not in st.session_state:
        st.session_state.transaction_analysis_results_2 = None
    if 'selected_transaction_answer' not in st.session_state:
        st.session_state.selected_transaction_answer = None

def set_transaction_analysis_results(results: Dict[str, Any]):
    """Set the transaction analysis results in the session state."""
    st.session_state.transaction_analysis_results = results

def get_transaction_analysis_results() -> Optional[Dict[str, Any]]:
    """Get the transaction analysis results from the session state."""
    return st.session_state.transaction_analysis_results

# Add dual answer support for transaction analysis
def set_transaction_analysis_results_dual(results_1: Dict[str, Any], results_2: Dict[str, Any]):
    """Set both sets of transaction analysis results in the session state."""
    st.session_state.transaction_analysis_results_1 = results_1
    st.session_state.transaction_analysis_results_2 = results_2
    # For backward compatibility
    st.session_state.transaction_analysis_results = results_1

def get_transaction_analysis_results_dual() -> tuple:
    """Get both sets of transaction analysis results from the session state."""
    return (st.session_state.transaction_analysis_results_1, st.session_state.transaction_analysis_results_2)

def set_selected_transaction_answer(answer_num: int):
    """Set which transaction analysis answer was selected as best."""
    st.session_state.selected_transaction_answer = answer_num

def get_selected_transaction_answer() -> Optional[int]:
    """Get which transaction analysis answer was selected as best."""
    return st.session_state.selected_transaction_answer

def init_use_case_state():
    """Initialize the session state for use case processing."""
    if 'use_case_results' not in st.session_state:
        st.session_state.use_case_results = None
    # Add dual answer support
    if 'use_case_results_1' not in st.session_state:
        st.session_state.use_case_results_1 = None
    if 'use_case_results_2' not in st.session_state:
        st.session_state.use_case_results_2 = None
    if 'selected_use_case_answer' not in st.session_state:
        st.session_state.selected_use_case_answer = None

def set_use_case_results(results: Dict[str, Any]):
    """Set the use case results in the session state."""
    st.session_state.use_case_results = results

def get_use_case_results() -> Optional[Dict[str, Any]]:
    """Get the use case results from the session state."""
    return st.session_state.use_case_results

# Add dual answer support for use case processing
def set_use_case_results_dual(results_1: Dict[str, Any], results_2: Dict[str, Any]):
    """Set both sets of use case results in the session state."""
    st.session_state.use_case_results_1 = results_1
    st.session_state.use_case_results_2 = results_2
    # For backward compatibility
    st.session_state.use_case_results = results_1

def get_use_case_results_dual() -> tuple:
    """Get both sets of use case results from the session state."""
    return (st.session_state.use_case_results_1, st.session_state.use_case_results_2)

def set_selected_use_case_answer(answer_num: int):
    """Set which use case answer was selected as best."""
    st.session_state.selected_use_case_answer = answer_num

def get_selected_use_case_answer() -> Optional[int]:
    """Get which use case answer was selected as best."""
    return st.session_state.selected_use_case_answer

# Add feedback collection functions
def save_feedback(module_type: str, feedback: Dict[str, Any]):
    """Save user feedback to a JSON file.
    
    Args:
        module_type: Type of module ('use_case' or 'transaction_analysis')
        feedback: The feedback data to save
    """
    # Add timestamp
    feedback['timestamp'] = datetime.now().isoformat()
    
    # Create feedback directory if it doesn't exist
    os.makedirs('feedback', exist_ok=True)
    
    # Append to the appropriate feedback file
    filename = f"feedback/{module_type}_feedback.json"
    
    # Read existing data
    existing_data = []
    if os.path.exists(filename):
        try:
            with open(filename, 'r') as f:
                existing_data = json.load(f)
                if not isinstance(existing_data, list):
                    existing_data = []
        except:
            existing_data = []
    
    # Append new feedback
    existing_data.append(feedback)
    
    # Write updated data
    with open(filename, 'w') as f:
        json.dump(existing_data, f, indent=2)

# Add product design state functions
def init_product_design_state():
    """Initialize the session state for product design."""
    if 'product_design_results' not in st.session_state:
        st.session_state.product_design_results = None
    if 'saved_designs' not in st.session_state:
        st.session_state.saved_designs = []

def set_product_design_results(results: Dict[str, Any]):
    """Set the product design results in the session state."""
    st.session_state.product_design_results = results

def get_product_design_results() -> Optional[Dict[str, Any]]:
    """Get the product design results from the session state."""
    return st.session_state.product_design_results

def add_saved_design(design: Dict[str, Any]):
    """Add a design to the saved designs list."""
    if 'saved_designs' not in st.session_state:
        st.session_state.saved_designs = []
    st.session_state.saved_designs.append(design)

def get_saved_designs() -> List[Dict[str, Any]]:
    """Get the list of saved designs."""
    if 'saved_designs' not in st.session_state:
        st.session_state.saved_designs = []
    return st.session_state.saved_designs

# Add compliance verifier state functions
def init_compliance_verifier_state():
    """Initialize the session state for compliance verification."""
    if 'compliance_verifier_results' not in st.session_state:
        st.session_state.compliance_verifier_results = None
    if 'saved_verifications' not in st.session_state:
        st.session_state.saved_verifications = []

def set_compliance_verifier_results(results: Dict[str, Any]):
    """Set the compliance verification results in the session state."""
    st.session_state.compliance_verifier_results = results

def get_compliance_verifier_results() -> Optional[Dict[str, Any]]:
    """Get the compliance verification results from the session state."""
    return st.session_state.compliance_verifier_results

def add_saved_verification(verification: Dict[str, Any]):
    """Add a verification to the saved verifications list."""
    if 'saved_verifications' not in st.session_state:
        st.session_state.saved_verifications = []
    st.session_state.saved_verifications.append(verification)

def get_saved_verifications() -> List[Dict[str, Any]]:
    """Get the list of saved verifications."""
    if 'saved_verifications' not in st.session_state:
        st.session_state.saved_verifications = []
    return st.session_state.saved_verifications

# Add committee edit state functions
def init_committee_edit_state():
    """Initialize committee edit state variables if they don't exist."""
    if "committee_edited_text" not in st.session_state:
        st.session_state.committee_edited_text = None
    if "committee_validation_result" not in st.session_state:
        st.session_state.committee_validation_result = None
    if "show_committee_editor" not in st.session_state:
        st.session_state.show_committee_editor = False
    if "editing_in_progress" not in st.session_state:
        st.session_state.editing_in_progress = False
    if "active_committee_tab" not in st.session_state:
        st.session_state.active_committee_tab = "committee_editor"
        
def set_committee_edit_text(text):
    """Set the committee edited text."""
    st.session_state.committee_edited_text = text
    
def get_committee_edit_text():
    """Get the committee edited text."""
    return st.session_state.committee_edited_text
    
def set_committee_validation_result(result):
    """Set the committee validation result."""
    st.session_state.committee_validation_result = result
    
def get_committee_validation_result():
    """Get the committee validation result."""
    return st.session_state.committee_validation_result

def set_active_committee_tab(tab_name):
    """Set the active committee tab."""
    st.session_state.active_committee_tab = tab_name
    
def get_active_committee_tab():
    """Get the active committee tab."""
    if "active_committee_tab" not in st.session_state:
        st.session_state.active_committee_tab = "committee_editor"
    return st.session_state.active_committee_tab

def init_all_states():
    """Initialize all session states."""
    init_enhancement_state()
    init_transaction_analysis_state()
    init_use_case_state()
    init_product_design_state()
    init_compliance_verifier_state()
    init_committee_edit_state()