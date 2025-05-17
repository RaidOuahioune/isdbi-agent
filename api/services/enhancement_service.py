from typing import Dict, Any, Optional, Callable
from enhancement import run_standards_enhancement as enhancement_function

class EnhancementService:
    """Service for standards enhancement functionality."""
    
    @staticmethod
    def run_standards_enhancement(standard_id: str, 
                                trigger_scenario: str,
                                include_cross_standard_analysis: bool = True) -> Dict[str, Any]:
        """
        Run the standards enhancement process.
        
        Args:
            standard_id: The ID of the standard to enhance (e.g., "10" for FAS 10)
            trigger_scenario: The scenario that triggers the need for enhancement
            include_cross_standard_analysis: Whether to include cross-standard impact analysis
            
        Returns:
            Dict with the enhancement results
        """
        try:
            # Use a simple progress callback that just prints to the console in the API context
            def api_progress_callback(phase: str, detail: Optional[str] = None) -> None:
                import logging
                logging.info(f"Enhancement progress: {phase} - {detail if detail else ''}")
            
            # Call the enhancement function from the main module
            results = enhancement_function(
                standard_id=standard_id,
                trigger_scenario=trigger_scenario,
                progress_callback=api_progress_callback,
                include_cross_standard_analysis=include_cross_standard_analysis
            )
            
            return results
        except Exception as e:
            # Log the exception
            import logging
            logging.error(f"Error in standards enhancement: {str(e)}")
            # Re-raise a more informative exception
            raise Exception(f"Failed to process standards enhancement: {str(e)}")