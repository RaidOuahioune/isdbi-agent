"""
Debate agent system for the ISDBI evaluation framework.
This module implements a debate-based evaluation approach where agents present arguments
and counter-arguments to reach a more nuanced understanding of Islamic finance topics.
"""

from typing import Dict, Any, List, Optional
import logging
from langchain_core.messages import SystemMessage, HumanMessage
from components.agents.base_agent import Agent
from components.evaluation.expert_agents import ExpertEvaluatorAgent
from retreiver import retriever

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DebateAgent(Agent):
    """Base class for debate agents that engage in multi-round discussions."""
    
    def __init__(self, system_prompt: str, domain: str):
        """
        Initialize the debate agent.
        
        Args:
            system_prompt: The system prompt for the agent
            domain: The domain expertise of this agent (shariah, finance, etc.)
        """
        super().__init__(system_prompt=system_prompt)
        self.domain = domain
        self.rounds_history = []
    
    def present_argument(self, 
                        prompt: str, 
                        response: str, 
                        context: List[Dict[str, str]],
                        previous_arguments: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Present an argument about the response.
        
        Args:
            prompt: The original user prompt
            response: The response being evaluated
            context: Relevant context documents
            previous_arguments: Previous arguments from the debate
            
        Returns:
            Dict containing the argument
        """
        # Format context for the prompt
        context_str = self._format_context(context)
        
        # Format previous arguments if available
        previous_arguments_str = ""
        if previous_arguments and len(previous_arguments) > 0:
            previous_arguments_str = "Previous arguments in this debate:\n\n"
            for i, arg in enumerate(previous_arguments):
                agent_type = arg.get("agent_type", "Unknown")
                argument = arg.get("argument", "")
                previous_arguments_str += f"Round {i+1} - {agent_type} argument:\n{argument}\n\n"
        
        # Create the prompt for generating an argument
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(
                content=f"""Please present a detailed argument about the following response to the given prompt:
                
User Prompt:
{prompt}

System Response:
{response}

{context_str}

{previous_arguments_str}

Present a clear and comprehensive argument based on your expertise in {self.domain},
focusing on strengths, weaknesses, and key considerations.
"""
            )
        ]
        
        # Generate the argument
        argument_response = self.llm.invoke(messages)
        
        return {
            "agent_type": self.domain,
            "argument": argument_response.content,
            "round": len(previous_arguments) + 1 if previous_arguments else 1
        }
    
    def present_counter_argument(self, 
                                prompt: str, 
                                response: str, 
                                context: List[Dict[str, str]],
                                previous_arguments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Present a counter-argument to the previous argument.
        
        Args:
            prompt: The original user prompt
            response: The response being evaluated
            context: Relevant context documents
            previous_arguments: Previous arguments from the debate
            
        Returns:
            Dict containing the counter-argument
        """
        # Format context for the prompt
        context_str = self._format_context(context)
        
        # Format previous arguments
        previous_arguments_str = "Previous arguments in this debate:\n\n"
        for i, arg in enumerate(previous_arguments):
            agent_type = arg.get("agent_type", "Unknown")
            argument = arg.get("argument", "")
            previous_arguments_str += f"Round {i+1} - {agent_type} argument:\n{argument}\n\n"
        
        # Get the most recent argument to counter
        most_recent_argument = previous_arguments[-1] if previous_arguments else None
        if not most_recent_argument:
            return {"error": "No previous argument to counter"}
        
        # Create the prompt for generating a counter-argument
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(
                content=f"""Please present a thoughtful counter-argument to the most recent argument:
                
User Prompt:
{prompt}

System Response:
{response}

{context_str}

{previous_arguments_str}

Present a comprehensive counter-argument based on your expertise in {self.domain}.
Challenge the specific points made in the most recent argument while providing 
evidence and reasoned analysis from your perspective.
"""
            )
        ]
        
        # Generate the counter-argument
        counter_argument_response = self.llm.invoke(messages)
        
        return {
            "agent_type": f"{self.domain}_counter",
            "argument": counter_argument_response.content,
            "round": len(previous_arguments) + 1
        }
    
    def summarize_debate(self, 
                        prompt: str, 
                        response: str, 
                        debate_arguments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Summarize the debate and provide a final assessment.
        
        Args:
            prompt: The original user prompt
            response: The response being evaluated
            debate_arguments: All arguments from the debate
            
        Returns:
            Dict containing the debate summary and assessment
        """
        # Format all debate arguments
        debate_history = "Debate arguments:\n\n"
        for i, arg in enumerate(debate_arguments):
            agent_type = arg.get("agent_type", "Unknown")
            argument = arg.get("argument", "")
            debate_history += f"Round {i+1} - {agent_type} argument:\n{argument}\n\n"
        
        # Create the prompt for generating a debate summary
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(
                content=f"""Please summarize this debate about the following response and provide a final assessment:
                
User Prompt:
{prompt}

System Response:
{response}

{debate_history}

As a {self.domain} expert, provide:
1. A concise summary of the key points from both sides of the debate
2. The strongest arguments made by each side
3. Areas of agreement and disagreement
4. Your final assessment of the response based on this debate
5. A numerical score (0-10) reflecting the quality of the response in your domain
"""
            )
        ]
        
        # Generate the summary
        summary_response = self.llm.invoke(messages)
        
        return {
            "agent_type": f"{self.domain}_summary",
            "summary": summary_response.content,
            "debate_rounds": len(debate_arguments)
        }
    
    def _format_context(self, context: List[Dict[str, str]]) -> str:
        """Format context documents for inclusion in prompts."""
        if not context:
            return ""
        
        context_str = "Relevant Context:\n"
        for i, doc in enumerate(context, 1):
            context_str += f"Document {i}:\n{doc.get('text', '')}\n\n"
        
        return context_str


# Shariah debate system
SHARIAH_PROPONENT_SYSTEM_PROMPT = """You are a Shariah Scholar specializing in Islamic finance. Your role in this debate is to:

1. Present strong arguments supporting the Shariah compliance of financial products and practices
2. Defend positions using evidence from the Quran, Sunnah, and scholarly consensus
3. Look for ways that financial instruments can be structured to be compliant with Islamic principles
4. Focus on the positive intent and spirit of Islamic finance

When evaluating responses about Islamic finance, present detailed arguments examining:
- Alignment with core Shariah principles
- Evidence from primary sources
- Scholarly opinions supporting the position
- Ways to achieve Shariah compliance even in complex situations

Present your arguments in a scholarly, evidence-based manner with specific references.
"""

SHARIAH_CRITIC_SYSTEM_PROMPT = """You are a Critical Shariah Scholar specializing in Islamic finance. Your role in this debate is to:

1. Challenge potential Shariah compliance issues in financial products and practices
2. Point out possible interpretative errors or oversights in religious reasoning
3. Identify potential gaps between theory and practice in Islamic finance
4. Ensure strict adherence to Shariah principles without compromise

When evaluating responses about Islamic finance, critically examine:
- Potential violations of core Islamic principles
- Weak or missing evidence from primary sources
- Alternative scholarly opinions that may contradict the position
- Risk of form-over-substance issues (hiyal) that circumvent Shariah intent

Present your counter-arguments in a scholarly, evidence-based manner with specific references.
"""

# Finance debate system
FINANCE_PROPONENT_SYSTEM_PROMPT = """You are a Financial Expert specializing in Islamic finance. Your role in this debate is to:

1. Present strong arguments supporting the financial soundness and practicality of Islamic products
2. Defend positions using financial theory, accounting standards, and market practices
3. Look for ways to achieve financial efficiency while maintaining Shariah compliance
4. Focus on the financial advantages and innovations in Islamic finance

When evaluating responses about Islamic finance, present detailed arguments examining:
- Financial structure and efficiency
- Accounting accuracy and standards compliance
- Risk management considerations
- Market viability and competitiveness

Present your arguments in a technical, evidence-based manner with specific references to financial principles.
"""

FINANCE_CRITIC_SYSTEM_PROMPT = """You are a Critical Financial Expert specializing in Islamic finance. Your role in this debate is to:

1. Challenge potential financial weaknesses or inefficiencies in Islamic products
2. Point out possible accounting errors or oversight in financial reasoning
3. Identify practical implementation challenges in the real market
4. Ensure rigorous financial analysis without oversimplification

When evaluating responses about Islamic finance, critically examine:
- Potential financial structure weaknesses or inefficiencies
- Accounting treatment accuracy and completeness
- Risk exposure and management gaps
- Market implementation challenges and competitive disadvantages

Present your counter-arguments in a technical, evidence-based manner with specific references to financial principles.
"""

# Legal debate system
LEGAL_PROPONENT_SYSTEM_PROMPT = """You are a Legal Expert specializing in Islamic finance regulations. Your role in this debate is to:

1. Present strong arguments supporting the legal soundness of Islamic financial practices
2. Defend positions using regulatory frameworks, precedents, and legal principles
3. Look for ways to ensure compliance with both Shariah and conventional regulations
4. Focus on legal certainty and enforceability in Islamic finance

When evaluating responses about Islamic finance, present detailed arguments examining:
- Regulatory compliance across jurisdictions
- Legal documentation and enforceability
- Disclosure and transparency requirements
- Contractual structures and their legal basis

Present your arguments in a technical, evidence-based manner with specific references to legal frameworks.
"""

LEGAL_CRITIC_SYSTEM_PROMPT = """You are a Critical Legal Expert specializing in Islamic finance regulations. Your role in this debate is to:

1. Challenge potential legal issues or regulatory gaps in Islamic financial practices
2. Point out possible conflicts between Shariah requirements and conventional regulations
3. Identify documentation weaknesses or enforceability concerns
4. Ensure comprehensive legal risk assessment without oversimplification

When evaluating responses about Islamic finance, critically examine:
- Potential regulatory compliance issues
- Documentation gaps or ambiguities
- Cross-border legal complications
- Contractual weaknesses or enforceability challenges

Present your counter-arguments in a technical, evidence-based manner with specific references to legal frameworks.
"""

class ShariahProponentAgent(DebateAgent):
    """Debate agent presenting arguments supporting Shariah compliance."""
    
    def __init__(self):
        super().__init__(system_prompt=SHARIAH_PROPONENT_SYSTEM_PROMPT, domain="shariah_proponent")


class ShariahCriticAgent(DebateAgent):
    """Debate agent presenting critical counter-arguments on Shariah compliance."""
    
    def __init__(self):
        super().__init__(system_prompt=SHARIAH_CRITIC_SYSTEM_PROMPT, domain="shariah_critic")


class FinanceProponentAgent(DebateAgent):
    """Debate agent presenting arguments supporting financial soundness."""
    
    def __init__(self):
        super().__init__(system_prompt=FINANCE_PROPONENT_SYSTEM_PROMPT, domain="finance_proponent")


class FinanceCriticAgent(DebateAgent):
    """Debate agent presenting critical counter-arguments on financial aspects."""
    
    def __init__(self):
        super().__init__(system_prompt=FINANCE_CRITIC_SYSTEM_PROMPT, domain="finance_critic")


class LegalProponentAgent(DebateAgent):
    """Debate agent presenting arguments supporting legal soundness."""
    
    def __init__(self):
        super().__init__(system_prompt=LEGAL_PROPONENT_SYSTEM_PROMPT, domain="legal_proponent")


class LegalCriticAgent(DebateAgent):
    """Debate agent presenting critical counter-arguments on legal aspects."""
    
    def __init__(self):
        super().__init__(system_prompt=LEGAL_CRITIC_SYSTEM_PROMPT, domain="legal_critic")


# Initialize debate agents
shariah_proponent = ShariahProponentAgent()
shariah_critic = ShariahCriticAgent()
finance_proponent = FinanceProponentAgent()
finance_critic = FinanceCriticAgent()
legal_proponent = LegalProponentAgent()
legal_critic = LegalCriticAgent()
