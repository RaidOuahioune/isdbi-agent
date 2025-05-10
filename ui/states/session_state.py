"""
Session state management for the Streamlit application.
"""

import streamlit as st
from typing import Dict, Any, List, Optional

def init_enhancement_state():
    """Initialize the session state for standards enhancement."""
    if 'enhancement_results' not in st.session_state:
        st.session_state.enhancement_results = None
    
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "home"

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

def set_transaction_analysis_results(results: Dict[str, Any]):
    """Set the transaction analysis results in the session state."""
    st.session_state.transaction_analysis_results = results

def get_transaction_analysis_results() -> Optional[Dict[str, Any]]:
    """Get the transaction analysis results from the session state."""
    return st.session_state.transaction_analysis_results

def init_use_case_state():
    """Initialize the session state for use case processing."""
    if 'use_case_results' not in st.session_state:
        st.session_state.use_case_results = None

def set_use_case_results(results: Dict[str, Any]):
    """Set the use case results in the session state."""
    st.session_state.use_case_results = results

def get_use_case_results() -> Optional[Dict[str, Any]]:
    """Get the use case results from the session state."""
    return st.session_state.use_case_results

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

def init_all_states():
    """Initialize all session states."""
    init_enhancement_state()
    init_transaction_analysis_state()
    init_use_case_state()
    init_product_design_state()
    init_compliance_verifier_state() 