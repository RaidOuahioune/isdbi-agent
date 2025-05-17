"""
Orchestrates the standards enhancement process by coordinating expert agents
and managing the discussion flow.
"""

from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass
from datetime import datetime
import logging
import asyncio

from ..monitoring.discussion_monitor import DiscussionMonitor
from ..agents.base_agent import Agent
from ..agents.reviewer_agent import reviewer_agent
from ..agents.proposer_agent import proposer_agent
from ..agents.validator_agent import validator_agent
from ..agents.cross_standard_analyzer import cross_standard_analyzer
from ..agents.expert_agents import (
    shariah_expert,
    finance_expert, 
    standards_expert,
    practical_expert
)

@dataclass
class EnhancementContext:
    """Context for a standards enhancement session"""
    standard_id: str
    trigger_scenario: str
    original_text: str
    proposed_text: str
    analysis: Dict
    concerns: List[str]
    discussion_history: List[Dict]
    round: int = 0

class EnhancementOrchestrator:
    def __init__(self, selected_experts=None):
        self.discussion_monitor = DiscussionMonitor()
        
        # Import expert agents
        from components.agents.expert_agents import (
            shariah_expert,
            finance_expert,
            standards_expert,
            practical_expert,
            risk_expert
        )
        
        # Base experts that are always included
        base_experts = {
            "shariah": shariah_expert,
            "finance": finance_expert,
            "standards": standards_expert
        }
        
        # Optional experts
        optional_experts = {
            "practical": practical_expert,
            "risk": risk_expert
        }
        
        # If no selection provided, use base experts plus practical expert by default
        if selected_experts is None:
            selected_experts = {
                "shariah": True,
                "finance": True, 
                "standards": True,
                "practical": True,
                "risk": False
            }
            
        # Initialize expert agents based on selection
        self.expert_agents = base_experts.copy()  # Start with required experts
        
        # Add optional experts if selected
        for name, expert in optional_experts.items():
            if selected_experts.get(name, False):
                self.expert_agents[name] = expert
                
        self.max_rounds = 2  # Reduced from 3 to 2 rounds

    def _report_progress(
        self,
        callback: Optional[Callable[[str, Optional[str]], None]],
        detail: str,
        phase: str = None
    ):
        """Report progress through the callback if provided"""
        if callback:
            callback(phase if phase else "progress", detail)
            
    async def _get_standard_text(self, standard_id: str) -> str:
        """Get the original text of the standard"""
        try:
            # Use the standards retriever to get text
            from retreiver import retriever
            nodes = retriever.retrieve(f"Full text of FAS {standard_id}")
            if nodes:
                return nodes[0].text
            return ""
        except Exception as e:
            logging.error(f"Error retrieving standard text: {str(e)}")
            return ""
            
    async def _get_initial_analysis(self, context: EnhancementContext) -> Dict:
        """Get initial analysis of the standard"""
        try:
            analysis = await reviewer_agent.analyze_standard({
                "standard_id": context.standard_id,
                "trigger_scenario": context.trigger_scenario,
                "text": context.original_text
            })
            return analysis
        except Exception as e:
            logging.error(f"Error in initial analysis: {str(e)}")
            return {
                "review_analysis": "Initial analysis unavailable due to error",
                "enhancement_areas": []
            }

    async def run_enhancement(
        self,
        standard_id: str,
        trigger_scenario: str,
        progress_callback: Optional[Callable[[str, Optional[str]], None]] = None,
        include_cross_standard_analysis: bool = False
    ) -> Dict[str, Any]:
        """Run the enhancement process."""
        try:
            # Create initial context
            context = EnhancementContext(
                standard_id=standard_id,
                trigger_scenario=trigger_scenario,
                original_text="",  # This should be retrieved
                proposed_text="",  # This will be populated during process
                analysis={},
                concerns=[],
                round=0,
                discussion_history=[]
            )

            # Add progress callback
            self._report_progress(progress_callback, "Starting review phase...")
            
            # Get original text from standards retriever
            context.original_text = await self._get_standard_text(standard_id)
            
            # Initial analysis
            self._report_progress(progress_callback, "Starting initial analysis...")
            initial_analysis = await self._get_initial_analysis(context)
            context.analysis = initial_analysis
            
            # Generate enhancement proposal
            self._report_progress(progress_callback, "Initial analysis complete")
            self._report_progress(progress_callback, "Generating enhancement proposal...")
            context.proposed_text = await self._generate_proposal(context)
            
            if not context.proposed_text:
                raise ValueError("Failed to generate enhancement proposal")

            # Expert discussion
            self._report_progress(progress_callback, "Enhancement proposal generated")
            enhancement_result = await self._facilitate_expert_discussion(context, progress_callback)
            
            # Final validation
            self._report_progress(progress_callback, "Starting validation phase...")
            try:
                validation_result = validator_agent.validate_proposal(self._compile_final_proposal(context))
                # Ensure validation result is properly formatted
                if isinstance(validation_result, dict):
                    validation_text = validation_result.get("text", "") or str(validation_result)
                else:
                    validation_text = str(validation_result)
            except Exception as e:
                logging.error(f"Validation error: {str(e)}")
                validation_text = "Error during validation"

            # Cross-standard analysis if requested
            cross_analysis_result = None
            if include_cross_standard_analysis:
                cross_analysis_result = cross_standard_analyzer.analyze_impact(context)
            
            return {
                "standard_id": context.standard_id,
                "trigger_scenario": context.trigger_scenario,
                "original_text": context.original_text,
                "proposed_text": context.proposed_text,
                "review": context.analysis.get("review_analysis", ""),
                "proposal": context.proposed_text,
                "validation": validation_text,  # Now ensured to be a string
                "discussion_history": context.discussion_history,
                "cross_standard_analysis": cross_analysis_result
            }
            
        except Exception as e:
            logging.error(f"Error in enhancement process: {str(e)}")
            raise

    def _initialize_context(self, standard_id: str, trigger_scenario: str) -> EnhancementContext:
        """Initialize a new enhancement context"""
        return EnhancementContext(
            standard_id=standard_id,
            trigger_scenario=trigger_scenario,
            original_text="",
            proposed_text="",
            analysis={},
            concerns=[],
            discussion_history=[],
            round=0
        )
        
    async def _facilitate_expert_discussion(
        self,
        context: EnhancementContext,
        progress_callback: Optional[Callable] = None
    ) -> Dict:
        """Facilitate discussion between expert agents to refine the proposal"""
        while context.round < self.max_rounds:
            context.round += 1
            
            if progress_callback:
                progress_callback(
                    "discussion_round",
                    f"Starting discussion round {context.round}..."
                )
            
            # Collect expert contributions
            round_contributions = await self._collect_expert_contributions(context)
            context.discussion_history.extend(round_contributions)
            
            # Update concerns and proposed text based on expert feedback
            self._update_context_from_contributions(context, round_contributions)
            
            # Check for consensus
            if self.discussion_monitor.check_consensus(context.discussion_history):
                if progress_callback:
                    progress_callback(
                        "discussion_complete",
                        "Consensus reached in expert discussion"
                    )
                break
                
            # Check for convergence if not final round
            if context.round < self.max_rounds:
                if self.discussion_monitor.check_convergence(context.discussion_history):
                    if progress_callback:
                        progress_callback(
                            "discussion_complete",
                            "Discussion converged on solution"
                        )
                    break
        
        # Compile final enhancement proposal
        return self._compile_final_proposal(context)
        
    async def _collect_expert_contributions(self, context: EnhancementContext) -> List[Dict]:
        """Collect contributions from all expert agents for current round"""
        tasks = []
        for expert_name, expert in self.expert_agents.items():
            tasks.append(self._get_expert_contribution(expert_name, expert, context))
        
        contributions = await asyncio.gather(*tasks)
        return contributions

    async def _get_expert_contribution(self, expert_name: str, expert: Agent, context: EnhancementContext) -> Dict:
        """Get contribution from a single expert"""
        try:
            contribution = expert.analyze_proposal({
                "proposal": context.proposed_text,
                "analysis": context.analysis,
                "concerns": context.concerns,
                "previous_discussion": context.discussion_history
            })
            
            return {
                "type": "discussion",
                "round": context.round,
                "timestamp": datetime.now().isoformat(),
                "agent": expert_name,
                "content": contribution
            }
        except Exception as e:
            logging.error(f"Error getting contribution from {expert_name}: {str(e)}")
            return {
                "type": "discussion",
                "round": context.round,
                "timestamp": datetime.now().isoformat(),
                "agent": expert_name,
                "content": {
                    "analysis": {"text": "Analysis temporarily unavailable"},
                    "concerns": [],
                    "recommendations": []
                }
            }
        
    def _update_context_from_contributions(
        self,
        context: EnhancementContext,
        contributions: List[Dict]
    ):
        """Update context based on expert contributions"""
        # Collect all concerns and suggestions
        new_concerns = []
        text_suggestions = []
        
        for contrib in contributions:
            content = contrib["content"]
            # Add new concerns to list without trying to remove duplicates
            new_concerns.extend(content.get("concerns", []))
            
            if "suggested_text" in content:
                text_suggestions.append(content["suggested_text"])
        
        # Update concerns - custom deduplication since concerns are dicts
        seen_descriptions = set()
        unique_concerns = []
        
        # First add existing concerns
        for concern in context.concerns:
            desc = concern["description"] if isinstance(concern, dict) else str(concern)
            if desc not in seen_descriptions:
                seen_descriptions.add(desc)
                unique_concerns.append(concern)
        
        # Then add new concerns
        for concern in new_concerns:
            desc = concern["description"] if isinstance(concern, dict) else str(concern)
            if desc not in seen_descriptions:
                seen_descriptions.add(desc)
                unique_concerns.append(concern)
        
        context.concerns = unique_concerns
        
        # Update proposed text if we have suggestions
        if text_suggestions:
            # Use the most common suggestion or keep current if no consensus
            from collections import Counter
            suggestion_counts = Counter(text_suggestions)
            most_common = suggestion_counts.most_common(1)
            if most_common and most_common[0][1] > len(text_suggestions) / 2:
                context.proposed_text = most_common[0][0]
                
    def _compile_final_proposal(self, context: EnhancementContext) -> Dict:
        """Compile the final enhancement proposal from discussion results"""
        try:
            # Get consensus metrics
            metrics = self.discussion_monitor._calculate_consensus_metrics(
                self._get_latest_round_contributions(context)
            )
            
            return {
                "standard_id": context.standard_id,
                "trigger_scenario": context.trigger_scenario,
                # Add the full proposal content from initial analysis
                "enhancement_proposal": {
                    "proposal": context.proposed_text,
                    "original_text": context.original_text,
                    "analysis": context.analysis,  # Include full analysis
                    "rationale": context.analysis.get("review_analysis", "")  # Include rationale
                },
                "original_text": context.original_text,
                "proposed_text": context.proposed_text,
                "concerns_addressed": metrics.resolved_points if metrics else [],
                "remaining_concerns": metrics.unresolved_points if metrics else [],
                "expert_consensus_level": metrics.agreement_score if metrics else 0.0,
                "discussion_rounds": context.round,
                "discussion_history": context.discussion_history
            }
        except Exception as e:
            logging.error(f"Error compiling final proposal: {str(e)}")
            # Return a minimal valid proposal that won't break validation
            return {
                "standard_id": context.standard_id,
                "trigger_scenario": context.trigger_scenario,
                "enhancement_proposal": {
                    "proposal": context.proposed_text or "No enhancement proposal available",
                    "original_text": context.original_text or "No original text available",
                    "analysis": context.analysis or {},
                    "rationale": context.analysis.get("review_analysis", "No rationale available")
                },
                "original_text": context.original_text or "No original text available",
                "proposed_text": context.proposed_text or "No proposal available",
                "concerns_addressed": [],
                "remaining_concerns": [],
                "expert_consensus_level": 0.0,
                "discussion_rounds": context.round,
                "discussion_history": context.discussion_history
            }
        
    def _get_latest_round_contributions(self, context: EnhancementContext) -> List[Dict]:
        """Get contributions from the latest discussion round"""
        return [
            contrib for contrib in context.discussion_history
            if contrib["round"] == context.round
        ]

    async def _generate_proposal(self, context: EnhancementContext) -> str:
        """Generate enhancement proposal based on analysis."""
        try:
            proposal = await proposer_agent({
                "standard_id": context.standard_id,
                "trigger_scenario": context.trigger_scenario,
                "original_text": context.original_text,
                "analysis": context.analysis
            })
            
            if isinstance(proposal, dict):
                return proposal.get("proposal", "")
            elif isinstance(proposal, str):
                return proposal
            else:
                logging.error(f"Unexpected proposal format: {type(proposal)}")
                return ""
                
        except Exception as e:
            logging.error(f"Error generating proposal: {str(e)}")
            return ""