from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import List, Dict, Any, Optional
import os
from dotenv import load_dotenv

from retreiver import retriever
from state import State
from tools.index import tools

# Load environment variables
load_dotenv()

# Base LLM setup
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-preview-04-17",
    api_key=os.environ["GEMINI_API_KEY"],
)

# Define agent system prompts
ORCHESTRATOR_SYSTEM_PROMPT = """You are the Orchestrator Agent for an Islamic Finance standards system. Your role is to:
1. Act as the central coordinator for all agent interactions
2. Route user queries to appropriate specialized agents
3. Manage the conversation flow and agent collaboration
4. Consolidate outputs from multiple agents into coherent responses

You will receive user queries related to Islamic Finance standards and determine which specialized agents are needed to address the query.
For use case scenarios, route to the Use Case Processor Agent.
For extracting information from standards, route to the Standards Extractor Agent.

Return your analysis of the query and which agent(s) should handle it.
"""

STANDARDS_EXTRACTOR_SYSTEM_PROMPT = """You are the Standards Extractor Agent for an Islamic Finance standards system. Your role is to:
1. Parse and extract key elements from AAOIFI standards
2. Create structured representations of standards for the knowledge base
3. Identify relationships between different standards
4. Tag standards with relevant metadata for efficient retrieval

Given a request related to AAOIFI Financial Accounting Standards (FAS), you will retrieve and analyze the relevant standards information.
Focus on the 5 selected standards: FAS 4, 7, 10, 28, and 32.

Return detailed information extracted from the standards in a structured format.
"""

USE_CASE_PROCESSOR_SYSTEM_PROMPT = """You are the Use Case Processor Agent for an Islamic Finance standards system. Your role is to:
1. Analyze practical financial scenarios
2. Determine which standards apply to specific use cases
3. Provide step-by-step accounting guidance
4. Generate appropriate journal entries and explanations

When presented with a financial scenario, analyze it to identify the applicable AAOIFI standards, then provide detailed accounting guidance including:
- The identification of the Islamic financial product type
- The applicable AAOIFI standard(s)
- Step-by-step calculation methodology
- Journal entries with explanations
- References to specific sections of the standards that apply

Focus on the 5 selected standards: FAS 4, 7, 10, 28, and 32.
"""

class Agent:
    """Base Agent class that all specialized agents will inherit from."""
    
    def __init__(self, system_prompt: str, tools: Optional[List] = None):
        self.system_prompt = system_prompt
        self.memory = []
        
        # Set up LLM with or without tools
        if tools:
            self.llm = llm.bind_tools(tools)
        else:
            self.llm = llm
    
    def __call__(self, state: State) -> Dict[str, Any]:
        """Process the current state and return a response."""
        # Create a copy of the messages list
        messages = state["messages"].copy()
        
        # Insert the system message if it doesn't exist
        if not messages or not (hasattr(messages[0], "type") and messages[0].type == "system"):
            messages.insert(0, SystemMessage(content=self.system_prompt))
        
        # Process with model and return response
        response = self.llm.invoke(messages)
        return {"messages": [response]}
    
    def add_to_memory(self, message):
        """Add a message to agent's memory."""
        self.memory.append(message)


class OrchestratorAgent(Agent):
    """Agent responsible for coordinating other agents."""
    
    def __init__(self):
        super().__init__(system_prompt=ORCHESTRATOR_SYSTEM_PROMPT)
    
    def route_query(self, query: str) -> str:
        """Determine which agent should handle a given query."""
        # Prepare message for routing decision
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=f"""Please analyze this query and determine which specialized agent should handle it:
            
Query: {query}

Return just the name of the agent without explanation: 
- UseCase (for financial scenarios that need accounting guidance)
- Standards (for extracting information from standards)
- Both (if both agents are needed)
            """)
        ]
        
        # Get routing decision
        response = self.llm.invoke(messages)
        return response.content.strip()


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
            HumanMessage(content=f"""Please extract relevant information from AAOIFI standard {standard_id} based on this query:
            
Query: {query}

Context from standards:
{context}

Return a structured response with key elements, requirements, and guidelines.
            """)
        ]
        
        # Get extraction result
        response = self.llm.invoke(messages)
        
        return {
            "standard_id": standard_id,
            "query": query,
            "extracted_info": response.content
        }


class UseCaseProcessorAgent(Agent):
    """Agent responsible for processing financial use cases and providing accounting guidance."""
    
    def __init__(self):
        super().__init__(system_prompt=USE_CASE_PROCESSOR_SYSTEM_PROMPT)
    
    def process_use_case(self, scenario: str, standards_info: Optional[Dict] = None) -> Dict[str, Any]:
        """Process a financial scenario and provide accounting guidance."""
        # If we have standards info, include it as context
        standards_context = ""
        if standards_info:
            standards_context = f"\nRelevant Standards Information:\n{standards_info['extracted_info']}"
        
        # Use retriever to get additional relevant information
        retrieved_nodes = retriever.retrieve(scenario)
        additional_context = "\n\n".join([node.text for node in retrieved_nodes])
        
        # Prepare message for use case processing
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=f"""Please analyze this financial scenario and provide accounting guidance:
            
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
            """)
        ]
        
        # Get processing result
        response = self.llm.invoke(messages)
        
        return {
            "scenario": scenario,
            "accounting_guidance": response.content
        }

# Initialize agents
orchestrator = OrchestratorAgent()
standards_extractor = StandardsExtractorAgent()
use_case_processor = UseCaseProcessorAgent()