from langchain_core.messages import SystemMessage, HumanMessage
from typing import Dict, Any
from components.agents.base_agent import Agent
from components.agents.prompts import KNOWLEDGE_INTEGRATION_SYSTEM_PROMPT
import json

class KnowledgeIntegrationAgent(Agent):
    """Agent responsible for integrating transaction analysis with standards knowledge."""

    def __init__(self):
        super().__init__(system_prompt=KNOWLEDGE_INTEGRATION_SYSTEM_PROMPT)

    def integrate_knowledge(
        self, transaction_analysis: Dict[str, Any], standard_rationales: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Integrate transaction analysis with standards knowledge.

        Args:
            transaction_analysis: Output from TransactionAnalyzerAgent
            standard_rationales: Dict mapping standard IDs to rationales

        Returns:
            Dict containing integrated analysis
        """
        # Format the transaction analysis
        transaction_str = json.dumps(
            transaction_analysis["transaction_details"], indent=2
        )
        analysis_str = transaction_analysis["analysis"]

        # Format the standard rationales
        rationales_str = ""
        for std_id, rationale in standard_rationales.items():
            rationales_str += f"\n\n--- {std_id} RATIONALE ---\n{rationale}"

        # Prepare message for knowledge integration
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(
                content=f"""Please integrate this transaction analysis with standards knowledge:
            
Transaction:
{transaction_str}

Transaction Analysis:
{analysis_str}

Standard Rationales:
{rationales_str}

Provide an integrated analysis that:
1. Resolves conflicts between standards
2. Prioritizes the most applicable standard(s)
3. Provides a comprehensive accounting treatment
4. Explains how the transaction should be recorded according to AAOIFI standards
5. Highlights any special considerations for this type of transaction
            """
            ),
        ]

        # Get response from the model
        response = self.llm.invoke(messages)

        return {
            "transaction_analysis": transaction_analysis,
            "standard_rationales": standard_rationales,
            "integrated_analysis": response.content,
        }

# Initialize the agent
knowledge_integration = KnowledgeIntegrationAgent()