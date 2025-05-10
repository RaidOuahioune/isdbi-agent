from langchain_core.messages import SystemMessage, HumanMessage
from typing import Dict, Any, Optional
from components.agents.base_agent import Agent
from components.agents.prompts import USE_CASE_VERIFIER_SYSTEM_PROMPT
from retreiver import retriever
from tools.index import extract_financial_amounts, identify_transaction_type

class UseCaseVerifierAgent(Agent):
    """Agent responsible for verifying financial use cases processing and enhancing accounting guidance."""

    def __init__(self):
        super().__init__(system_prompt=USE_CASE_VERIFIER_SYSTEM_PROMPT)

    def verify_use_case(
        self, scenario: str, llm_output: str = ""
    ) -> Dict[str, Any]:
        """Verify a financial scenario processing and enhance accounting guidance with missing calculations."""
        # Identify the transaction type to get context-specific calculation formulas
        transaction_info = identify_transaction_type(scenario)
        
        # Extract all financial amounts from the scenario
        extracted_amounts = extract_financial_amounts(scenario)
        
        # Get additional context from the retriever
        retrieved_nodes = retriever.retrieve(scenario)
        additional_context = "\n\n".join([node.text for node in retrieved_nodes])

        # Prepare message for verification
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(
                content=f"""Please verify and enhance the accounting guidance for this financial scenario:
            
Scenario:
{scenario}

LLM Output:
{llm_output}

Transaction Information:
{transaction_info}

Extracted Financial Amounts:
{extracted_amounts}

Additional Context:
{additional_context}

Focus on identifying any missing calculations or amounts that were not properly addressed in the LLM output.
"""
            ),
        ]

        # Get verification result
        response = self.llm.invoke(messages)

        return {
            "scenario": scenario, 
            "original_guidance": llm_output,
            "verified_guidance": response.content
        }

# Initialize the agent
use_case_verifier = UseCaseVerifierAgent()