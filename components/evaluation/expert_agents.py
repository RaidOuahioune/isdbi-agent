"""
Expert evaluator agents for the ISDBI evaluation system.
These specialized agents assess different aspects of the system's outputs.
"""

from typing import Dict, Any, List, Optional
from langchain_core.messages import SystemMessage, HumanMessage
import logging
from sklearn.feature_extraction.text import TfidfVectorizer

from components.evaluation.utils import DOMAIN_KEYWORDS_FIXED

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
    """Base class for expert evaluator agents with tool-calling capabilities."""  # Domain-specific keywords to boost in extraction for different agent types

    DOMAIN_KEYWORDS = DOMAIN_KEYWORDS_FIXED

    def __init__(self, system_prompt: str, domain: str = "general"):
        # Store the domain for specialized keyword extraction
        self.domain = domain
        # Define the tools that will be available to the agent
        tools = [self._extract_keywords_tool_using_tfidf, self._search_standards_tool]
        # Initialize with tools
        super().__init__(system_prompt=system_prompt, tools=tools)

    def _extract_keywords_tool_using_tfidf(self, prompt: str) -> List[str]:
        """
        Tool to extract keywords using TF-IDF from scikit-learn.
        Enhances extraction with domain-specific keywords.
        """
        logger.info(
            f"[TOOL CALL] Extracting keywords with domain-specific TF-IDF ({len(prompt)} chars)"
        )

        try:
            # Get domain-specific keywords for the current agent type
            domain_keywords = self.DOMAIN_KEYWORDS.get(self.domain, [])

            # Create TF-IDF vectorizer and prepare corpus
            vectorizer, corpus = self._prepare_tfidf_vectorizer_and_corpus(
                prompt, domain_keywords
            )

            # Get keyword scores using TF-IDF
            doc_scores = self._calculate_keyword_scores(
                vectorizer, corpus, domain_keywords
            )

            # Extract and refine the keywords
            keywords = self._extract_and_refine_keywords(doc_scores, domain_keywords)

            # Log the results
            self._log_extracted_keywords(keywords)

            return keywords

        except Exception as e:
            return self._fallback_keyword_extraction(prompt, e)

    def _prepare_tfidf_vectorizer_and_corpus(
        self, prompt: str, domain_keywords: List[str]
    ) -> tuple:
        """
        Prepare the TF-IDF vectorizer and corpus for keyword extraction.

        Args:
            prompt: The input text to extract keywords from
            domain_keywords: List of domain-specific keywords to boost

        Returns:
            Tuple of (vectorizer, corpus)
        """
        # Initialize vectorizer with appropriate parameters
        vectorizer = TfidfVectorizer(
            max_df=0.85,
            min_df=1,  # Lower minimum document frequency to capture domain terms
            stop_words="english",
            use_idf=True,
            ngram_range=(1, 2),
        )

        # Create a corpus with the prompt and some dummy documents
        # (TF-IDF works better with multiple documents)
        corpus = [prompt] + [
            prompt[i : i + 100]
            for i in range(0, len(prompt), 100)
            if i + 100 < len(prompt)
        ]

        # Add domain-specific keywords to enhance the corpus
        if domain_keywords:
            # Create a document with just domain keywords to boost their importance
            domain_doc = " ".join(domain_keywords)
            corpus.append(domain_doc)
            logger.info(
                f"[DOMAIN] Added {len(domain_keywords)} domain keywords for {self.domain} expertise"
            )

        return vectorizer, corpus

    def _calculate_keyword_scores(
        self, vectorizer, corpus, domain_keywords: List[str]
    ) -> Dict[str, float]:
        """
        Calculate TF-IDF scores for keywords and boost domain-specific terms.

        Args:
            vectorizer: The TF-IDF vectorizer
            corpus: The document corpus
            domain_keywords: List of domain-specific keywords to boost

        Returns:
            Dictionary mapping keywords to their boosted scores
        """
        # Fit and transform the corpus
        tfidf_matrix = vectorizer.fit_transform(corpus)

        # Get feature names
        feature_names = vectorizer.get_feature_names_out()

        # Get scores for the first document (our prompt)
        doc_scores = dict(zip(feature_names, tfidf_matrix[0].toarray()[0]))

        # Apply domain-specific boosting
        doc_scores = self._boost_domain_keywords(
            doc_scores, domain_keywords, feature_names
        )

        return doc_scores

    def _boost_domain_keywords(
        self, doc_scores: Dict[str, float], domain_keywords: List[str], feature_names
    ) -> Dict[str, float]:
        """
        Boost scores of domain-specific keywords and related terms.

        Args:
            doc_scores: Original keyword scores
            domain_keywords: List of domain-specific keywords to boost
            feature_names: All features/terms from the vectorizer

        Returns:
            Dictionary with boosted scores
        """
        for keyword in domain_keywords:
            # Boost exact matches of domain keywords
            if keyword in doc_scores:
                doc_scores[keyword] *= 1.5  # Boost domain keywords by 50%

            # Also boost bi-grams containing domain keywords
            for feature in feature_names:
                if keyword in feature and feature in doc_scores:
                    doc_scores[feature] *= 1.3  # Boost by 30%

        return doc_scores

    def _extract_and_refine_keywords(
        self, doc_scores: Dict[str, float], domain_keywords: List[str]
    ) -> List[str]:
        """
        Extract top keywords and ensure domain-specific terms are included.

        Args:
            doc_scores: Dictionary of keyword scores
            domain_keywords: List of domain-specific keywords

        Returns:
            List of extracted keywords
        """
        # Sort by score and take top 15
        sorted_keywords = sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)
        keywords = [keyword for keyword, _ in sorted_keywords[:15]]

        # Try to include domain-specific keywords if they're not already present
        domain_keywords_to_add = [
            k for k in domain_keywords if k in doc_scores and k not in keywords
        ][:3]

        if domain_keywords_to_add and len(keywords) > len(domain_keywords_to_add):
            # Replace the lowest-scoring keywords with domain keywords
            keywords = keywords[: -len(domain_keywords_to_add)] + domain_keywords_to_add

        return keywords

    def _log_extracted_keywords(self, keywords: List[str]) -> None:
        """Log the extracted keywords for debugging."""
        logger.info(f"[TOOL RESULT] Extracted keywords for {self.domain}: {keywords}")
        print(f"\n===== EXTRACTED KEYWORDS ({self.domain.upper()}) =====")
        print(f"Number of keywords: {len(keywords)}")
        print(f"Keywords: {', '.join(keywords)}")
        print("============================================\n")

    def _fallback_keyword_extraction(self, prompt: str, error) -> List[str]:
        """
        Fallback method for keyword extraction when TF-IDF fails.

        Args:
            prompt: Original input text
            error: Exception that occurred

        Returns:
            List of keywords extracted using simple approach
        """
        logging.error(f"Error extracting keywords with domain-specific TF-IDF: {error}")

        # Simple approach: split by word and filter
        words = prompt.lower().split()
        keywords = list(set([w for w in words if len(w) > 3]))[:12]

        # Add some domain keywords as fallback
        domain_keywords = self.DOMAIN_KEYWORDS.get(self.domain, [])[:3]
        keywords.extend(domain_keywords)

        # Log the fallback results
        logger.info(f"[FALLBACK] Using simple keyword extraction: {keywords[:15]}")

        return keywords[:15]

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
                )  # Debug log the search results
            logger.info(f"[TOOL RESULT] Found {len(docs)} relevant documents")
            print("\n===== SEARCH RESULTS =====")
            print(f"Query: {query}")
            print(f"Number of documents found: {len(docs)}ShariahExpertAgent")

            # Print snippets of each document
            for i, doc in enumerate(docs):
                text = doc.get("text", "")
                # snippet = text[:100] + "..." if len(text) > 100 else text
                print(f"\nDocument {i + 1}:")
                print(f"  {text}")

                # Print metadata if available
                if doc.get("metadata"):
                    print(f"  Metadata: {doc.get('metadata')}")

            print("==========================\n")

            return docs
        except Exception as e:
            logger.error(f"Error searching standards: {e}")
            print("\n===== SEARCH ERROR =====")
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
                prompt_keywords = self._extract_keywords_tool_using_tfidf(prompt)
                response_keywords = self._extract_keywords_tool_using_tfidf(response)

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
        super().__init__(system_prompt=SHARIAH_EXPERT_SYSTEM_PROMPT, domain="shariah")


class FinanceExpertAgent(ExpertEvaluatorAgent):
    """Expert agent for evaluating financial accuracy."""

    def __init__(self):
        super().__init__(system_prompt=FINANCE_EXPERT_SYSTEM_PROMPT, domain="finance")


class StandardsExpertAgent(ExpertEvaluatorAgent):
    """Expert agent for evaluating standards compliance."""

    def __init__(self):
        super().__init__(
            system_prompt=STANDARDS_EXPERT_SYSTEM_PROMPT, domain="standards"
        )


class ReasoningExpertAgent(ExpertEvaluatorAgent):
    """Expert agent for evaluating logical reasoning."""

    def __init__(self):
        super().__init__(
            system_prompt=REASONING_EXPERT_SYSTEM_PROMPT, domain="reasoning"
        )


class PracticalExpertAgent(ExpertEvaluatorAgent):
    """Expert agent for evaluating practical application."""

    def __init__(self):
        super().__init__(
            system_prompt=PRACTICAL_EXPERT_SYSTEM_PROMPT, domain="practical"
        )


# Initialize the expert agents
shariah_expert = ShariahExpertAgent()
finance_expert = FinanceExpertAgent()
standards_expert = StandardsExpertAgent()
reasoning_expert = ReasoningExpertAgent()
practical_expert = PracticalExpertAgent()
