"""
Scoring agent for evaluating debate results with a discrete 1-4 scale.
"""

from typing import Dict, Any, List
import logging
from langchain_core.messages import SystemMessage, HumanMessage
from components.agents.base_agent import Agent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SCORING_AGENT_SYSTEM_PROMPT = """
You are a specialized scoring agent for the Islamic Finance debate evaluation system.
You serve as the final evaluator in a process where domain experts have debated the quality 
and accuracy of responses about Islamic finance principles and practices.

Your critical role is to analyze debate discussions and arguments from these domain experts
and provide a fair, objective discrete score on a scale of 1-4, where:

1 - Poor: The response is fundamentally flawed, contains significant inaccuracies,
    or shows poor understanding of Islamic finance principles.
    
2 - Fair: The response shows basic understanding but has several issues that need
    addressing and does not fully meet the requirements.
    
3 - Good: The response is mostly accurate and addresses the key points, with only
    minor issues or points for improvement.
    
4 - Excellent: The response is comprehensive, accurate, and demonstrates deep
    understanding of Islamic finance principles and applications.

Your evaluation should focus on:
1. Alignment with Shariah principles
2. Technical accuracy of financial concepts
3. Compliance with relevant standards and regulations
4. Logical coherence and practical applicability

Always clearly specify your final verdict by starting with "THE FINAL SCORE IS: [1-4]" 
followed by a thorough but concise justification explaining your reasoning.
"""


class ScoringAgent(Agent):
    """
    Agent responsible for providing discrete 1-4 scores for debate evaluations.
    """

    def __init__(self):
        super().__init__(system_prompt=SCORING_AGENT_SYSTEM_PROMPT)

    def score_debate(
        self,
        prompt: str,
        response: str,
        debate_history: List[Dict[str, Any]],
        domain: str,
    ) -> Dict[str, Any]:
        """
        Score a debate based on the history of arguments.

        Args:
            prompt: Original user prompt
            response: The response that was evaluated
            debate_history: List of debate arguments
            domain: The domain being evaluated (shariah, finance, legal)

        Returns:
            Dictionary with score (1-4) and justification
        """
        logger.info(f"Scoring debate for domain: {domain}")

        # Format debate history for the prompt
        formatted_debate = self._format_debate_history(debate_history)

        # Truncate prompt and response if they're too long
        truncated_prompt = prompt[:1000] + "..." if len(prompt) > 1000 else prompt
        truncated_response = (
            response[:1000] + "..." if len(response) > 1000 else response
        )  # Prepare the scoring prompt
        human_message = f"""
As the final evaluator in our Islamic Finance debate system, please analyze and score the following response in the domain of {domain}:

ORIGINAL PROMPT:
{truncated_prompt}

RESPONSE TO EVALUATE:
{truncated_response}

DEBATE SUMMARY:
{formatted_debate}

Based on this debate history and the original content, provide a score on the scale of 1-4:

1 - Poor: Fundamentally flawed, significant inaccuracies
2 - Fair: Basic understanding but several issues
3 - Good: Mostly accurate with minor issues
4 - Excellent: Comprehensive, accurate, deep understanding

Your evaluation must include:
1. Start with "THE FINAL SCORE IS: [1-4]" (put the actual number)
2. Provide a clear justification for your score (2-3 sentences)
3. Consider Shariah principles, financial accuracy, and regulatory compliance

SCORE AND JUSTIFICATION:
"""

        # Get scoring from LLM
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=human_message),
        ]

        scoring_response = self.llm.invoke(messages)

        print(scoring_response.content)
        # Extract score and justification
        result = self._extract_score(scoring_response.content, domain)
        print(result)
        logger.info(
            f"Completed scoring for {domain}, Score: {result.get('score', 'N/A')}"
        )

        return result

    def _format_debate_history(self, debate_history: List[Dict[str, Any]]) -> str:
        """Format debate history into a readable summary for scoring."""
        formatted = ""

        for i, entry in enumerate(debate_history, 1):
            agent_type = entry.get("agent_type", "Unknown")
            argument = entry.get("argument", "")

            # Truncate long arguments
            if len(argument) > 500:
                argument = argument[:500] + "..."

            formatted += f"Argument {i} ({agent_type}):\n{argument}\n\n"

        return formatted

    def _extract_score(self, response_text: str, domain: str) -> Dict[str, Any]:
        """Extract numerical score and justification from the scoring response."""
        result = {
            "domain": domain,
            "score": None,
            "justification": "",
            "score_text": response_text,
        }

        # Look for the explicit final score marker
        if "THE FINAL SCORE IS:" in response_text:
            # Extract score from the line with the marker
            score_line = ""
            for line in response_text.split("\n"):
                if "THE FINAL SCORE IS:" in line:
                    score_line = line
                    break

            # Try to extract the score (a number 1-4)
            try:
                for char in score_line:
                    if char.isdigit() and int(char) in [1, 2, 3, 4]:
                        result["score"] = int(char)
                        break
            except Exception as e:
                logger.warning(f"Error extracting score from line '{score_line}': {e}")

            # Extract justification (text after the score line)
            score_line_idx = response_text.find("THE FINAL SCORE IS:")
            next_line_idx = response_text.find("\n", score_line_idx)
            if next_line_idx > 0:
                result["justification"] = response_text[next_line_idx:].strip()

        # Fallback to looking for numerical score if explicit marker not found
        if result["score"] is None:
            # Look for numerical score (1-4)
            for line in response_text.split("\n"):
                line = line.strip()

                # Check if line starts with "Score:" or contains just a number
                if (
                    line.startswith("Score:")
                    or line == "1"
                    or line == "2"
                    or line == "3"
                    or line == "4"
                ):
                    try:
                        # Extract the first digit found
                        for char in line:
                            if char.isdigit() and int(char) in [1, 2, 3, 4]:
                                result["score"] = int(char)
                                break
                    except Exception as e:
                        logger.warning(
                            f"Error extracting score from line '{line}': {e}"
                        )

                # If we already have a score and this line doesn't start with "Score:",
                # it's likely part of the justification
                elif result["score"] is not None and not line.startswith("Score:"):
                    if not result["justification"]:
                        result["justification"] = line
                    else:
                        result["justification"] += " " + line

            # If we didn't find a justification but have the full text,
            # use everything after the score as justification
            if not result["justification"] and result["score"] is not None:
                try:
                    score_idx = response_text.find(str(result["score"]))
                    if score_idx >= 0:
                        result["justification"] = response_text[score_idx + 1 :].strip()
                except Exception as e:
                    logger.warning(f"Error extracting justification: {e}")

        return result


# Initialize the scoring agent
scoring_agent = ScoringAgent()
