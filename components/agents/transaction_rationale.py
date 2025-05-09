# filepath: c:\Users\ELITE COMPUTER\Desktop\Hackaton\isdbi\isdbi-agent\components\agents\transaction_rationale.py
from langchain_core.messages import SystemMessage, HumanMessage
from typing import Dict, Any, Union
from components.agents.base_agent import Agent
from components.agents.prompts import TRANSACTION_RATIONALE_SYSTEM_PROMPT
from retreiver import retriever
import logging

class TransactionStandardRationaleAgent(Agent):
    """Agent responsible for explaining why a specific standard applies to a transaction."""

    def __init__(self):
        super().__init__(system_prompt=TRANSACTION_RATIONALE_SYSTEM_PROMPT)
        
    def explain_standard_application(
        self, transaction_input: Union[str, Dict[str, Any]], standard_id: str
    ) -> Dict[str, Any]:
        """
        Explain why a specific standard applies to a transaction.
        
        Args:
            transaction_input: Either a string describing the transaction or a Dict
                          containing transaction details
            standard_id: The ID of the standard to explain (e.g., "FAS 4")
            
        Returns:
            Dict containing rationale explanation
        """
        # Handle string input vs. dictionary input
        if isinstance(transaction_input, str):
            transaction_details = {"context": transaction_input}
            transaction_query = transaction_input
        else:
            # Format transaction details by leveraging the TransactionAnalyzerAgent method
            transaction_details = transaction_input
            from components.agents.transaction_analyzer import transaction_analyzer
            transaction_query = transaction_analyzer._build_structured_query(
                transaction_details
            )

        # Get specific information about the standard
        standard_query = f"Detailed information about {standard_id} including scope, recognition criteria, and measurement requirements"
        retrieved_nodes = retriever.retrieve(standard_query)

        # Log retrieved chunks
        logging.info(
            f"RationaleAgent: Retrieved {len(retrieved_nodes)} chunks for standard {standard_id}"
        )
        for i, node in enumerate(retrieved_nodes[:2]):
            logging.info(f"Standard chunk {i + 1}: {node.text[:100]}...")

        standard_info = "\n\n".join([node.text for node in retrieved_nodes])

        # Prepare message for rationale explanation
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(
                content=f"""Please explain in detail why {standard_id} applies to this transaction:
            
Transaction:
{transaction_query}

Standard Information:
{standard_info}

Provide a comprehensive explanation addressing:
1. Transaction Analysis: Identify key elements of the transaction related to {standard_id}
2. Standard Requirements: Outline the specific requirements of {standard_id} that apply
3. Matching Rationale: Explain how transaction elements match standard requirements
4. Evidence-Based Reasoning: Cite specific clauses of {standard_id} supporting this application
5. Confidence Level: Assess how confident you are that this standard applies (high/medium/low)
            """
            ),
        ]

        # Get response from the model
        response = self.llm.invoke(messages)

        return {
            "standard_id": standard_id,
            "transaction_details": transaction_details,
            "rationale": response.content,
        }

# Initialize the agent
transaction_rationale = TransactionStandardRationaleAgent()
