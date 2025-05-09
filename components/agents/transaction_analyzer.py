from langchain_core.messages import SystemMessage, HumanMessage
from typing import Dict, Any, List, Union
from components.agents.base_agent import Agent
from components.agents.prompts import TRANSACTION_ANALYZER_SYSTEM_PROMPT
from retreiver import retriever
import re
import logging


class TransactionAnalyzerAgent(Agent):
    """Agent responsible for analyzing journal entries to identify applicable AAOIFI standards."""

    def __init__(self):
        super().__init__(system_prompt=TRANSACTION_ANALYZER_SYSTEM_PROMPT)
        self.retriever = retriever  # Make retriever accessible as a class attribute

    def analyze_transaction(
        self, transaction_input: Union[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze a transaction to identify applicable AAOIFI standards.

        Args:
            transaction_input: Either a string describing the transaction or a Dict
                              containing transaction context, journal entries, and additional info

        Returns:
            Dict containing analysis results
        """
        # Handle string input
        if isinstance(transaction_input, str):
            transaction_details = {"context": transaction_input}
            query = transaction_input
        else:
            # Handle structured dictionary input (backward compatibility)
            transaction_details = transaction_input
            query = self._build_structured_query(transaction_details)

        # Use retriever to get relevant standards information
        retrieved_nodes = self.retriever.retrieve(query)
        standards_context = "\n\n".join([node.text for node in retrieved_nodes])

        # Log chunk information
        logging.info(f"TransactionAnalyzer retrieved {len(retrieved_nodes)} chunks")

        # Prepare message for transaction analysis
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(
                content=f"""Please analyze this financial transaction and identify applicable AAOIFI standards:
            
Transaction Details:
{query}

Standards Context:
{standards_context}

Provide your analysis with:
1. Transaction Summary: Brief description of what this transaction represents
2. Applicable Standards: Ranked by probability with percentages
3. Detailed Reasoning: For each standard, explain why it applies to this transaction
            """
            ),
        ]

        # Get response from the model
        response = self.llm.invoke(messages)

        # Extract standards mentioned in the response
        standards = self._extract_standards(response.content)

        return {
            "transaction_details": transaction_details,
            "analysis": response.content,
            "identified_standards": standards,
            "retrieval_stats": {
                "chunk_count": len(retrieved_nodes),
                "chunks_summary": [
                    node.text[:100] + "..." for node in retrieved_nodes[:5]
                ],
            },
        }

    def _build_structured_query(self, transaction_details: Dict[str, Any]) -> str:
        """Build a structured query string from transaction details."""
        # Extract context
        context = ""
        if "context" in transaction_details:
            context += f"Context: {transaction_details['context']}\n"

        # Extract journal entries
        journal_entries = ""
        if "journal_entries" in transaction_details:
            journal_entries = "Journal Entries:\n"
            for entry in transaction_details["journal_entries"]:
                journal_entries += f"Dr. {entry['debit_account']} ${entry['amount']}\n"
                journal_entries += (
                    f" Cr. {entry['credit_account']} ${entry['amount']}\n"
                )

        # Extract additional information
        additional_info = ""
        if "additional_info" in transaction_details:
            additional_info = "Additional Information:\n"
            for key, value in transaction_details["additional_info"].items():
                additional_info += f"{key}: {value}\n"

        return f"{context}\n{journal_entries}\n{additional_info}"

    def _extract_standards(self, text: str) -> List[str]:
        """Extract standards mentioned in the text."""
        # Find all mentions of FAS followed by numbers
        standards = re.findall(r"FAS\s+\d+", text)
        return list(set(standards))


# Initialize the agent
transaction_analyzer = TransactionAnalyzerAgent()
