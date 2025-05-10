"""
Progress display utility functions for the UI.
"""

import streamlit as st

def display_progress_bar(container, progress: float, status: str = None):
    """
    Display a progress bar and optional status message in the given container.
    
    Args:
        container: Streamlit container where the progress bar will be displayed
        progress: Progress value (0.0 to 1.0)
        status: Optional status message to display alongside the progress bar
    """
    with container:
        progress_bar = st.progress(progress)
        if status:
            st.caption(status)
        return progress_bar 