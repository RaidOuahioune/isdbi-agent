from langchain_core.messages import SystemMessage, HumanMessage
from typing import Dict, Any
from components.agents.base_agent import Agent
from components.agents.prompts import STANDARDS_EXTRACTOR_SYSTEM_PROMPT
from retreiver import retriever

class StandardsExtractorAgent(Agent):
    """Agent responsible for extracting information from AAOIFI standards."""

    def __init__(self):
        super().__init__(system_prompt=STANDARDS_EXTRACTOR_SYSTEM_PROMPT)

    def extract_standard_info(self, standard_id: str, query: str) -> Dict[str, Any]:
        """Extract specific information from standards based on query."""
        # Use retriever to get relevant chunks from standards
        retrieval_query = f"Standard {standard_id}: {query}"
        retrieved_nodes = retriever.retrieve(retrieval_query)

        # Extract text content from retrieved nodes
        context = "\n\n".join([node.text for node in retrieved_nodes])

        # Prepare message for extraction
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(
                content=f"""Please extract relevant information from AAOIFI standard {standard_id} based on this query:
            
Query: {query}

Context from standards:
{context}

Return a structured response with key elements, requirements, and guidelines.
            """
            ),
        ]

        # Get extraction result
        response = self.llm.invoke(messages)

        return {
            "standard_id": standard_id,
            "query": query,
            "extracted_info": response.content,
        }

# Initialize the agent
standards_extractor = StandardsExtractorAgent()