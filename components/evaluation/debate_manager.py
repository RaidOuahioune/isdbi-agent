"""
Debate Manager for orchestrating multi-round debates between expert agents.
This module implements the structured debate process where agents present arguments
and counter-arguments over multiple rounds to reach a nuanced evaluation.
"""

from typing import Dict, Any, List, Optional, Tuple, Union
import logging
import time
import re

# Import debate agents
from components.evaluation.debate_agents import (
    shariah_proponent,
    shariah_critic,
    finance_proponent,
    finance_critic,
    legal_proponent,
    legal_critic,
)

# Import context retriever
from components.evaluation.context_retriever import context_retriever

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DebateManager:
    """
    Manager class that coordinates multi-round debates between expert agents.
    """

    def __init__(self, max_rounds: int = 3):
        """
        Initialize the debate manager.

        Args:
            max_rounds: Maximum number of rounds per debate
        """
        self.max_rounds = max_rounds

        # Initialize debate pairs
        self.debate_pairs = {
            "shariah": (shariah_proponent, shariah_critic),
            "finance": (finance_proponent, finance_critic),
            "legal": (legal_proponent, legal_critic),
        }

    def _conduct_single_domain_debate(
        self,
        prompt: str,
        response: str,
        domain: str,
        context: Optional[List[Dict[str, str]]] = None,
    ) -> Dict[str, Any]:
        """
        Conduct a debate for a single domain.

        Args:
            prompt: The original user prompt
            response: The response being evaluated
            domain: The domain to debate (shariah, finance, legal)
            context: Optional context documents for this domain

        Returns:
            Dict containing debate results for a single domain
        """
        if domain not in self.debate_pairs:
            return {
                "error": f"Invalid domain: {domain}. Valid options are: {list(self.debate_pairs.keys())}"
            }

        # Get the proponent and critic agents for this domain
        proponent, critic = self.debate_pairs[domain]

        # Get context if not provided
        debate_context = context or []
        if not debate_context:
            combined_text = f"{prompt}\n\n{response}"
            # Use the global context_retriever
            debate_context = context_retriever.get_evaluation_context(
                combined_text, domain
            ).get(domain, [])

        print("Debate Context: ", debate_context)
        # Initialize debate history
        debate_history = []

        logger.info(f"Starting {domain} debate with max {self.max_rounds} rounds")

        # Round 1: Proponent presents initial argument
        logger.info(f"Round 1: {domain} proponent presenting initial argument")
        initial_argument = proponent.present_argument(prompt, response, debate_context)
        debate_history.append(initial_argument)

        # Conduct the debate for remaining rounds
        current_round = 2
        while current_round <= self.max_rounds:
            # Even rounds: Critic presents counter-argument
            if current_round % 2 == 0:
                logger.info(
                    f"Round {current_round}: {domain} critic presenting counter-argument"
                )
                counter_argument = critic.present_counter_argument(
                    prompt, response, debate_context, debate_history
                )
                debate_history.append(counter_argument)
            # Odd rounds: Proponent responds to critique
            else:
                logger.info(
                    f"Round {current_round}: {domain} proponent responding to critique"
                )
                proponent_response = proponent.present_counter_argument(
                    prompt, response, debate_context, debate_history
                )
                debate_history.append(proponent_response)

            current_round += 1
            time.sleep(1)  # Small delay between rounds

        # Generate debate summary from the proponent agent
        logger.info(f"Generating final summary of {domain} debate")
        debate_summary = proponent.summarize_debate(prompt, response, debate_history)

        # Return results
        return {
            "domain": domain,
            "rounds_completed": len(debate_history),
            "debate_history": debate_history,
            "summary": debate_summary,
            "timestamp": time.time(),
        }

    def conduct_debate(
        self,
        prompt: str,
        response: str,
        domains: Union[str, List[str]],
        context: Optional[Dict[str, List[Dict[str, str]]]] = None,
    ) -> Dict[str, Any]:
        """
        Conduct multi-round debates for one or more domains.

        Args:
            prompt: The original user prompt
            response: The response being evaluated
            domains: A single domain or list of domains to debate (shariah, finance, legal)
            context: Optional context documents by domain

        Returns:
            Dict containing debate results, arguments, and summaries for all domains
        """
        # Convert single domain to list for consistent processing
        if isinstance(domains, str):
            # If only one domain is provided, just run for that domain
            if context and domains in context:
                domain_context = context[domains]
            else:
                domain_context = None
            return self._conduct_single_domain_debate(
                prompt, response, domains, domain_context
            )

        # Multiple domains - validate all domains
        invalid_domains = [d for d in domains if d not in self.debate_pairs]
        if invalid_domains:
            return {
                "error": f"Invalid domain(s): {invalid_domains}. Valid options are: {list(self.debate_pairs.keys())}"
            }

        # Initialize results container
        all_debate_results = {}

        # Process each domain
        for domain in domains:
            logger.info(f"Starting debate for domain: {domain}")

            # Get context for this domain if provided
            domain_specific_context = None
            print("FULL CONTEXT: ", context)
            if context and domain in context:
                print("CONDITIONED: ", context[domain])
                domain_specific_context = context[domain]

            # Conduct debate for this domain
            debate_result = self._conduct_single_domain_debate(
                prompt=prompt,
                response=response,
                domain=domain,
                context=domain_specific_context,
            )

            # Add to results
            all_debate_results[domain] = debate_result

        # Aggregate results across domains if multiple domains
        if len(domains) > 1:
            aggregated_assessment = self._aggregate_debate_results(all_debate_results)

            return {
                "individual_debates": all_debate_results,
                "aggregated_assessment": aggregated_assessment,
                "domains": domains,
            }
        else:
            # If we reached here with single domain, just return that result
            return all_debate_results[domains[0]]

    def _aggregate_debate_results(
        self, debate_results: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Aggregate results from multiple domain debates.

        Args:
            debate_results: Results from individual domain debates

        Returns:
            Dict containing aggregated assessment
        """
        # Extract scores from debate summaries
        scores = {}
        key_points = []
        strengths = []
        weaknesses = []

        for domain, result in debate_results.items():
            summary = result.get("summary", {}).get("summary", "")

            # Try to extract score from summary
            score_match = re.search(r"(\d+(?:\.\d+)?)\s*\/\s*10", summary)
            if score_match:
                scores[domain] = float(score_match.group(1))

            # Extract key points
            lines = summary.split("\n")
            for line in lines:
                line = line.strip()
                if line and len(line) > 20:  # Simple filter for substantive lines
                    if any(
                        strength_word in line.lower()
                        for strength_word in ["strength", "positive", "advantage"]
                    ):
                        strengths.append(f"[{domain.capitalize()}] {line}")
                    elif any(
                        weakness_word in line.lower()
                        for weakness_word in [
                            "weakness",
                            "limitation",
                            "issue",
                            "concern",
                        ]
                    ):
                        weaknesses.append(f"[{domain.capitalize()}] {line}")
                    elif (
                        len(key_points) < 10
                    ):  # Limit key points to avoid excessive length
                        key_points.append(f"[{domain.capitalize()}] {line}")

        # Calculate overall score if scores are available
        overall_score = None
        if scores:
            overall_score = sum(scores.values()) / len(scores)

        return {
            "domain_scores": scores,
            "overall_score": overall_score,
            "key_points": key_points[:10],  # Limit to top 10 points
            "strengths": strengths[:5],  # Limit to top 5 strengths
            "weaknesses": weaknesses[:5],  # Limit to top 5 weaknesses
        }


# Initialize debate manager
debate_manager = DebateManager(max_rounds=3)
