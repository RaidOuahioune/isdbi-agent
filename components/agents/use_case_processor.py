from langchain_core.messages import SystemMessage, HumanMessage
from typing import Dict, Any, Optional
from components.agents.base_agent import Agent
from components.agents.prompts import USE_CASE_PROCESSOR_SYSTEM_PROMPT
from retreiver import retriever

class UseCaseProcessorAgent(Agent):
    """Agent responsible for processing financial use cases and providing accounting guidance."""

    def __init__(self):
        super().__init__(system_prompt=USE_CASE_PROCESSOR_SYSTEM_PROMPT)

    def process_use_case(
        self, scenario: str, standards_info: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Process a financial scenario and provide accounting guidance."""
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
{standards_context}

Additional Context:
{additional_context}

Provide:
1. The Islamic financial product type
2. The applicable AAOIFI standard(s)
3. Step-by-step calculation methodology
4. Journal entries with explanations
5. References to specific sections of the standards
            """
            ),
        ]

        # Get processing result
        response = self.llm.invoke(messages)

        return {"scenario": scenario, "accounting_guidance": response.content}

# Initialize the agent
use_case_processor = UseCaseProcessorAgent()