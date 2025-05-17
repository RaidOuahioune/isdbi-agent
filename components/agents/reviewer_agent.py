from typing import Dict, Any, List
from components.agents.base_agent import Agent
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from retreiver import retriever
import logging

from .expert_agents import (
    shariah_expert,
    finance_expert,
    standards_expert,
    practical_expert,
    risk_expert
)

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

class ReviewerAgent(Agent):
    """Agent responsible for initial analysis of standards and enhancement needs"""

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
- Specific clauses or definitions that lack clarity or could be improved
- Areas where the standard might not fully address the trigger scenario
- Specific text that could be ambiguous when applied to this scenario
- Potential inconsistencies within the standard or with other standards
""")
        ]

        # Get analysis result
        response = self._invoke_with_retry(messages)
        
        return {
            "standard_id": standard_id,
            "trigger_scenario": trigger_scenario,
            "review_content": context, 
            "review_analysis": response.content,
            "enhancement_areas": self._extract_enhancement_areas(response.content)
        }
        
    async def analyze_standard(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a standard and identify enhancement needs"""
        try:
            # If context doesn't have 'text', retrieve it using the retriever
            if 'text' not in context:
                retrieval_query = f"Standard FAS {context['standard_id']} elements that might need enhancement regarding: {context['trigger_scenario']}"
                retrieved_nodes = retriever.retrieve(retrieval_query)
                context['text'] = "\n\n".join([node.text for node in retrieved_nodes])
            
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
                "enhancement_areas": self._extract_enhancement_areas(response.content),
                "text": context['text']  # Explicitly include the retrieved text in the response
            }
            
        except Exception as e:
            logging.error(f"Error in standard analysis: {str(e)}")
            return {
                "review_analysis": "Analysis failed due to technical error",
                "enhancement_areas": [],
                "text": context.get('text', "")  # Include text field even in error case
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
        
    def _invoke_with_retry(self, messages, max_retries=3):
        """Invoke LLM with retry logic"""
        for attempt in range(max_retries):
            try:
                return self.llm.invoke(messages)
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                logging.warning(f"Attempt {attempt+1} failed: {str(e)}. Retrying...")


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
        
    def _search_standard(self, standard_id: str, trigger_scenario: str) -> List[str]:
        """Search for relevant sections using retriever"""
        retrieval_query = f"Standard FAS {standard_id} elements that might need enhancement regarding: {trigger_scenario}"
        retrieved_nodes = retriever.retrieve(retrieval_query)
        return [node.text for node in retrieved_nodes]
    
    def _identify_gaps(self, relevant_sections: List[str], trigger_scenario: str) -> List[Dict[str, Any]]:
        """Identify gaps and ambiguities in standard sections"""
        sections_text = "\n\n".join(relevant_sections)
        
        messages = [
            SystemMessage(content="Identify gaps and ambiguities in the provided standard sections."),
            HumanMessage(content=f"""
            Trigger Scenario:
            {trigger_scenario}
            
            Standard Sections:
            {sections_text}
            
            Identify specific gaps, ambiguities, or areas needing enhancement.
            """)
        ]
        
        response = self._invoke_with_retry(messages)
        return self._parse_gaps(response.content)
    
    def _parse_gaps(self, gaps_text: str) -> List[Dict[str, Any]]:
        """Parse identified gaps into structured format"""
        try:
            messages = [
                SystemMessage(content="Parse the identified gaps into a structured list of dictionaries."),
                HumanMessage(content=gaps_text)
            ]
            
            response = self._invoke_with_retry(messages)
            
            # This is simplified - in practice you'd parse the response into a structured format
            lines = [line.strip() for line in response.content.split('\n') if line.strip()]
            gaps = []
            
            current_gap = {}
            for line in lines:
                if line.startswith('- '):
                    if current_gap and 'description' in current_gap:
                        gaps.append(current_gap)
                    current_gap = {'description': line[2:]}
                elif current_gap:
                    current_gap['details'] = current_gap.get('details', '') + ' ' + line
            
            if current_gap and 'description' in current_gap:
                gaps.append(current_gap)
                
            return gaps
        except Exception as e:
            logging.error(f"Error parsing gaps: {str(e)}")
            return []
    
    def _prepare_discussion_context(self, gaps: List[Dict[str, Any]], trigger_scenario: str) -> Dict[str, Any]:
        """Prepare context for expert discussion"""
        return {
            "trigger_scenario": trigger_scenario,
            "identified_gaps": gaps,
            "key_questions": self._generate_discussion_questions(gaps, trigger_scenario)
        }
    
    def _generate_discussion_questions(self, gaps: List[Dict[str, Any]], trigger_scenario: str) -> List[str]:
        """Generate key questions for expert discussion"""
        messages = [
            SystemMessage(content="Generate key questions for expert discussion based on identified gaps."),
            HumanMessage(content=f"""
            Trigger Scenario:
            {trigger_scenario}
            
            Identified Gaps:
            {str(gaps)}
            
            Generate 3-5 key questions to guide expert discussion.
            """)
        ]
        
        response = self._invoke_with_retry(messages)
        return [q.strip() for q in response.content.split('\n') if q.strip()]

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
        
        response = self.llm.invoke(messages)
        
        return {
            "content": response.content,
            "expert_opinions": expert_opinions,
            "consensus_rationale": self._extract_consensus_rationale(response.content)
        }
        
    def _extract_consensus_rationale(self, proposal_text: str) -> str:
        """Extract rationale from consensus proposal"""
        try:
            messages = [
                SystemMessage(content="Extract the key rationale behind the consensus proposal."),
                HumanMessage(content=proposal_text)
            ]
            
            response = self._invoke_with_retry(messages)
            return response.content
        except Exception as e:
            logging.error(f"Error extracting consensus rationale: {str(e)}")
            return "Rationale extraction failed due to technical error"

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
        
        response = self.llm.invoke(messages)
        return response.content

    async def _generate_discussion_summary(self, discussion_rounds: List) -> str:
        """Generate summary of the discussion process"""
        messages = [
            SystemMessage(content="Generate a concise summary of the expert discussion process, highlighting key points of agreement and disagreement."),
            HumanMessage(content=f"Summarize the following discussion rounds:\n\n{str(discussion_rounds)}")
        ]
        
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
        
    def _refine_proposal(self, proposal: Dict[str, Any], expert_opinions: Dict[str, Any]) -> Dict[str, Any]:
        """Refine proposal based on expert feedback"""
        messages = [
            SystemMessage(content="Refine the proposal based on expert feedback."),
            HumanMessage(content=f"""
            Current Proposal:
            {proposal['content']}
            
            Expert Feedback:
            {str(expert_opinions)}
            
            Provide an updated proposal that addresses expert feedback.
            """)
        ]
        
        response = self._invoke_with_retry(messages)
        
        return {
            "content": response.content,
            "previous_discussion": proposal.get("previous_discussion", []) + [expert_opinions]
        }
        
    def _invoke_with_retry(self, messages, max_retries=3):
        """Invoke LLM with retry logic"""
        for attempt in range(max_retries):
            try:
                return self.llm.invoke(messages)
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                logging.warning(f"Attempt {attempt+1} failed: {str(e)}. Retrying...")


# Initialize the agents
reviewer_agent = ReviewerAgent()
moderator_agent = ModeratorAgent()