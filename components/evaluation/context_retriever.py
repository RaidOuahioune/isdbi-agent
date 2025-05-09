"""
Context retrieval module for the evaluation system.
This module provides functionality to retrieve relevant content from the vector database.
"""

from typing import Dict, Any, List, Optional
import logging

# Import the retreiver (already implemented in the base system)
from retreiver import retriever

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def retrieve_evaluation_context(
    prompt: str, response: str, k: int = 5
) -> List[Dict[str, str]]:
    """
    Retrieve relevant context from the vector database for evaluation.

    Args:
        prompt: The original user prompt
        response: The system response being evaluated
        k: Number of documents to retrieve

    Returns:
        List of retrieved documents
    """
    # Create a combined query from both prompt and response
    # This approach retrieves context relevant to both the input and output
    combined_query = f"""
    User prompt: {prompt}
    
    System response key points:
    {_extract_key_points(response)}
    """

    logger.info(
        f"Retrieving context for evaluation with query: {combined_query[:100]}..."
    )

    # Retrieve relevant documents
    nodes = retriever.retrieve(combined_query)

    # Convert nodes to dictionary format
    docs = []
    for node in nodes:
        docs.append({"text": node.text, "metadata": node.metadata})

    logger.info(f"Retrieved {len(docs)} context documents for evaluation")
    return docs


def retrieve_standard_specific_context(
    standard_id: str, k: int = 3
) -> List[Dict[str, str]]:
    """
    Retrieve specific context about a standard from the vector database.

    Args:
        standard_id: The ID of the standard (e.g., 'FAS 32')
        k: Number of documents to retrieve

    Returns:
        List of retrieved documents
    """
    # Create a query focused on the specific standard
    query = f"Detailed information about {standard_id} including key requirements and implementation guidance"

    # Retrieve relevant documents
    nodes = retriever.retrieve(query)

    # Convert nodes to dictionary format
    docs = []
    for node in nodes:
        docs.append({"text": node.text, "metadata": node.metadata})

    return docs


def _extract_key_points(text: str, max_points: int = 5) -> str:
    """
    Extract key points from a longer text to create a more focused query.

    Args:
        text: The text to extract key points from
        max_points: Maximum number of points to extract

    Returns:
        String with extracted key points
    """
    # Simple implementation: take first sentence from each paragraph
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

    key_points = []
    for paragraph in paragraphs[:max_points]:
        sentences = paragraph.split(".")
        if sentences:
            first_sentence = sentences[0].strip()
            if first_sentence and len(first_sentence) > 10:
                key_points.append(first_sentence)

    return "\n".join(key_points)
