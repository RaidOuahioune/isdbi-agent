from typing import Dict, Any, List
from .base_agent import Agent
from langchain_core.messages import SystemMessage, HumanMessage
import logging

class ExpertAgent(Agent):
    """Base class for expert agents"""
    def __init__(self, domain: str, expertise: str):
        super().__init__(system_prompt=f"""You are an {expertise} expert. Be extremely concise.
Focus only on critical issues and give brief, actionable feedback.
Limit analysis to 2-3 sentences.
List maximum 2 key concerns.
List maximum 2 key recommendations.""")
        self.domain = domain
        self.expertise = expertise
    
    def analyze_proposal(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze proposed enhancement from expert's domain perspective"""
        try:
            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=f"""Analyze this proposal from {self.domain} perspective.
                
                Proposal:
                {context["proposal"]}
                
                Previous Discussion:
                {self._format_previous_discussion(context.get("previous_discussion", []))}
                
                Provide your analysis in this format:
                ANALYSIS:
                (your detailed analysis)
                
                CONCERNS:
                1. (first concern)
                2. (second concern)
                ...
                
                RECOMMENDATIONS:
                1. (first recommendation)
                2. (second recommendation)
                ...""")
            ]
            
            response = self._invoke_with_retry(messages)
            
            # Parse the structured response
            sections = self._parse_structured_response(response.content)
            
            return {
                "domain": self.domain,
                "analysis": {"text": sections.get("ANALYSIS", "")},
                "concerns": [{"type": self.domain, "description": c} for c in sections.get("CONCERNS", [])],
                "recommendations": [{"type": self.domain, "description": r} for r in sections.get("RECOMMENDATIONS", [])]
            }
            
        except Exception as e:
            logging.error(f"Error in {self.domain} expert analysis: {str(e)}")
            return {
                "domain": self.domain,
                "analysis": {"text": "Analysis temporarily unavailable due to rate limits"},
                "concerns": [],
                "recommendations": []
            }

    def _parse_structured_response(self, text: str) -> Dict[str, Any]:
        """Parse a structured response into sections"""
        sections = {}
        current_section = None
        current_items = []
        
        for line in text.split('\n'):
            line = line.strip()
            if not line:
                continue
                
            if line.endswith(':') and line.isupper():
                if current_section and current_items:
                    sections[current_section] = '\n'.join(current_items) if current_section == "ANALYSIS" else current_items
                    current_items = []
                current_section = line[:-1]
            elif current_section:
                if current_section in ["CONCERNS", "RECOMMENDATIONS"]:
                    if line[0].isdigit() and '. ' in line:
                        current_items.append(line.split('. ', 1)[1])
                else:
                    current_items.append(line)
        
        if current_section and current_items:
            sections[current_section] = '\n'.join(current_items) if current_section == "ANALYSIS" else current_items
            
        return sections

    def _evaluate_from_domain_perspective(self, proposal: str, previous_discussion: List) -> Dict:
        """Evaluate proposal from domain perspective - to be implemented by subclasses"""
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=f"""Evaluate the proposal from {self.domain} perspective:
            
            Proposal:
            {proposal}
            
            Previous Discussion:
            {self._format_previous_discussion(previous_discussion)}
            """)
        ]
        
        # Use the retry mechanism from base agent
        try:
            response = self._invoke_with_retry(messages)
            return {"text": response.content}
        except Exception as e:
            logging.warning(f"Evaluation failed for {self.domain} expert, using fallback: {str(e)}")
            return {"text": "Evaluation temporarily unavailable"}

    def _identify_concerns(self, analysis: Dict) -> List[Dict]:
        """Extract concerns from analysis"""
        if "text" not in analysis:
            return []
            
        try:
            concerns_text = self._extract_concerns_from_text(analysis["text"])
            return [{"type": self.domain, "description": concern} for concern in concerns_text]
        except Exception as e:
            logging.warning(f"Failed to identify concerns for {self.domain} expert: {str(e)}")
            return []

    def _generate_recommendations(self, analysis: Dict) -> List[Dict]:
        """Generate recommendations based on analysis"""
        if "text" not in analysis:
            return []
            
        try:
            recs_text = self._extract_recommendations_from_text(analysis["text"])
            return [{"type": self.domain, "description": rec} for rec in recs_text]
        except Exception as e:
            logging.warning(f"Failed to generate recommendations for {self.domain} expert: {str(e)}")
            return []

    def _format_previous_discussion(self, discussion: List) -> str:
        """Format previous discussion rounds for context"""
        if not discussion:
            return "No previous discussion"
        return "\n\n".join([f"Round {i+1}:\n{d}" for i, d in enumerate(discussion)])
    
    def _extract_concerns_from_text(self, text: str) -> List[str]:
        """Extract concerns from analysis text"""
        messages = [
            SystemMessage(content="Extract specific concerns from the analysis text. Return them as a numbered list."),
            HumanMessage(content=f"Extract concerns from:\n\n{text}")
        ]
        
        try:
            response = self._invoke_with_retry(messages)
            return self._parse_list_response(response.content)
        except Exception as e:
            logging.warning(f"Failed to extract concerns from text for {self.domain} expert: {str(e)}")
            return []

    def _extract_recommendations_from_text(self, text: str) -> List[str]:
        """Extract recommendations from analysis text"""
        messages = [
            SystemMessage(content="Extract specific recommendations from the analysis text. Return them as a numbered list."),
            HumanMessage(content=f"Extract recommendations from:\n\n{text}")
        ]
        
        try:
            response = self._invoke_with_retry(messages)
            return self._parse_list_response(response.content)
        except Exception as e:
            logging.warning(f"Failed to extract recommendations from text for {self.domain} expert: {str(e)}")
            return []

    def _parse_list_response(self, response: str) -> List[str]:
        """Parse a numbered list response into a list of strings"""
        items = []
        current_item = []
        
        for line in response.split('\n'):
            line = line.strip()
            if not line:
                continue
            
            if line[0].isdigit() and '. ' in line:
                if current_item:
                    items.append(' '.join(current_item))
                    current_item = []
                current_item.append(line.split('. ', 1)[1])
            else:
                current_item.append(line)
        
        if current_item:
            items.append(' '.join(current_item))
        
        return items

class ShariahExpert(ExpertAgent):
    """Shariah expert agent for Islamic finance compliance analysis"""
    def __init__(self):
        super().__init__("shariah", "Islamic finance principles and Shariah compliance")
        
    def _evaluate_from_domain_perspective(self, proposal: str, previous_discussion: List) -> Dict:
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=f"""Evaluate from Shariah compliance perspective, considering:
            1. Adherence to Islamic principles (no Riba, Gharar, Maysir)
            2. Alignment with Shariah objectives (Maqasid)
            3. Impact on contract validity
            4. Clarity of Shariah guidance
            
            Proposal:
            {proposal}
            
            Previous Discussion:
            {self._format_previous_discussion(previous_discussion)}
            """)
        ]
        
        response = self.llm.invoke(messages)
        return {"text": response.content}

class FinanceExpert(ExpertAgent):
    """Finance expert agent for accounting and reporting analysis"""
    def __init__(self):
        super().__init__("finance", "Islamic financial accounting and reporting")
        
    def _evaluate_from_domain_perspective(self, proposal: str, previous_discussion: List) -> Dict:
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=f"""Evaluate from financial accounting perspective, considering:
            1. Recognition and measurement implications
            2. Financial reporting clarity
            3. Practical accounting procedures
            4. Consistency with accounting principles
            
            Proposal:
            {proposal}
            
            Previous Discussion:
            {self._format_previous_discussion(previous_discussion)}
            """)
        ]
        
        response = self.llm.invoke(messages)
        return {"text": response.content}

class StandardsExpert(ExpertAgent):
    """Standards expert agent for AAOIFI standards analysis"""
    def __init__(self):
        super().__init__("standards", "AAOIFI standards structure and interrelationships")
        
    def _evaluate_from_domain_perspective(self, proposal: str, previous_discussion: List) -> Dict:
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=f"""Evaluate for standards consistency, considering:
            1. Alignment with existing standards
            2. Technical clarity and structure
            3. Cross-standard implications
            4. Implementation guidance
            
            Proposal:
            {proposal}
            
            Previous Discussion:
            {self._format_previous_discussion(previous_discussion)}
            """)
        ]
        
        response = self.llm.invoke(messages)
        return {"text": response.content}

class PracticalExpert(ExpertAgent):
    """Practical expert agent for implementation feasibility analysis"""
    def __init__(self):
        super().__init__("practical", "Implementation feasibility and industry practices")
        
    def _evaluate_from_domain_perspective(self, proposal: str, previous_discussion: List) -> Dict:
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=f"""Evaluate for practical implementation, considering:
            1. Operational feasibility
            2. Industry readiness
            3. Resource requirements
            4. Implementation challenges
            
            Proposal:
            {proposal}
            
            Previous Discussion:
            {self._format_previous_discussion(previous_discussion)}
            """)
        ]
        
        response = self.llm.invoke(messages)
        return {"text": response.content}

class RiskExpert(ExpertAgent):
    """Risk expert agent for risk assessment and mitigation analysis"""
    def __init__(self):
        super().__init__("risk", "Risk assessment and mitigation")
        
    def _evaluate_from_domain_perspective(self, proposal: str, previous_discussion: List) -> Dict:
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=f"""Evaluate from risk management perspective, considering:
            1. Operational risks
            2. Compliance risks
            3. Market risks
            4. Mitigation strategies
            
            Proposal:
            {proposal}
            
            Previous Discussion:
            {self._format_previous_discussion(previous_discussion)}
            """)
        ]
        
        response = self.llm.invoke(messages)
        return {"text": response.content}

# Initialize expert agents
shariah_expert = ShariahExpert()
finance_expert = FinanceExpert()
standards_expert = StandardsExpert()
practical_expert = PracticalExpert()
risk_expert = RiskExpert()