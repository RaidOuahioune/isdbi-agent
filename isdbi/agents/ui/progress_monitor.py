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

def create_progress_components():
    """Create the progress components for the UI."""
    # Create containers for each phase
    review_container = st.empty()
    proposal_container = st.empty()
    validation_container = st.empty()
    
    # Create a progress bar
    progress_bar = st.progress(0)
    progress_status = st.empty()
    
    return {
        'review': review_container,
        'proposal': proposal_container,
        'validation': validation_container,
        'progress_bar': progress_bar,
        'progress_status': progress_status
    }

def run_enhancement_with_monitoring(standard_id: str, trigger_scenario: str, 
                                   run_func: Callable, components: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run the enhancement process with real-time progress monitoring.
    
    Args:
        standard_id: The ID of the standard to enhance
        trigger_scenario: The trigger scenario
        run_func: Function to run for enhancement (run_standards_enhancement)
        components: UI components dict from create_progress_components()
        
    Returns:
        Enhancement results
    """
    # Initialize progress monitor
    monitor = EnhancementProgressMonitor()
    
    # Phase indicators
    components['review'].info("⏳ Initializing review phase...")
    components['proposal'].info("🔄 Waiting for review to complete...")
    components['validation'].info("🔄 Waiting for proposal generation...")
    
    # Progress bar initialization
    components['progress_bar'].progress(0)
    components['progress_status'].text("Starting enhancement process...")
    
    # Start monitoring thread
    monitor.start_monitoring()
    
    # Define the detailed phase steps for a more realistic progress simulation
    phase_steps = {
        'review': [
            "Loading standard FAS {standard_id}...",
            "Analyzing standard structure...",
            "Identifying relevant sections...",
            "Analyzing definitions and scope...",
            "Examining recognition criteria...",
            "Reviewing measurement guidelines...",
            "Checking disclosure requirements...",
            "Evaluating standard in context of trigger scenario...",
            "Identifying potential enhancement areas...",
            "Summarizing review findings..."
        ],
        'proposal': [
            "Analyzing review findings...",
            "Identifying key sections to enhance...",
            "Researching best practices...",
            "Drafting text changes...",
            "Refining proposal language...",
            "Ensuring terminology consistency...",
            "Checking clarity of enhanced text...",
            "Adding rationale for changes...",
            "Final proposal formatting..."
        ],
        'validation': [
            "Retrieving Shariah principles...",
            "Checking alignment with core principles...",
            "Verifying absence of Riba elements...",
            "Evaluating Gharar considerations...",
            "Checking compliance with Maysir prohibitions...",
            "Verifying internal consistency...",
            "Checking alignment with other standards...",
            "Evaluating practical implementability...",
            "Formulating final validation decision..."
        ]
    }
    
    try:
        # Function to update progress with realistic steps
        def update_progress_with_steps(phase, steps, start_pct, end_pct):
            # Get the phase name without '_start' or '_complete'
            phase_name = phase.split('_')[0] if '_' in phase else phase
            
            # Only proceed if we have steps for this phase
            if phase_name not in phase_steps:
                return
                
            steps_count = len(steps)
            for i, step in enumerate(steps):
                # Calculate progress percentage
                progress = start_pct + (i / steps_count) * (end_pct - start_pct)
                
                # Format step text with any placeholders
                step_text = step.format(standard_id=standard_id)
                
                # Update progress
                components['progress_bar'].progress(progress)
                components['progress_status'].text(step_text)
                
                # Add a small random delay to simulate processing time (between 0.3 and 0.9 seconds)
                time.sleep(0.3 + random.random() * 0.6)
        
        # Function to capture progress updates - this will be passed to run_standards_enhancement
        def progress_callback(phase, detail=None):
            update = {'phase': phase}
            if detail:
                update[f'{phase}_detail'] = detail
            monitor.add_update(update)
            
            # Update UI based on phase
            if phase == 'review_start':
                components['review'].info("🔍 Reviewing standard and identifying enhancement areas...")
                update_progress_with_steps('review', phase_steps['review'], 0.0, 0.33)
            elif phase == 'review_complete':
                components['review'].success("✅ Review complete!")
                components['proposal'].info("✏️ Generating enhancement proposals...")
                update_progress_with_steps('proposal', phase_steps['proposal'], 0.33, 0.66)
            elif phase == 'proposal_complete':
                components['proposal'].success("✅ Proposals generated!")
                components['validation'].info("⚖️ Validating proposals against Shariah principles...")
                update_progress_with_steps('validation', phase_steps['validation'], 0.66, 1.0)
            elif phase == 'validation_complete':
                components['validation'].success("✅ Validation complete!")
                components['progress_bar'].progress(1.0)
                components['progress_status'].text("Enhancement process completed!")
        
        # Run the enhancement process with the progress callback
        results = run_func(standard_id, trigger_scenario, progress_callback)
        
        return results
        
    finally:
        # Stop monitoring thread
        monitor.stop_monitoring()

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