from typing import Dict, Any, List, Optional
import logging
import os
from urllib.parse import urljoin

# Try to import requests, with a graceful fallback if not installed
try:
    import requests

    REQUESTS_AVAILABLE = True
except ImportError:
    logger = logging.getLogger(__name__)
    logger.warning("requests library not found. Install with: pip install requests")

    # Create a dummy requests module to prevent errors
    class DummyResponse:
        def __init__(self):
            self.status_code = 404
            self.text = "Error: requests module not available"

        def json(self):
            return {"error": "requests module not available", "clauses": []}

    class DummyRequests:
        def post(self, *args, **kwargs):
            logger = logging.getLogger(__name__)
            logger.warning("requests module not available. Using vector DB fallback.")
            return DummyResponse()

    # Create a dummy module object
    class DummyModule:
        pass

    requests = DummyModule()
    requests.post = DummyRequests().post
    REQUESTS_AVAILABLE = False

# Import the retreiver (already implemented in the base system)
from retreiver import retriever

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API configuration
CONTEXT_API_BASE_URL = os.environ.get(
    "CONTEXT_API_BASE_URL", "https://fd04-41-111-151-25.ngrok-free.app/"
)
CONTEXT_API_ENDPOINT = os.environ.get("CONTEXT_API_ENDPOINT", "api/fetch")
API_TIMEOUT = 1000000  # seconds


class ContextRetriever:
    """
    Class for retrieving relevant context for evaluation from various sources.
    """

    def __init__(self, domain_specific_sources: Optional[Dict[str, Any]] = None):
        """
        Initialize the context retriever.

        Args:
            domain_specific_sources: Optional dict mapping domain to specialized sources
        """
        self.domain_specific_sources = domain_specific_sources or {}
        self.logger = logging.getLogger(__name__)

    def get_evaluation_context(
        self, query: str, domain: Optional[str] = None
    ) -> Dict[str, List[Dict[str, str]]]:
        """
        Get context for evaluation, optionally filtered by domain.

        Args:
            query: The query to search for context (can be prompt + response)
            domain: Optional domain to filter context (shariah, finance, legal)

        Returns:
            Dict mapping domains to lists of context documents
        """
        self.logger.info(f"Retrieving context for evaluation: {query[:100]}...")

        # If domain is specified, only return that domain's context
        if domain:
            # Use the API for the specific domain
            domain_docs = self._retrieve_context(query, domain=domain)
            return {domain: domain_docs}

        # Otherwise organize by domain with some overlap
        domain_context = {}
        for d in ["shariah", "finance", "legal"]:
            # Fetch context for each domain using the API
            domain_context[d] = self._retrieve_context(query, domain=d)
            self.logger.info(
                f"Retrieved {len(domain_context[d])} documents for {d} domain"
            )

        return domain_context

    def _retrieve_context(
        self, query: str, k: int = 5, domain: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """
        Retrieve context from the external API or fall back to vector database.

        Args:
            query: The query to search for context
            k: Number of documents to retrieve
            domain: Optional domain to filter context (shariah, finance, legal)

        Returns:
            List of context documents
        """
        try:
            # Try to fetch from external API first
            if domain:
                return self._fetch_from_api(query, domain, k)

            # Fall back to vector DB retrieval if no domain specified
            return self._fetch_from_vector_db(query, k)
        except Exception as e:
            self.logger.error(f"Error retrieving context: {e}")
            # Final fallback - return empty list if all retrieval methods fail
            return []

    def _fetch_from_api(
        self, query: str, domain: str, k: int = 5
    ) -> List[Dict[str, str]]:
        """
        Fetch context from the external API.

        Args:
            query: The query text
            domain: The domain to query for (maps to 'source' in API: shariah, finance, legal)
            k: Maximum number of results to return

        Returns:
            List of context documents
        """
        try:
            # Skip API call if requests module is not available
            if not REQUESTS_AVAILABLE:
                self.logger.warning(
                    "Requests module not available, falling back to vector DB"
                )
                return self._fetch_from_vector_db(query, k)

            # Construct API URL
            api_url = urljoin(CONTEXT_API_BASE_URL, CONTEXT_API_ENDPOINT)

            # Prepare request payload - match the API documentation format
            payload = {"question": query, "source": domain, "top_k": k}

            # Make API request
            self.logger.info(f"Requesting context from API for source: {domain}")
            response = requests.post(api_url, json=payload, timeout=API_TIMEOUT)

            # Check for successful response
            if response.status_code == 200:
                try:
                    data = response.json()

                    # Validate response structure
                    if "clauses" not in data:
                        self.logger.warning("API response missing 'clauses' field")
                        return self._fetch_from_vector_db(query, k)

                    # Transform the API response to the expected format
                    docs = []
                    for clause in data.get("clauses", []):
                        # Skip invalid entries
                        if not clause.get("text"):
                            continue

                        docs.append(
                            {
                                "text": clause.get("text", ""),
                                "metadata": {
                                    "id": clause.get("id", f"api-{domain}-{len(docs)}"),
                                    "score": float(clause.get("score", 0.0)),
                                    "domain": domain,
                                    "source": domain,
                                    "source_type": clause.get("source_type", "Unknown"),
                                },
                            }
                        )

                    self.logger.info(
                        f"Retrieved {len(docs)} documents from API for source: {domain}"
                    )

                    # If API returned no results, fall back to vector DB
                    if not docs:
                        self.logger.warning(
                            "API returned no results for source: {}".format(domain)
                        )
                        return self._fetch_from_vector_db(query, k)

                    return docs
                except ValueError as e:
                    self.logger.error(f"Failed to parse API response: {e}")
                    return self._fetch_from_vector_db(query, k)
            elif response.status_code == 429:
                self.logger.warning("API rate limit exceeded (429)")
                return self._fetch_from_vector_db(query, k)
            else:
                self.logger.warning(
                    "API request failed with status code: {}".format(
                        response.status_code
                    )
                )
                # Fall back to vector DB if API fails
                return self._fetch_from_vector_db(query, k)

        except requests.exceptions.Timeout:
            self.logger.warning(
                "API request timed out after {} seconds".format(API_TIMEOUT)
            )
            return self._fetch_from_vector_db(query, k)
        except requests.exceptions.ConnectionError:
            self.logger.warning("API connection error - check network or API endpoint")
            return self._fetch_from_vector_db(query, k)
        except Exception as e:
            self.logger.error(f"Error fetching from API: {e}")
            # Fall back to vector DB if API call fails
            return self._fetch_from_vector_db(query, k)

    def _fetch_from_vector_db(self, query: str, k: int = 5) -> List[Dict[str, str]]:
        """Retrieve context from the vector database as fallback."""
        self.logger.info("Falling back to vector database retrieval")
        # Retrieve relevant documents
        nodes = retriever.retrieve(query)

        # Convert nodes to dictionary format
        docs = []
        for node in nodes:
            if hasattr(node, "metadata"):
                docs.append({"text": node.text, "metadata": node.metadata})
            else:
                docs.append({"text": node.text, "metadata": {}})

        return docs

    def _filter_for_domain(
        self, docs: List[Dict[str, str]], domain: str
    ) -> List[Dict[str, str]]:
        """
        Filter context documents for a specific domain.
        Note: This is kept for backward compatibility with existing code.
        New code should use the API-based retrieval with domain parameter.
        """
        # Simple keyword-based filtering as fallback
        domain_keywords = {
            "shariah": [
                "shariah",
                "islamic",
                "halal",
                "quran",
                "sunnah",
                "hadith",
                "fiqh",
                "fatwa",
            ],
            "finance": [
                "accounting",
                "finance",
                "calculation",
                "balance",
                "assets",
                "liabilities",
                "profit",
                "loss",
            ],
            "legal": [
                "legal",
                "regulation",
                "compliance",
                "standard",
                "requirement",
                "document",
                "contract",
            ],
        }

        # Get keywords for the specified domain
        keywords = domain_keywords.get(domain, [])

        # Filter documents that match domain keywords
        filtered_docs = []
        for doc in docs:
            text = doc.get("text", "").lower()
            if any(keyword in text for keyword in keywords):
                filtered_docs.append(doc)

        # If no matches, return a subset of general docs
        if not filtered_docs and docs:
            return docs[:3]

        return filtered_docs


def retrieve_evaluation_context(
    prompt: str, response: str, k: int = 5
) -> List[Dict[str, str]]:
    """
    Legacy function to retrieve relevant context from the vector database for evaluation.

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

    try:
        # Skip API call if requests module is not available
        if not REQUESTS_AVAILABLE:
            logger.warning("Requests module not available, falling back to vector DB")
            raise ImportError("Requests module not available")

        # Try to use the API-based context retriever first
        api_url = urljoin(CONTEXT_API_BASE_URL, CONTEXT_API_ENDPOINT)

        # Prepare request payload using all sources for general context
        # Use finance as default since it likely contains most evaluation standards
        payload = {
            "question": combined_query,
            "source": "finance",  # Default to finance for general evaluation
            "top_k": k,
        }

        # Make API request
        logger.info("Requesting context from API for general evaluation")
        response = requests.post(api_url, json=payload, timeout=API_TIMEOUT)

        if response.status_code == 200:
            data = response.json()

            # Transform the API response to the expected format
            docs = []
            for clause in data.get("clauses", []):
                docs.append(
                    {
                        "text": clause.get("text", ""),
                        "metadata": {
                            "id": clause.get("id", ""),
                            "score": clause.get("score", 0.0),
                            "source_type": clause.get("source_type", "Unknown"),
                        },
                    }
                )

            logger.info(f"Retrieved {len(docs)} documents from API")
            return docs

    except Exception as e:
        logger.error(f"Error fetching from API: {e}")
        # Fall back to original retrieval method

    # Fallback: Use the existing retriever
    logger.info("Falling back to vector database retrieval")
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

    try:
        # Skip API call if requests module is not available
        if not REQUESTS_AVAILABLE:
            logger.warning("Requests module not available, falling back to vector DB")
            raise ImportError("Requests module not available")

        # Try to use the API-based context retriever first
        api_url = urljoin(CONTEXT_API_BASE_URL, CONTEXT_API_ENDPOINT)

        # Prepare request payload (using 'finance' source as standards are typically finance documents)
        payload = {
            "question": query,
            "source": "finance",  # Financial standards are in the finance domain
            "top_k": k,
            "standard_id": standard_id,  # Pass standard ID as additional parameter
        }

        # Make API request
        logger.info(f"Requesting context from API for standard: {standard_id}")
        response = requests.post(api_url, json=payload, timeout=API_TIMEOUT)

        if response.status_code == 200:
            data = response.json()

            # Transform the API response to the expected format
            docs = []
            for clause in data.get("clauses", []):
                docs.append(
                    {
                        "text": clause.get("text", ""),
                        "metadata": {
                            "id": clause.get("id", ""),
                            "score": clause.get("score", 0.0),
                            "standard_id": standard_id,
                            "source_type": clause.get("source_type", "Standard"),
                        },
                    }
                )

            logger.info(
                f"Retrieved {len(docs)} documents from API for standard: {standard_id}"
            )
            return docs

    except Exception as e:
        logger.error(f"Error fetching from API for standard {standard_id}: {e}")
        # Fall back to original retrieval method

    # Fallback: Use the existing retriever
    logger.info(
        f"Falling back to vector database retrieval for standard: {standard_id}"
    )
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


# Initialize context retriever instance for use by other modules
context_retriever = ContextRetriever()
