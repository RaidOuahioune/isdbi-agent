import streamlit as st
import queue
import threading
import time
from typing import Dict, Any, Optional, Callable, List
import random

class EnhancementProgressMonitor:
    """
    A class to monitor and display the progress of the enhancement process.
    This enables real-time updates during long-running operations.
    """
    
    def __init__(self):
        self.progress_queue = queue.Queue()
        self.stop_event = threading.Event()
        self.current_phase = "setup"
        self.review_details = []
        self.proposal_details = []
        self.validation_details = []
    
    def start_monitoring(self):
        """Start the monitoring thread."""
        self.stop_event.clear()
        thread = threading.Thread(target=self._update_progress)
        thread.daemon = True
        thread.start()
    
    def stop_monitoring(self):
        """Stop the monitoring thread."""
        self.stop_event.set()
    
    def _update_progress(self):
        """Update progress information from the queue."""
        while not self.stop_event.is_set():
            try:
                # Get updates from the queue with a timeout to allow checking stop_event
                try:
                    update = self.progress_queue.get(timeout=0.1)
                    self._process_update(update)
                    self.progress_queue.task_done()
                except queue.Empty:
                    pass  # No updates, continue waiting
                
                # Sleep briefly to reduce CPU usage
                time.sleep(0.05)
            except Exception as e:
                print(f"Error in progress monitor: {e}")
    
    def _process_update(self, update: Dict[str, Any]):
        """Process an update from the queue."""
        if 'phase' in update:
            self.current_phase = update['phase']
        
        # Process phase-specific updates
        if self.current_phase == 'review' and 'review_detail' in update:
            self.review_details.append(update['review_detail'])
        elif self.current_phase == 'proposal' and 'proposal_detail' in update:
            self.proposal_details.append(update['proposal_detail'])
        elif self.current_phase == 'validation' and 'validation_detail' in update:
            self.validation_details.append(update['validation_detail'])
    
    def add_update(self, update: Dict[str, Any]):
        """Add an update to the queue."""
        self.progress_queue.put(update)

def create_progress_components() -> Dict[str, Any]:
    """Create progress monitoring components"""
    
    components = {
        "progress_bar": st.progress(0),
        "progress_status": st.empty(),
        "review": st.empty(),
        "proposal": st.empty(),
        "validation": st.empty()
    }
    
    # Initialize status messages
    components["review"].info("🔄 Initializing review phase...")
    components["proposal"].info("⏳ Waiting for review to complete...")
    components["validation"].info("⏳ Waiting for proposal generation...")
    
    return components

def run_enhancement_with_monitoring(
    standard_id: str,
    trigger_scenario: str,
    run_func: Callable,
    components: Dict[str, Any]
) -> Dict[str, Any]:
    """Run enhancement process with visual progress monitoring"""
    
    # Define progress phases and steps
    phase_steps = {
        "review": [
            "Loading standard...",
            "Analyzing content...",
            "Identifying gaps...",
            "Summarizing findings..."
        ],
        "proposal": [
            "Reviewing analysis...",
            "Generating proposals...",
            "Refining text...",
            "Finalizing changes..."
        ],
        "validation": [
            "Checking Shariah compliance...",
            "Verifying consistency...",
            "Evaluating practicality...",
            "Making final decision..."
        ]
    }
    
    try:
        # Progress callback function
        def progress_callback(phase: str, detail: str = None):
            if phase == "review_start":
                components["review"].info("🔍 Reviewing standard...")
                update_phase_progress("review", components, 0.0, 0.33)
            elif phase == "review_complete":
                components["review"].success("✅ Review complete")
                components["proposal"].info("✏️ Generating proposals...")
                update_phase_progress("proposal", components, 0.33, 0.66)
            elif phase == "proposal_complete":
                components["proposal"].success("✅ Proposals generated")
                components["validation"].info("⚖️ Validating changes...")
                update_phase_progress("validation", components, 0.66, 1.0)
            elif phase == "validation_complete":
                components["validation"].success("✅ Validation complete")
                components["progress_bar"].progress(1.0)
                components["progress_status"].success("Enhancement process completed!")
                
            if detail:
                components["progress_status"].info(detail)
        
        # Run the enhancement process
        results = run_func(standard_id, trigger_scenario, progress_callback)
        return results
        
    except Exception as e:
        components["progress_status"].error(f"Error: {str(e)}")
        raise

def update_phase_progress(
    phase: str,
    components: Dict[str, Any],
    start_pct: float,
    end_pct: float
):
    """Update progress bar through a phase's steps"""
    steps = 5
    for i in range(steps):
        progress = start_pct + (i / steps) * (end_pct - start_pct)
        components["progress_bar"].progress(progress)
        time.sleep(0.1)  # Small delay for visual feedback

def create_fancy_progress_bar():
    """Create a fancy animated progress bar."""
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    phases = ["Initializing", "Reviewing Standard", "Analyzing Gaps", 
             "Generating Proposals", "Validating Compliance", "Finalizing"]
    
    # Simulate progress updates
    def update_progress(phase_idx, progress):
        progress_bar.progress(progress)
        status_text.text(f"{phases[phase_idx]}: {int(progress * 100)}%")
    
    return update_progress

def update_progress_with_steps(phase: str, progress: float, status: str):
    """Update progress bar with current status."""
    progress_container = st.empty()
    status_text = st.empty()
    
    progress_mapping = {
        "review": {
            "icon": "🔍",
            "color": "blue",
            "steps": ["Loading standard", "Analyzing requirements", "Identifying gaps"]
        },
        "proposal": {
            "icon": "✏️",
            "color": "green",
            "steps": ["Drafting changes", "Refining language", "Validating consistency"]
        },
        "validation": {
            "icon": "⚖️",
            "color": "orange",
            "steps": ["Checking Shariah compliance", "Verifying consistency", "Final assessment"]
        }
    }
    
    phase_info = progress_mapping.get(phase, {})
    progress_container.progress(progress)
    status_text.markdown(
        f"<div style='color: {phase_info.get('color', 'gray')}'>"
        f"{phase_info.get('icon', '')} {status}</div>",
        unsafe_allow_html=True
    )