from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import List, Dict, Any, Optional
import os
from dotenv import load_dotenv

from retreiver import retriever
from state import State
from tools.index import tools
from shariah_principles import format_principles_for_validation

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
For standards enhancement scenarios, route to the Standards Enhancement workflow.

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

# Define new system prompts for standards enhancement agents
REVIEWER_SYSTEM_PROMPT = """You are the Standards Reviewer Agent for an Islamic Finance standards system. Your role is to:
1. Parse and extract key elements from AAOIFI standards
2. Identify potential ambiguities, gaps, or inconsistencies in standards
3. Analyze the standard in the context of specific trigger scenarios
4. Extract sections that may need enhancement

Given a standard ID and a trigger scenario, you will retrieve and analyze the relevant standard sections that may need enhancement.
You should identify specific clauses, definitions, or guidelines that could be improved in light of the trigger scenario.

Focus on the 5 selected standards: FAS 4, 7, 10, 28, and 32.

Return detailed findings including:
- The specific section/clause of the standard being analyzed
- The potential gap or ambiguity identified
- Why this might be an issue in the context of the trigger scenario
"""

PROPOSER_SYSTEM_PROMPT = """You are the Standards Enhancement Proposer Agent for an Islamic Finance standards system. Your role is to:
1. Generate improvement ideas for AAOIFI standards
2. Draft specific text changes to standards
3. Provide clear rationale for each proposed change
4. Ensure proposed changes address identified issues while maintaining compatibility

Based on the reviewer's findings, propose specific enhancements to the standard text.
Your proposals should:
- Address the identified gap or ambiguity
- Be clearly worded and concise
- Maintain the style and terminology of the original standard
- Include rationale for each change

Focus on practical enhancements that address ambiguities, modernize standards, or improve clarity.
Return both the original text and your proposed modified text with clear explanations.
"""

VALIDATOR_SYSTEM_PROMPT = """You are the Standards Validator Agent for an Islamic Finance standards system. Your role is to:
1. Evaluate proposed changes against Shariah principles
2. Check compliance with core Islamic finance concepts
3. Verify internal consistency within the standard
4. Ensure proposed changes are practical and implementable
5. Provide clear reasoning for approval or rejection

Given a proposed enhancement to an AAOIFI standard, evaluate whether it:
- Complies with core Shariah principles (no Riba, Gharar, or Maysir)
- Maintains consistency with the rest of the standard
- Maintains alignment with other related standards
- Provides practical guidance that can be implemented

For each validation check, provide specific reasoning with references to Shariah principles or other aspects of the standard.
Clearly indicate whether the proposal is APPROVED, REJECTED, or NEEDS REVISION with detailed feedback.
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


class ReviewerAgent(Agent):
    """Agent responsible for reviewing standards and identifying areas for enhancement."""
    
    def __init__(self):
        super().__init__(system_prompt=REVIEWER_SYSTEM_PROMPT)
    
    def extract_standard_elements(self, standard_id: str, trigger_scenario: str) -> Dict[str, Any]:
        """
        Extract key elements and identify areas for enhancement.
        
        Args:
            standard_id: The ID of the standard (e.g., "10" for FAS 10)
            trigger_scenario: The scenario that triggers the need for enhancement
            
        Returns:
            Dict with analysis results
        """
        # Use retriever to get relevant chunks from standards
        retrieval_query = f"Standard FAS {standard_id} elements that might need enhancement regarding: {trigger_scenario}"
        retrieved_nodes = retriever.retrieve(retrieval_query)
        
        # Extract text content from retrieved nodes
        context = "\n\n".join([node.text for node in retrieved_nodes])
        
        # Prepare message for analysis
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=f"""Please review AAOIFI FAS {standard_id} and identify elements that might need enhancement:
            
Trigger Scenario:
{trigger_scenario}

Relevant Sections from FAS {standard_id}:
{context}

Provide a detailed analysis of sections that might need enhancement, including:
1. Specific clauses or definitions that lack clarity or could be improved
2. Areas where the standard might not fully address the trigger scenario
3. Specific text that could be ambiguous when applied to this scenario
4. Potential inconsistencies within the standard or with other standards
            """)
        ]
        
        # Get analysis result
        response = self.llm.invoke(messages)
        
        return {
            "standard_id": standard_id,
            "trigger_scenario": trigger_scenario,
            "review_content": context, 
            "review_analysis": response.content
        }


class ProposerAgent(Agent):
    """Agent responsible for proposing enhancements to standards."""
    
    def __init__(self):
        super().__init__(system_prompt=PROPOSER_SYSTEM_PROMPT)
    
    def generate_enhancement_proposal(self, review_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate proposed enhancements based on reviewer findings.
        
        Args:
            review_result: The dictionary returned by ReviewerAgent.extract_standard_elements()
            
        Returns:
            Dict with the proposal details
        """
        # Extract necessary information from review results
        standard_id = review_result["standard_id"]
        trigger_scenario = review_result["trigger_scenario"]
        review_content = review_result["review_content"]
        review_analysis = review_result["review_analysis"]
        
        # Prepare message for generating proposals
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=f"""Please propose enhancements to AAOIFI FAS {standard_id} based on this review:
            
Trigger Scenario:
{trigger_scenario}

Relevant Standard Content:
{review_content}

Reviewer Analysis:
{review_analysis}

Provide specific enhancement proposals including:
1. The original text of sections needing enhancement
2. Your proposed modified text
3. Clear rationale for each proposed change
4. How the change addresses the trigger scenario
            """)
        ]
        
        # Get proposal result
        response = self.llm.invoke(messages)
        
        return {
            "standard_id": standard_id,
            "trigger_scenario": trigger_scenario,
            "review_analysis": review_analysis,
            "enhancement_proposal": response.content
        }


class ValidatorAgent(Agent):
    """Agent responsible for validating proposed changes."""
    
    def __init__(self):
        super().__init__(system_prompt=VALIDATOR_SYSTEM_PROMPT)
    
    def validate_proposal(self, proposal: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate the proposed enhancements.
        
        Args:
            proposal: The dictionary returned by ProposerAgent.generate_enhancement_proposal()
            
        Returns:
            Dict with validation results
        """
        # Extract necessary information from proposal
        standard_id = proposal["standard_id"]
        trigger_scenario = proposal["trigger_scenario"]
        enhancement_proposal = proposal["enhancement_proposal"]
        
        # Get formatted principles for this standard
        shariah_principles = format_principles_for_validation(standard_id)
        
        # Use retriever to get related standards information
        related_query = f"Related standards to FAS {standard_id} and consistency considerations"
        related_nodes = retriever.retrieve(related_query)
        related_standards = "\n\n".join([node.text for node in related_nodes])
        
        # Prepare message for validation
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=f"""Please validate this proposed enhancement to AAOIFI FAS {standard_id}:
            
Trigger Scenario:
{trigger_scenario}

Proposed Enhancement:
{enhancement_proposal}

Shariah Principles to Consider:
{shariah_principles}

Related Standards Context:
{related_standards}

Validate the proposal and provide:
1. Shariah Compliance Assessment: Does it comply with core Islamic principles?
2. Consistency Check: Is it consistent with the rest of FAS {standard_id} and other standards?
3. Practical Implementation Assessment: Can it be practically implemented?
4. Final Decision: APPROVED, REJECTED, or NEEDS REVISION with detailed reasoning
            """)
        ]
        
        # Get validation result
        response = self.llm.invoke(messages)
        
        return {
            "standard_id": standard_id,
            "trigger_scenario": trigger_scenario,
            "enhancement_proposal": enhancement_proposal,
            "validation_result": response.content
        }

# Initialize agents
orchestrator = OrchestratorAgent()
standards_extractor = StandardsExtractorAgent()
use_case_processor = UseCaseProcessorAgent()
reviewer_agent = ReviewerAgent()
proposer_agent = ProposerAgent()
validator_agent = ValidatorAgent()