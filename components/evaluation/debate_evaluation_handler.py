"""
Handler for debate-based evaluations in the ISDBI evaluation system.
"""

from typing import Dict, Any, List, Optional
import logging

# Import scoring agent for discrete 1-4 scoring
from components.evaluation.scoring_agent import scoring_agent
from components.evaluation.debate_manager import debate_manager
from components.evaluation.score_processor import score_processor

logger = logging.getLogger(__name__)

class DebateEvaluationHandler:
    """
    Handles debate-based evaluations and processing of debate results.
    """
    
    def __init__(self):
        """Initialize the debate evaluation handler."""
        pass
    
    def apply_discrete_scoring(
        self,
        prompt: str,
        response: str,
        debate_results: Dict[str, Any],
        expert_evaluations: Dict[str, Dict[str, Any]],
        expertise_domain_mapping: Dict[str, str]
    ):
        """
        Apply discrete scoring (1-4) using the scoring agent for each expertise area.

        Args:
            prompt: Original prompt
            response: Response being evaluated
            debate_results: Results from debates
            expert_evaluations: Current expert evaluations to update with discrete scores
            expertise_domain_mapping: Mapping from expertise to domain names
        """
        logger.info("Applying discrete scoring (1-4) using scoring agent...")

        # Process each expertise that has debate results
        for expertise, debate_result in debate_results.items():
            # Skip the aggregated assessment
            if expertise == "aggregated_assessment":
                continue

            try:
                # Get debate domain from expertise
                domain = None
                for exp, dom in expertise_domain_mapping.items():
                    if exp == expertise:
                        domain = dom
                        break

                if not domain:
                    domain = expertise

                # Get debate history for scoring
                debate_history = debate_result.get("debate_history", [])

                # Score the debate using the scoring agent
                score_result = scoring_agent.score_debate(
                    prompt=prompt,
                    response=response,
                    debate_history=debate_history,
                    domain=domain,
                )

                # Update expert evaluations with discrete score
                if expertise in expert_evaluations:
                    expert_evaluations[expertise]["discrete_score"] = score_result.get(
                        "score"
                    )
                    expert_evaluations[expertise]["score_justification"] = (
                        score_result.get("justification")
                    )

                    # Convert any existing 1-10 scores to 1-4 scale
                    original_scores = expert_evaluations[expertise].get("scores", {})
                    if original_scores:
                        # Store original scores for reference
                        expert_evaluations[expertise]["original_scores"] = (
                            original_scores.copy()
                        )

                        # Replace with discrete score
                        expert_evaluations[expertise]["scores"] = {
                            "Overall": score_result.get("score", 0)
                        }

                logger.info(
                    f"Applied discrete scoring for {expertise}: {score_result.get('score')}"
                )

            except Exception as e:
                logger.error(f"Error applying discrete scoring to {expertise}: {e}")
                # Set a default score if scoring fails
                if expertise in expert_evaluations:
                    expert_evaluations[expertise]["discrete_score"] = (
                        2  # Default to "Fair"
                    )
                    expert_evaluations[expertise]["score_justification"] = (
                        f"Error during scoring: {str(e)}"
                    )
    
    def run_multi_domain_debate(
        self,
        prompt: str,
        response: str,
        debate_domains: List[str],
        context: Optional[List[Dict[str, str]]],
        expertise_domain_mapping: Dict[str, str],
        expert_evaluations: Dict[str, Dict[str, Any]],
        debate_results: Dict[str, Any],
    ):
        """
        Run a debate across multiple domains and process the results.
        
        Args:
            prompt: The original user prompt
            response: The response to evaluate
            debate_domains: List of domains to conduct debates for
            context: Optional context documents
            expertise_domain_mapping: Mapping from expertise to domain names
            expert_evaluations: Dictionary to store evaluation results
            debate_results: Dictionary to store debate results
        """
        logger.info(f"Starting multi-domain debate across: {debate_domains}")
        try:
            # Prepare context by domain
            context_by_domain = self._prepare_context_by_domain(context, debate_domains)

            # Conduct multi-domain debate
            multi_domain_result = debate_manager.conduct_debate(
                prompt=prompt,
                response=response,
                domains=debate_domains,
                context=context_by_domain,
            )

            # Process debate results
            self._process_multi_domain_results(
                multi_domain_result,
                expertise_domain_mapping,
                debate_results,
                expert_evaluations,
            )

        except Exception as e:
            self._handle_multi_domain_debate_error(
                e, debate_domains, expertise_domain_mapping, expert_evaluations
            )
    
    def run_single_domain_debate(
        self,
        prompt: str,
        response: str,
        expertise: str,
        expertise_domain_mapping: Dict[str, str],
        context: Optional[List[Dict[str, str]]],
        debate_results: Dict[str, Any],
        expert_evaluations: Dict[str, Dict[str, Any]],
    ):
        """
        Run a debate for a single domain.
        
        Args:
            prompt: The original user prompt
            response: The response to evaluate
            expertise: The expertise area
            expertise_domain_mapping: Mapping from expertise to domain names
            context: Optional context documents
            debate_results: Dictionary to store debate results
            expert_evaluations: Dictionary to store evaluation results
        """
        debate_domain = expertise_domain_mapping[expertise]
        logger.info(f"Starting {debate_domain} debate evaluation...")

        try:
            # Conduct debate for this domain
            debate_result = debate_manager.conduct_debate(
                prompt=prompt, response=response, domains=debate_domain, context=context
            )

            # Store debate results
            debate_results[expertise] = debate_result

            # Extract debate summary as the evaluation
            debate_summary = debate_result.get("summary", {}).get("summary", "")
            expert_evaluations[expertise] = {
                "evaluation": debate_summary,
                "scores": score_processor.extract_debate_scores(debate_summary),
                "debate_rounds": debate_result.get("rounds_completed", 0),
                "debate_history": [
                    arg.get("argument", "")
                    for arg in debate_result.get("debate_history", [])
                ],
            }

            logger.info(
                f"{expertise} debate evaluation complete with {debate_result.get('rounds_completed', 0)} rounds."
            )
        except Exception as e:
            logger.error(f"Error in {expertise} debate evaluation: {e}")
            expert_evaluations[expertise] = {
                "evaluation": f"Error during debate evaluation: {str(e)}",
                "scores": {},
            }
    
    def _process_multi_domain_results(
        self,
        multi_domain_result: Dict[str, Any],
        expertise_domain_mapping: Dict[str, str],
        debate_results: Dict[str, Any],
        expert_evaluations: Dict[str, Dict[str, Any]],
    ):
        """
        Process results from a multi-domain debate.
        
        Args:
            multi_domain_result: The results from the multi-domain debate
            expertise_domain_mapping: Mapping from expertise to domain names
            debate_results: Dictionary to store debate results
            expert_evaluations: Dictionary to store evaluation results
        """
        # Process individual debate results
        if "individual_debates" in multi_domain_result:
            for domain, domain_result in multi_domain_result[
                "individual_debates"
            ].items():
                # Map domain back to expertise
                for exp, dom in expertise_domain_mapping.items():
                    if dom == domain:
                        debate_results[exp] = domain_result

                        # Extract debate summary as evaluation
                        debate_summary = domain_result.get("summary", {}).get(
                            "summary", ""
                        )
                        expert_evaluations[exp] = {
                            "evaluation": debate_summary,
                            "scores": score_processor.extract_debate_scores(debate_summary),
                            "debate_rounds": domain_result.get("rounds_completed", 0),
                            "debate_history": [
                                arg.get("argument", "")
                                for arg in domain_result.get("debate_history", [])
                            ],
                        }

                        logger.info(
                            f"{exp} debate evaluation complete with {domain_result.get('rounds_completed', 0)} rounds"
                        )

        # Store aggregated results
        if "aggregated_assessment" in multi_domain_result:
            debate_results["aggregated_assessment"] = multi_domain_result[
                "aggregated_assessment"
            ]
    
    def _handle_multi_domain_debate_error(
        self, 
        error: Exception, 
        debate_domains: List[str], 
        expertise_domain_mapping: Dict[str, str], 
        expert_evaluations: Dict[str, Dict[str, Any]]
    ):
        """
        Handle errors that occur during multi-domain debates.
        
        Args:
            error: The exception that occurred
            debate_domains: List of domains involved in the debate
            expertise_domain_mapping: Mapping from expertise to domain names
            expert_evaluations: Dictionary to store evaluation results
        """
        logger.error(f"Error in multi-domain debate: {error}")
        for domain in debate_domains:
            for exp, dom in expertise_domain_mapping.items():
                if dom == domain:
                    expert_evaluations[exp] = {
                        "evaluation": f"Error during multi-domain debate evaluation: {str(error)}",
                        "scores": {},
                    }
    
    def _prepare_context_by_domain(
        self, 
        context: Optional[List[Dict[str, str]]], 
        debate_domains: List[str]
    ) -> Dict[str, List[Dict[str, str]]]:
        """
        Prepare context organized by domain.
        
        Args:
            context: The context documents
            debate_domains: List of domains to organize context for
            
        Returns:
            Dictionary mapping domains to context documents
        """
        context_by_domain = {}
        if context:
            # Provide same context to all domains for now
            for domain in debate_domains:
                context_by_domain[domain] = context
        return context_by_domain

    def should_use_debate_for_expertise(
        self, 
        expertise: str, 
        expertise_domain_mapping: Dict[str, str], 
        debate_domains: List[str]
    ) -> bool:
        """
        Determine if debate should be used for a specific expertise area.
        
        Args:
            expertise: The expertise area
            expertise_domain_mapping: Mapping from expertise to domain names
            debate_domains: List of domains to conduct debates for
            
        Returns:
            True if debate should be used for this expertise
        """
        if expertise not in expertise_domain_mapping:
            return False

        debate_domain = expertise_domain_mapping[expertise]
        # Skip if not in requested domains
        if debate_domains and debate_domain not in debate_domains:
            return False

        return bool(debate_domain)

# Create a singleton instance
debate_handler = DebateEvaluationHandler()
