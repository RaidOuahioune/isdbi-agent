"""
Expert evaluator agents for the ISDBI evaluation system.
These specialized agents assess different aspects of the system's outputs.
"""

from typing import Dict, Any, List, Optional
from langchain_core.messages import SystemMessage, HumanMessage
import logging

# Import base agent class
from components.agents.base_agent import Agent

# Import system prompts
from components.agents.prompts import (
    SHARIAH_EXPERT_SYSTEM_PROMPT,
    FINANCE_EXPERT_SYSTEM_PROMPT,
    STANDARDS_EXPERT_SYSTEM_PROMPT,
    REASONING_EXPERT_SYSTEM_PROMPT,
    PRACTICAL_EXPERT_SYSTEM_PROMPT,
)

# Import retreiver for direct access
from retreiver import retriever

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ExpertEvaluatorAgent(Agent):
    """Base class for expert evaluator agents with tool-calling capabilities."""

    def __init__(self, system_prompt: str):
        # Define the tools that will be available to the agent
        tools = [self._extract_keywords_tool, self._search_standards_tool]
        # Initialize with tools
        super().__init__(system_prompt=system_prompt, tools=tools)

    def _extract_keywords_tool(self, prompt: str) -> List[str]:
        """
        Tool to extract relevant keywords from a prompt for better retrieval.

        Args:
            prompt: The text to extract keywords from

        Returns:
            List of extracted keywords
        """
        # Log the tool invocation
        logger.info(f"[TOOL CALL] Extracting keywords from text ({len(prompt)} chars)")

        # Use the LLM to extract keywords
        keyword_prompt = f"""
        Extract 10-15 important keywords or key phrases from the following text.
        Focus on domain-specific terminology, financial concepts, and Islamic finance terms.
        Return ONLY the keywords as a comma-separated list without any other text.
        
        TEXT:
        {prompt}
        """

        messages = [
            SystemMessage(
                content="You are a keyword extraction assistant that identifies the most relevant terms in financial and Islamic finance text."
            ),
            HumanMessage(content=keyword_prompt),
        ]  # Get keywords from the model
        try:
            result = self.llm.invoke(messages)

            # Debug the result object and its content
            logger.info(f"[TOOL RESULT] Result type: {type(result)}")

            if hasattr(result, "content"):
                logger.info(f"[TOOL RESULT] Content: {result.content}")
                keywords_text = result.content.strip()
            else:
                logger.error("[TOOL RESULT] Result has no 'content' attribute")
                logger.info(f"[TOOL RESULT] Result attributes: {dir(result)}")
                # Try to get content from different attribute or convert to string
                if hasattr(result, "text"):
                    keywords_text = result.text.strip()
                elif hasattr(result, "message"):
                    keywords_text = result.message.content.strip()
                else:
                    keywords_text = str(result).strip()

            print(f"\n===== LLM RESULT =====")
            print(f"Raw result: {keywords_text}")
            print("======================\n")

            # Split by commas and clean up each keyword
            keywords = [k.strip() for k in keywords_text.split(",")]
            # Filter out any empty keywords
            keywords = [k for k in keywords if k]

            # Debug log the extracted keywords
            logger.info(f"[TOOL RESULT] Extracted keywords: {keywords}")
            print(f"\n===== EXTRACTED KEYWORDS =====")
            print(f"Number of keywords: {len(keywords)}")
            print(f"Keywords: {', '.join(keywords)}")
            print("==============================\n")

            return keywords
        except Exception as e:
            logging.error(f"Error extracting keywords: {e}")
            # Return a minimal set of keywords from the original prompt
            fallback_keywords = prompt.split()[:10]
            logger.warning(
                f"[TOOL FALLBACK] Using simple word splitting: {fallback_keywords}"
            )
            return fallback_keywords

    def _search_standards_tool(self, query: str) -> List[Dict[str, str]]:
        """
        Tool to search the vector database for relevant context.

        Args:
            query: The search query

        Returns:
            List of relevant documents
        """
        # Log the tool invocation
        logger.info(f"[TOOL CALL] Searching standards with query: {query}")

        try:
            # Get the nodes from the retriever
            nodes = retriever.retrieve(query)

            # Convert to a format suitable for the agent
            docs = []
            for node in nodes[:5]:  # Limit to top 5 for relevance
                docs.append(
                    {
                        "text": node.text,
                        "metadata": node.metadata if hasattr(node, "metadata") else {},
                    }
                )

            # Debug log the search results
            logger.info(f"[TOOL RESULT] Found {len(docs)} relevant documents")
            print(f"\n===== SEARCH RESULTS =====")
            print(f"Query: {query}")
            print(f"Number of documents found: {len(docs)}")

            # Print snippets of each document
            for i, doc in enumerate(docs):
                text = doc.get("text", "")
                snippet = text[:100] + "..." if len(text) > 100 else text
                print(f"\nDocument {i + 1}:")
                print(f"  {snippet}")

                # Print metadata if available
                if doc.get("metadata"):
                    print(f"  Metadata: {doc.get('metadata')}")

            print("==========================\n")

            return docs
        except Exception as e:
            logger.error(f"Error searching standards: {e}")
            print(f"\n===== SEARCH ERROR =====")
            print(f"Query: {query}")
            print(f"Error: {e}")
            print("=======================\n")
            return []

    def evaluate(
        self,
        prompt: str,
        response: str,
        context: Optional[List[Dict[str, str]]] = None,
        fetch_additional_context: bool = True,
    ) -> Dict[str, Any]:
        """
        Evaluate a response based on a prompt and optional context.

        Args:
            prompt: The original user prompt
            response: The system response to be evaluated
            context: Optional list of context documents from vector DB
            fetch_additional_context: Whether to fetch additional context using tools

        Returns:
            Dict containing evaluation scores and justifications
        """
        # Initial context provided or empty
        context_docs = context or []

        # If requested, fetch additional context using tool calls
        additional_context = []
        if fetch_additional_context:
            try:
                # Extract keywords from both prompt and response
                prompt_keywords = self._extract_keywords_tool(prompt)
                response_keywords = self._extract_keywords_tool(response)

                # Combine keywords but avoid duplicates
                all_keywords = list(set(prompt_keywords + response_keywords))

                # Use keywords to search for relevant context
                keyword_query = " ".join(all_keywords[:15])  # Use top 15 keywords
                additional_context = self._search_standards_tool(keyword_query)

                # Add the additional context to existing context
                context_docs.extend(additional_context)
            except Exception as e:
                logging.error(f"Error fetching additional context: {e}")

        # Format all context for inclusion in the prompt
        context_str = ""
        if context_docs:
            context_str = "Relevant Context:\n"
            for i, doc in enumerate(context_docs, 1):
                context_str += f"Document {i}:\n{doc.get('text', '')}\n\n"

        # Prepare message for evaluation with all available context
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(
                content=f"""Please evaluate this response to the given prompt:
                
User Prompt:
{prompt}

System Response:
{response}

{context_str}

Provide a detailed evaluation covering:
1. Strengths of the response
2. Weaknesses or issues identified
3. Specific examples supporting your evaluation
4. A numerical score (0-10) for each criterion in your domain of expertise
5. Overall assessment summary
                """
            ),
        ]

        # Get evaluation result
        evaluation_response = self.llm.invoke(messages)

        # Process the response to extract scores
        scores = self._extract_scores(evaluation_response.content)

        # Return full evaluation with metadata about the context used
        return {
            "evaluation": evaluation_response.content,
            "scores": scores,
            "context_used": {
                "provided_context_count": len(context or []),
                "additional_context_count": len(additional_context),
                "keywords_used": all_keywords if fetch_additional_context else [],
            },
        }

    def _extract_scores(self, evaluation_text: str) -> Dict[str, float]:
        """
        Extract numerical scores from evaluation text.
        This is a simple implementation - in production, this would use regex
        or more sophisticated parsing to extract structured scores.

        Returns:
            Dict of criterion -> score mappings
        """
        # Default implementation - subclasses may override for specialized extraction
        lines = evaluation_text.split("\n")
        scores = {}

        for line in lines:
            # Look for lines with score pattern like "Criterion: X/10" or "Criterion Score: X"
            if ":" in line and any(
                score in line.lower() for score in ["score", "/10", "rating", "points"]
            ):
                parts = line.split(":")
                if len(parts) >= 2:
                    criterion = parts[0].strip()
                    # Try to extract a number from the score part
                    score_text = parts[1].strip()
                    for word in score_text.split():
                        try:
                            score = float(word.replace("/10", ""))
                            scores[criterion] = score
                            break
                        except ValueError:
                            continue

        return scores


class ShariahExpertAgent(ExpertEvaluatorAgent):
    """Expert agent for evaluating Shariah compliance."""

    def __init__(self):
        super().__init__(system_prompt=SHARIAH_EXPERT_SYSTEM_PROMPT)


class FinanceExpertAgent(ExpertEvaluatorAgent):
    """Expert agent for evaluating financial accuracy."""

    def __init__(self):
        super().__init__(system_prompt=FINANCE_EXPERT_SYSTEM_PROMPT)


class StandardsExpertAgent(ExpertEvaluatorAgent):
    """Expert agent for evaluating standards compliance."""

    def __init__(self):
        super().__init__(system_prompt=STANDARDS_EXPERT_SYSTEM_PROMPT)


class ReasoningExpertAgent(ExpertEvaluatorAgent):
    """Expert agent for evaluating logical reasoning."""

    def __init__(self):
        super().__init__(system_prompt=REASONING_EXPERT_SYSTEM_PROMPT)


class PracticalExpertAgent(ExpertEvaluatorAgent):
    """Expert agent for evaluating practical application."""

    def __init__(self):
        super().__init__(system_prompt=PRACTICAL_EXPERT_SYSTEM_PROMPT)


# Initialize the expert agents
shariah_expert = ShariahExpertAgent()
finance_expert = FinanceExpertAgent()
standards_expert = StandardsExpertAgent()
reasoning_expert = ReasoningExpertAgent()
practical_expert = PracticalExpertAgent()
