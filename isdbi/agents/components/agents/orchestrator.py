from langchain_core.messages import SystemMessage, HumanMessage
from components.agents.base_agent import Agent
from components.agents.prompts import ORCHESTRATOR_SYSTEM_PROMPT

class OrchestratorAgent(Agent):
    """Agent responsible for coordinating other agents."""

    def __init__(self):
        super().__init__(system_prompt=ORCHESTRATOR_SYSTEM_PROMPT)

    def route_query(self, query: str) -> str:
        """Determine which agent should handle a given query."""
        # Prepare message for routing decision
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(
                content=f"""Please analyze this query and determine which specialized agent should handle it:
            
Query: {query}

Return just the name of the agent without explanation: 
- UseCase (for financial scenarios that need accounting guidance)
- Standards (for extracting information from standards)
- Both (if both agents are needed)
- Enhancement (for standards enhancement scenarios)
            """
            ),
        ]

        # Get routing decision
        response = self.llm.invoke(messages)
        return response.content.strip()

# Initialize the agent
orchestrator = OrchestratorAgent()