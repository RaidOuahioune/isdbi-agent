from typing import Dict, Any, List
from components.agents.base_agent import Agent
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from components.agents.prompts import REVIEWER_SYSTEM_PROMPT
from retreiver import retriever
from openai import AsyncOpenAI

from .expert_agents import (
    shariah_expert,
    finance_expert,
    standards_expert,
    practical_expert,
    risk_expert
)

class ReviewerAgent(Agent):
    """Agent responsible for initial analysis of standards and enhancement needs"""
    
    def __init__(self):
        super().__init__(system_prompt=REVIEWER_SYSTEM_PROMPT)
    
    async def analyze_standard(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a standard and identify enhancement needs"""
        try:
            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=f"""
Please analyze AAOIFI FAS {context['standard_id']} concerning the following scenario:

{context['trigger_scenario']}

Current Standard Text:
{context['text']}

Identify gaps, ambiguities, or areas needing enhancement in the current standard.
Provide detailed analysis of how the standard could be improved to better address this scenario.
""")
            ]
            
            response = self._invoke_with_retry(messages)
            
            return {
                "review_analysis": response.content,
                "enhancement_areas": self._extract_enhancement_areas(response.content)
            }
            
        except Exception as e:
            logging.error(f"Error in standard analysis: {str(e)}")
            return {
                "review_analysis": "Analysis failed due to technical error",
                "enhancement_areas": []
            }
            
    def _extract_enhancement_areas(self, analysis: str) -> List[str]:
        """Extract key enhancement areas from analysis text"""
        try:
            messages = [
                SystemMessage(content="Extract the key areas needing enhancement from the analysis. Return as a list."),
                HumanMessage(content=analysis)
            ]
            
            response = self._invoke_with_retry(messages)
            return [area.strip() for area in response.content.split('\n') if area.strip()]
            
        except Exception as e:
            logging.error(f"Error extracting enhancement areas: {str(e)}")
            return []

class ModeratorAgent(Agent):
    """
    ModeratorAgent coordinates expert discussions and builds consensus on standard enhancements.
    """
    def __init__(self):
        super().__init__(system_prompt="You are a skilled moderator coordinating expert discussions on Islamic financial standards.")
        self.experts = {
            "shariah": shariah_expert,
            "finance": finance_expert,
            "standards": standards_expert,
            "practical": practical_expert,
            "risk": risk_expert
        }
    
    def analyze_standard(self, standard_id: str, trigger_scenario: str) -> Dict[str, Any]:
        """
        Analyze standard and identify sections needing enhancement
        """
        # Extract relevant sections using vector search
        relevant_sections = self._search_standard(standard_id, trigger_scenario)
        
        # Identify gaps and ambiguities
        gaps = self._identify_gaps(relevant_sections, trigger_scenario)
        
        # Structure the findings for expert discussion
        discussion_context = self._prepare_discussion_context(gaps, trigger_scenario)
        
        return {
            "standard_id": standard_id,
            "sections": relevant_sections,
            "gaps": gaps,
            "discussion_context": discussion_context
        }
    
    async def moderate_discussion(self, proposal: Dict[str, Any], max_rounds: int = 3) -> Dict[str, Any]:
        """
        Moderate expert discussion to reach consensus on enhancement proposal
        """
        discussion_rounds = []
        current_proposal = proposal
        
        for round_num in range(max_rounds):
            # Get expert opinions
            expert_opinions = self._gather_expert_opinions(current_proposal)
            discussion_rounds.append(expert_opinions)
            
            # Monitor discussion progress
            discussion_status = self._monitor_discussion_progress(discussion_rounds)
            
            if discussion_status["status"] == "consensus_reached":
                return {
                    "status": "success",
                    "final_proposal": await self._generate_consensus_proposal(discussion_status["final_proposal"]),
                    "consensus_level": discussion_status["agreement_level"],
                    "discussion_summary": await self._generate_discussion_summary(discussion_rounds)
                }
            
            # Update proposal based on expert feedback
            current_proposal = self._refine_proposal(current_proposal, expert_opinions)
        
        # If max rounds reached without consensus
        return {
            "status": "max_rounds_reached",
            "current_proposal": current_proposal,
            "discussion_summary": await self._generate_discussion_summary(discussion_rounds),
            "remaining_concerns": self._extract_remaining_concerns(discussion_rounds)
        }
    
    def _gather_expert_opinions(self, proposal: Dict[str, Any]) -> Dict[str, Any]:
        """Gather opinions from all experts"""
        opinions = {}
        
        for domain, expert in self.experts.items():
            opinions[domain] = expert.analyze_proposal({
                "proposal": proposal["content"],
                "previous_discussion": proposal.get("previous_discussion", [])
            })
        
        return opinions
    
    def _monitor_discussion_progress(self, discussion_rounds: List[Dict]) -> Dict[str, Any]:
        """Monitor discussion progress and consensus level"""
        latest_round = discussion_rounds[-1]
        
        # Calculate agreement level
        agreement_level = self._calculate_agreement_level(latest_round)
        
        if agreement_level >= 0.8:  # 80% consensus threshold
            return {
                "status": "consensus_reached",
                "agreement_level": agreement_level,
                "final_proposal": self._generate_consensus_proposal(latest_round)
            }
        
        return {
            "status": "in_progress",
            "agreement_level": agreement_level,
            "next_focus": self._identify_discussion_focus(latest_round)
        }
    
    def _calculate_agreement_level(self, expert_opinions: Dict) -> float:
        """Calculate level of agreement between experts"""
        total_concerns = 0
        critical_concerns = 0
        
        for domain, opinion in expert_opinions.items():
            concerns = opinion.get("concerns", [])
            total_concerns += len(concerns)
            critical_concerns += len([c for c in concerns if c.get("severity") == "high"])
        
        if total_concerns == 0:
            return 1.0
        
        return 1.0 - (critical_concerns / total_concerns)
    
    async def _generate_consensus_proposal(self, expert_opinions: Dict) -> Dict[str, Any]:
        """Generate final proposal incorporating expert consensus"""
        messages = [
            SystemMessage(content="Generate a consensus proposal that addresses the key points and recommendations from all experts."),
            HumanMessage(content=f"Synthesize expert opinions into a final proposal:\n\n{str(expert_opinions)}")
        ]
        
        # Remove await since Gemini returns directly
        response = self.llm.invoke(messages)
        
        return {
            "content": response.content,
            "expert_opinions": expert_opinions,
            "consensus_rationale": self._extract_consensus_rationale(response.content)
        }
    
    async def _identify_discussion_focus(self, expert_opinions: Dict) -> Dict[str, Any]:
        """Identify next focus points for discussion"""
        # Collect all concerns and recommendations
        all_concerns = []
        all_recommendations = []
        
        for domain, opinion in expert_opinions.items():
            all_concerns.extend([(domain, c) for c in opinion.get("concerns", [])])
            all_recommendations.extend([(domain, r) for r in opinion.get("recommendations", [])])
        
        # Prioritize discussion points
        critical_concerns = [
            (d, c) for d, c in all_concerns 
            if c.get("severity", "").lower() in ["high", "critical"]
        ]
        
        high_priority_recs = [
            (d, r) for d, r in all_recommendations
            if r.get("priority", "").lower() in ["high", "critical"]
        ]
        
        return {
            "critical_concerns": critical_concerns,
            "priority_recommendations": high_priority_recs,
            "suggested_focus": await self._suggest_discussion_focus(critical_concerns, high_priority_recs)
        }
    
    async def _suggest_discussion_focus(self, concerns: List, recommendations: List) -> str:
        """Suggest specific focus for next discussion round"""
        messages = [
            SystemMessage(content="Analyze concerns and recommendations to suggest the most important focus for the next discussion round."),
            HumanMessage(content=f"""
            Critical Concerns:
            {str(concerns)}
            
            Priority Recommendations:
            {str(recommendations)}
            
            Suggest the most important aspect to focus on next.
            """)
        ]
        
        # Remove await since Gemini returns directly
        response = self.llm.invoke(messages)
        return response.content

    async def _generate_discussion_summary(self, discussion_rounds: List) -> str:
        """Generate summary of the discussion process"""
        messages = [
            SystemMessage(content="Generate a concise summary of the expert discussion process, highlighting key points of agreement and disagreement."),
            HumanMessage(content=f"Summarize the following discussion rounds:\n\n{str(discussion_rounds)}")
        ]
        
        # Remove await since Gemini returns directly
        response = self.llm.invoke(messages)
        return response.content
    
    def _extract_remaining_concerns(self, discussion_rounds: List) -> List[Dict]:
        """Extract unresolved concerns from discussion"""
        latest_round = discussion_rounds[-1]
        remaining_concerns = []
        
        for domain, opinion in latest_round.items():
            concerns = opinion.get("concerns", [])
            remaining_concerns.extend([
                {
                    "domain": domain,
                    **concern
                }
                for concern in concerns
                if concern.get("severity", "").lower() in ["high", "critical"]
            ])
        
        return remaining_concerns

# Initialize the agents
reviewer_agent = ReviewerAgent()
moderator_agent = ModeratorAgent()