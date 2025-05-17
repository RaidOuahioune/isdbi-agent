"""
Orchestrates the standards enhancement process by coordinating various agents
and managing the iterative refinement workflow.
"""

import asyncio
import dataclasses
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

# Assuming these paths are correct for your project structure
from ..agents.base_agent import Agent # Base Agent class
from ..agents.reviewer_agent import reviewer_agent
from ..agents.proposer_agent import proposer_agent # The structured-output version
from ..agents.validator_agent import validator_agent
from ..agents.cross_standard_analyzer import cross_standard_analyzer
from ..agents.expert_agents import (
    shariah_expert,
    finance_expert,
    standards_expert,
    practical_expert,
    risk_expert # Ensure risk_expert is also imported if used
)
# Now importing the actual DiscussionMonitor
from ..monitoring.discussion_monitor import DiscussionMonitor, ConsensusMetrics
# Assuming retriever is correctly set up and importable
from retreiver import retriever


logger = logging.getLogger(__name__)

@dataclass
class EnhancementContext:
    """Context for a standards enhancement session."""
    standard_id: str
    trigger_scenario: str
    reviewer_retrieved_context: str = "" # Specific context analyzed by reviewer
    initial_reviewer_analysis: Dict[str, Any] = field(default_factory=dict) # Full output from reviewer
    
    current_proposal_structured_text: str = ""
    initial_proposal_structured_text: str = ""

    accumulated_concerns: List[Dict] = field(default_factory=list) # From experts
    accumulated_recommendations: List[Dict] = field(default_factory=list) # From experts
    
    discussion_history: List[Dict] = field(default_factory=list) # Raw contributions
    current_round: int = 0
    consensus_metrics_history: List[ConsensusMetrics] = field(default_factory=list) # Store metrics per round

class EnhancementOrchestrator:
    def __init__(self, selected_experts_config: Optional[Dict[str, bool]] = None, max_discussion_rounds: int = 2):
        # Initialize DiscussionMonitor here
        self.discussion_monitor = DiscussionMonitor()
        self.max_rounds = max_discussion_rounds

        all_available_experts = {
            "shariah": shariah_expert,
            "finance": finance_expert,
            "standards": standards_expert,
            "practical": practical_expert,
            "risk": risk_expert
        }

        if selected_experts_config is None:
            selected_experts_config = {
                "shariah": True, "finance": True, "standards": True,
                "practical": True, "risk": False
            }

        self.expert_agents: Dict[str, Agent] = {}
        for name, expert_instance in all_available_experts.items():
            if selected_experts_config.get(name, False):
                self.expert_agents[name] = expert_instance
        
        logger.info(f"Orchestrator initialized with experts: {list(self.expert_agents.keys())} and max_rounds: {self.max_rounds}")

    def _report_progress(
        self,
        callback: Optional[Callable[[str, Optional[str]], None]],
        phase: str,
        detail: str
    ):
        if callback:
            try:
                callback(phase, detail)
            except Exception as e:
                logger.warning(f"Error in progress callback: {e}")
        logger.info(f"Progress: [{phase}] - {detail}")

    async def _get_full_standard_text(self, standard_id: str) -> str: # Kept for potential future use
        try:
            nodes = retriever.retrieve(f"Complete text of AAOIFI FAS {standard_id}")
            if nodes:
                return "\n".join([node.text for node in nodes])
            logger.warning(f"No text found by retriever for full standard FAS {standard_id}.")
            return ""
        except Exception as e:
            logger.error(f"Error retrieving full standard text for FAS {standard_id}: {e}")
            return ""

    async def run_enhancement_workflow(
        self,
        standard_id: str,
        trigger_scenario: str,
        progress_callback: Optional[Callable[[str, Optional[str]], None]] = None,
        include_cross_standard_analysis: bool = False
    ) -> Dict[str, Any]:
        self._report_progress(progress_callback, "WorkflowStart", f"Starting enhancement for FAS {standard_id} on: {trigger_scenario}")
        context = EnhancementContext(standard_id=standard_id, trigger_scenario=trigger_scenario)

        try:            # --- 1. Review Phase ---
            self._report_progress(progress_callback, "ReviewPhase", "Starting initial standard review...")           
            reviewer_input = {
                "standard_id": standard_id, 
                "trigger_scenario": trigger_scenario
            }
            reviewer_output = await reviewer_agent.analyze_standard(reviewer_input)
            context.initial_reviewer_analysis = reviewer_output
            context.reviewer_retrieved_context = reviewer_output.get("text", "") or reviewer_output.get("review_content", "")
            if not context.reviewer_retrieved_context:
                logger.warning("Reviewer did not return retrieved_context.")
            self._report_progress(progress_callback, "ReviewPhaseComplete", "Initial review complete.")

            # --- 2. Initial Proposal Generation Phase ---
            self._report_progress(progress_callback, "ProposalPhase", "Generating initial enhancement proposal...")
            proposer_input = {
                "standard_id": context.standard_id,
                "trigger_scenario": context.trigger_scenario,
                "retrieved_context": context.reviewer_retrieved_context,
                "review_analysis": context.initial_reviewer_analysis.get("review_analysis", ""),
                "enhancement_areas": context.initial_reviewer_analysis.get("enhancement_areas", [])
            }
            initial_proposal_result = await proposer_agent.generate_enhancement_proposal(proposer_input)
            context.initial_proposal_structured_text = initial_proposal_result.get("enhancement_proposal_structured", "")
            context.current_proposal_structured_text = context.initial_proposal_structured_text

            if not context.current_proposal_structured_text:
                self._report_progress(progress_callback, "WorkflowError", "Failed to generate initial proposal.")
                raise ValueError("Initial proposal generation failed.")
            self._report_progress(progress_callback, "ProposalPhaseComplete", "Initial proposal generated.")

            # --- 3. Expert Discussion and Refinement Phase ---
            if self.expert_agents and self.max_rounds > 0:
                self._report_progress(progress_callback, "DiscussionPhase", "Starting expert discussion and refinement...")
                await self._facilitate_expert_discussion_and_refinement(context, progress_callback)
                self._report_progress(progress_callback, "DiscussionPhaseComplete", "Expert discussion and refinement finished.")
            else:
                self._report_progress(progress_callback, "DiscussionPhaseSkipped", "Skipping discussion (no experts or max_rounds is 0).")

            # --- 4. Validation Phase ---
            self._report_progress(progress_callback, "ValidationPhase", "Validating final proposal...")
            final_proposal_for_validation = self._compile_final_output(context, "validation_input")
            validation_text = "Validation not performed."
            try:
                # Assuming validator_agent.validate_proposal is synchronous. If async, use await.
                validation_result_raw = validator_agent.validate_proposal(final_proposal_for_validation)
                if isinstance(validation_result_raw, dict):
                    validation_text = validation_result_raw.get("validation_summary", str(validation_result_raw))
                elif isinstance(validation_result_raw, str):
                    validation_text = validation_result_raw
                else:
                    validation_text = "Validation result in unexpected format."
                logger.info(f"Validation result: {validation_text}")
            except Exception as e:
                logger.error(f"Error during validation phase: {e}")
                validation_text = f"Validation failed due to an error: {str(e)}"
            self._report_progress(progress_callback, "ValidationPhaseComplete", "Validation complete.")

            # --- 5. Cross-Standard Analysis Phase (Optional) ---
            cross_analysis_text = None
            if include_cross_standard_analysis:
                self._report_progress(progress_callback, "CrossStandardAnalysisPhase", "Performing cross-standard impact analysis...")
                try:
                    impact_analysis_input = {
                        "standard_id": context.standard_id,
                        "proposed_changes_summary": context.current_proposal_structured_text,
                        "trigger_scenario": context.trigger_scenario
                    }
                    # Assuming cross_standard_analyzer.analyze_cross_standard_impact is synchronous. If async, use await.
                    cross_analysis_result_raw = cross_standard_analyzer.analyze_cross_standard_impact(impact_analysis_input)
                    cross_analysis_text = cross_analysis_result_raw.get("cross_standard_analysis", str(cross_analysis_result_raw))
                except Exception as e:
                    logger.error(f"Error during cross-standard analysis: {e}")
                    cross_analysis_text = f"Cross-standard analysis failed: {str(e)}"
                self._report_progress(progress_callback, "CrossStandardAnalysisPhaseComplete", "Cross-standard analysis complete.")
            
            self._report_progress(progress_callback, "WorkflowComplete", "Enhancement workflow finished successfully.")
            return self._compile_final_output(context, "final_workflow_output", validation_text, cross_analysis_text)

        except Exception as e:
            logger.error(f"Critical error in enhancement workflow for FAS {standard_id}: {e}", exc_info=True)
            self._report_progress(progress_callback, "WorkflowError", f"Workflow failed: {str(e)}")
            return {
                "error": str(e), "standard_id": standard_id, "trigger_scenario": trigger_scenario,
                "status": "failed", "current_phase_context_snapshot": dataclasses.asdict(context) if context else None
            }

    async def _facilitate_expert_discussion_and_refinement(
        self,
        context: EnhancementContext,
        progress_callback: Optional[Callable[[str, Optional[str]], None]]
    ):
        for i in range(self.max_rounds):
            context.current_round = i + 1
            self._report_progress(progress_callback, "DiscussionRoundStart", f"Starting discussion round {context.current_round}/{self.max_rounds}.")

            expert_contributions_raw = await self._collect_expert_contributions(context)
            
            # Filter out error contributions for consensus calculation, but keep them in history
            valid_expert_contributions_for_round = [
                c for c in expert_contributions_raw if c.get("type") == "discussion_contribution"
            ]
            context.discussion_history.extend(expert_contributions_raw)

            current_round_concerns, current_round_recommendations = self._process_expert_contributions(valid_expert_contributions_for_round)
            context.accumulated_concerns.extend(current_round_concerns) # Consider deduplication if needed
            context.accumulated_recommendations.extend(current_round_recommendations) # Consider deduplication

            self._report_progress(progress_callback, f"DiscussionRoundFeedback_R{context.current_round}", 
                                  f"Collected {len(valid_expert_contributions_for_round)} valid expert opinions. "
                                  f"{len(current_round_concerns)} new concerns, {len(current_round_recommendations)} new recommendations.")

            # Calculate and store consensus metrics for the current round's valid contributions
            if valid_expert_contributions_for_round:
                # The DiscussionMonitor._calculate_consensus_metrics expects a list of contribution *contents*
                # However, the provided DiscussionMonitor expects the full contribution dicts. Let's adapt.
                # The provided DiscussionMonitor's _get_latest_round and _group_by_rounds
                # expect "type": "discussion" and "round": round_num.
                # Our current structure is "type": "discussion_contribution". We need to align or adapt.
                # For now, let's assume the monitor can handle our structure or we adapt the input.
                # The monitor's _extract_key_points works on the 'content' field of the contribution.
                
                # To use the provided DiscussionMonitor's _calculate_consensus_metrics,
                # it expects a list of contribution dicts for the current round.
                # Let's filter the history for the current round for the monitor.
                current_round_history_for_monitor = [
                    item for item in context.discussion_history 
                    if item.get("round") == context.current_round and item.get("type") == "discussion_contribution"
                ]
                if current_round_history_for_monitor: # Ensure there are contributions to analyze
                    metrics = self.discussion_monitor._calculate_consensus_metrics(current_round_history_for_monitor)
                    context.consensus_metrics_history.append(metrics)
                    self._report_progress(progress_callback, f"ConsensusMetrics_R{context.current_round}", 
                                          f"Agreement: {metrics.agreement_score:.2f}, Unresolved: {len(metrics.unresolved_points)}")
                    
                    # Check for consensus to potentially break early
                    if self.discussion_monitor.check_consensus(context.discussion_history): # Pass full history
                        self._report_progress(progress_callback, "DiscussionConsensusReached", "Consensus threshold met.")
                        break
                else:
                     self._report_progress(progress_callback, f"ConsensusMetrics_R{context.current_round}", "No valid expert contributions to calculate consensus.")


            # Refine Proposal
            if context.current_round <= self.max_rounds: # Refine after each round
                self._report_progress(progress_callback, f"ProposalRefinement_R{context.current_round}", "Attempting to refine proposal...")
                refinement_input = {
                    "standard_id": context.standard_id,
                    "trigger_scenario": context.trigger_scenario,
                    "retrieved_context": context.reviewer_retrieved_context,
                    "review_analysis": context.initial_reviewer_analysis.get("review_analysis", ""),
                    "enhancement_areas": context.initial_reviewer_analysis.get("enhancement_areas", []),
                    "current_proposal_text": context.current_proposal_structured_text,
                    "expert_feedback_summary": {
                        "concerns": current_round_concerns, # Feedback from this round
                        "recommendations": current_round_recommendations
                    }
                }
                try:
                    refined_proposal_result = await proposer_agent.generate_enhancement_proposal(refinement_input)
                    refined_text = refined_proposal_result.get("enhancement_proposal_structured")
                    if refined_text and refined_text.strip() and refined_text != context.current_proposal_structured_text:
                        context.current_proposal_structured_text = refined_text
                        self._report_progress(progress_callback, f"ProposalRefinementSuccess_R{context.current_round}", "Proposal refined.")
                    else:
                        self._report_progress(progress_callback, f"ProposalRefinementNoChange_R{context.current_round}", "Proposal not significantly changed by refinement.")
                except Exception as e:
                    logger.error(f"Error during proposal refinement in round {context.current_round}: {e}")
                    self._report_progress(progress_callback, f"ProposalRefinementError_R{context.current_round}", f"Refinement error: {str(e)}")
            
            if context.current_round == self.max_rounds:
                 self._report_progress(progress_callback, "DiscussionMaxRounds", "Maximum discussion rounds reached.")


    async def _collect_expert_contributions(self, context: EnhancementContext) -> List[Dict]:
        tasks = []
        for expert_name, expert_instance in self.expert_agents.items():
            tasks.append(self._get_single_expert_contribution(expert_name, expert_instance, context))
        
        contributions_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        processed_contributions = []
        for i, result in enumerate(contributions_results):
            expert_name = list(self.expert_agents.keys())[i] # Relies on dict insertion order (Python 3.7+)
            if isinstance(result, Exception):
                logger.error(f"Exception from {expert_name} in round {context.current_round}: {result}")
                processed_contributions.append({
                    "type": "discussion_error", "round": context.current_round,
                    "timestamp": datetime.now().isoformat(), "agent": expert_name,
                    "error_message": str(result),
                    "content": {"analysis": {"text": "Analysis failed due to error"}, "concerns": [], "recommendations": []}
                })
            elif isinstance(result, dict): # Expected successful contribution
                 processed_contributions.append(result)
            else: # Unexpected result type
                logger.error(f"Unexpected result type from {expert_name}: {type(result)}")
                processed_contributions.append({
                    "type": "discussion_error", "round": context.current_round,
                    "timestamp": datetime.now().isoformat(), "agent": expert_name,
                    "error_message": "Unexpected result type from agent.",
                    "content": {"analysis": {"text": "Analysis failed due to unexpected agent output"}, "concerns": [], "recommendations": []}
                })
        return processed_contributions

    async def _get_single_expert_contribution(self, expert_name: str, expert: Agent, context: EnhancementContext) -> Dict:
        logger.info(f"Requesting contribution from {expert_name} for round {context.current_round}...")
        expert_input = {
            "proposal": context.current_proposal_structured_text,
            "previous_discussion": context.discussion_history
        }
        contribution_content = await expert.analyze_proposal(expert_input) # This is async
        return {
            "type": "discussion_contribution", # Changed from "discussion" for clarity
            "round": context.current_round,
            "timestamp": datetime.now().isoformat(),
            "agent": expert_name,
            "content": contribution_content
        }
        
    def _process_expert_contributions(self, contributions: List[Dict]) -> tuple[List[Dict], List[Dict]]:
        all_concerns = []
        all_recommendations = []
        for contrib_wrapper in contributions: # Iterate over the wrapped contributions
            # Ensure we are processing actual contribution content
            if contrib_wrapper.get("type") == "discussion_contribution":
                content = contrib_wrapper.get("content", {})
                # Expert agents now return concerns/recommendations as lists of dicts
                concerns_from_expert = content.get("concerns", [])
                if concerns_from_expert: # Ensure it's not None
                    all_concerns.extend(concerns_from_expert)
                
                recommendations_from_expert = content.get("recommendations", [])
                if recommendations_from_expert: # Ensure it's not None
                    all_recommendations.extend(recommendations_from_expert)
        return all_concerns, all_recommendations

    def _compile_final_output(
        self, 
        context: EnhancementContext,
        output_type: str,
        validation_summary: Optional[str] = None,
        cross_analysis_summary: Optional[str] = None
    ) -> Dict[str, Any]:
        
        last_consensus_metrics = context.consensus_metrics_history[-1] if context.consensus_metrics_history else None
        agreement_score = last_consensus_metrics.agreement_score if last_consensus_metrics else 0.0
        unresolved_points = last_consensus_metrics.unresolved_points if last_consensus_metrics else []
        resolved_points = last_consensus_metrics.resolved_points if last_consensus_metrics else []


        final_data = {
            "standard_id": context.standard_id,
            "trigger_scenario": context.trigger_scenario,
            "reviewer_analysis_summary": context.initial_reviewer_analysis.get("review_analysis", ""),
            "reviewer_enhancement_areas": context.initial_reviewer_analysis.get("enhancement_areas", []),
            "reviewer_retrieved_context": context.reviewer_retrieved_context,
            "initial_proposal_structured": context.initial_proposal_structured_text,
            "final_proposal_structured": context.current_proposal_structured_text,
            "discussion_rounds_completed": context.current_round,
            "accumulated_expert_concerns": context.accumulated_concerns, # Full list of concerns raised
            "accumulated_expert_recommendations": context.accumulated_recommendations, # Full list of recs
            "final_agreement_score": agreement_score,
            "final_resolved_points": resolved_points,
            "final_unresolved_points": unresolved_points,
            "discussion_history": context.discussion_history, # Full raw history
            "consensus_metrics_per_round": [dataclasses.asdict(cm) for cm in context.consensus_metrics_history]
        }

        if output_type == "final_workflow_output":
            final_data["validation_summary"] = validation_summary
            final_data["cross_standard_analysis_summary"] = cross_analysis_summary
            final_data["status"] = "completed"
            return final_data
        
        if output_type == "validation_input":
            # Validator might need a specific subset of information
            return {
                 "standard_id": context.standard_id,
                 "enhancement_proposal": context.current_proposal_structured_text, # The final version
                 "trigger_scenario": context.trigger_scenario,
                 "original_standard_context": context.reviewer_retrieved_context,
                 "initial_analysis_summary": context.initial_reviewer_analysis.get("review_analysis")
                 # Add any other fields the validator specifically needs
            }
        
        # Default to returning the comprehensive data if output_type is not matched
        return final_data