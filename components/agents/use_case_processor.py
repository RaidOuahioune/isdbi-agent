from langchain_core.messages import SystemMessage, HumanMessage
from typing import Dict, Any, Optional
from components.agents.base_agent import Agent
from components.agents.prompts import USE_CASE_PROCESSOR_SYSTEM_PROMPT
from components.agents.use_case_verifier import use_case_verifier
from retreiver import retriever


class UseCaseProcessorAgent(Agent):
    """Agent responsible for processing financial use cases and providing accounting guidance."""

    def __init__(self):
        super().__init__(system_prompt=USE_CASE_PROCESSOR_SYSTEM_PROMPT)

    def process_use_case(
        self, scenario: str, standards_info: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Process a financial scenario and provide accounting guidance with verification."""
        # If we have standards info, include it as context
        standards_context = ""
        if standards_info:
            standards_context = (
                f"\nRelevant Standards Information:\n{standards_info['extracted_info']}"
            )

        # Use retriever to get additional relevant information
        retrieved_nodes = retriever.retrieve(scenario)
        additional_context = "\n\n".join([node.text for node in retrieved_nodes])

        # Prepare message for use case processing
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(
                content=f"""Please analyze this financial scenario and provide accounting guidance:
            
Scenario:
{scenario}

Additional Context:
{additional_context}
{standards_context}
            """
            ),
        ]

        # Get initial processing result
        initial_response = self.llm.invoke(messages)
        initial_guidance = initial_response.content

        # Pass the initial output to the verifier for validation and enhancement
        verified_result = use_case_verifier.verify_use_case(
            scenario=scenario, llm_output=initial_guidance
        )

        # Return the combined result
        return {
            "scenario": scenario,
            "accounting_guidance": verified_result["verified_guidance"],
        }


# Initialize the agent
use_case_processor = UseCaseProcessorAgent()
