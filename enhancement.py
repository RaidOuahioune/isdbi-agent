from typing import Dict, Any, List, Optional, Callable
import asyncio
from components.orchestration.enhancement_orchestrator import EnhancementOrchestrator
from components.monitoring.discussion_monitor import DiscussionMonitor
from langchain_core.messages import AIMessage
import time

import logging

from agents import cross_standard_analyzer

# Initialize orchestrator
orchestrator = EnhancementOrchestrator()

# Define test cases for standards enhancement
ENHANCEMENT_TEST_CASES = [
    {
        "name": "Digital Assets in Istisna'a",
        "standard_id": "10",
        "trigger_scenario": """A financial institution wants to structure an Istisna'a contract for the development 
                              of a large-scale AI software platform. The current wording of FAS 10 on 'well-defined 
                              subject matter' and 'determination of cost' is causing uncertainty for intangible assets 
                              like software development."""
    },
    {
        "name": "Tokenized Mudarabah Investments",
        "standard_id": "4",
        "trigger_scenario": """Fintech platforms are offering investment in tokenized Mudarabah funds where investors can 
                              buy/sell fractional ownership tokens on blockchain networks. FAS 4 needs clarification on 
                              how to handle these digital representations of investment units and profit distribution in 
                              real-time token trading scenarios."""
    },
    {
        "name": "Green Sukuk Environmental Impact",
        "standard_id": "32",
        "trigger_scenario": """Islamic financial institutions are increasingly issuing 'Green Sukuk' to fund 
                              environmentally sustainable projects, but FAS 32 lacks specific guidance on how to account 
                              for and report environmental impact metrics alongside financial returns."""
    },
    {
        "name": "Digital Banking Services in Ijarah",
        "standard_id": "28",
        "trigger_scenario": """Islamic banks are offering digital banking services through cloud-based infrastructure 
                              leased through Ijarah arrangements. FAS 28 needs enhancement to address how to classify, 
                              recognize, and measure these digital service agreements which may include both tangible 
                              and intangible components."""
    },
    {
        "name": "Cryptocurrency Zakat Calculation",
        "standard_id": "7",
        "trigger_scenario": """Islamic financial institutions holding cryptocurrencies as assets need guidance on how 
                              to calculate and distribute Zakat on these volatile digital assets. The current FAS 7 
                              doesn't address value fluctuations and verification methods specific to crypto assets."""
    }
]


async def run_standards_enhancement_async(
    standard_id: str, 
    trigger_scenario: str,
    progress_callback: Optional[Callable[[str, str], None]] = None,
    include_cross_standard_analysis: bool = True
) -> Dict[str, Any]:
    """
    Async version of the standards enhancement process.
    """
    results = await orchestrator.run_enhancement_workflow(
        standard_id,
        trigger_scenario,
        progress_callback,
        include_cross_standard_analysis
    )
    
    # # Post-process results
    # from ui.output_parser import OutputParser
    # processed_results = OutputParser.parse_results_from_agents(results)
    
    return results

def run_standards_enhancement(
    standard_id: str, 
    trigger_scenario: str,
    progress_callback: Optional[Callable[[str, str], None]] = None,
    include_cross_standard_analysis: bool = True
) -> Dict[str, Any]:
    """
    Synchronous wrapper for the standards enhancement process.
    """
    # Create event loop if it doesn't exist
    
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    # Run enhancement process
    results = loop.run_until_complete(
        run_standards_enhancement_async(
            standard_id,
            trigger_scenario,
            progress_callback,
            include_cross_standard_analysis
        )
    )
    
    return results


def format_results_for_display(results: Dict[str, Any]) -> str:
    """Format enhancement results for display in console."""
    output = []
    
    try:
        # Add header
        output.append("="*50)
        output.append(f"Enhancement Results - FAS {results['standard_id']}")
        output.append("="*50)
        
        # Add trigger scenario (truncated)
        output.append("\nScenario:")
        output.append("-"*30)
        scenario = results.get("trigger_scenario", "")
        output.append(scenario[:200] + "..." if len(scenario) > 200 else scenario)
        
        # Add key findings from analysis
        output.append("\nKey Findings:")
        output.append("-"*30)
        if isinstance(results.get("review"), dict):
            analysis = results["review"].get("review_analysis", "")
            # Extract first paragraph or limit length
            if "\n\n" in analysis:
                analysis = analysis.split("\n\n")[0]
            output.append(analysis[:300] + "..." if len(analysis) > 300 else analysis)
        
        # Add core proposal
        output.append("\nProposed Changes:")
        output.append("-"*30)
        proposal = results.get("proposal", "")
        if isinstance(proposal, dict):
            proposal = proposal.get("proposal", "")
        output.append(str(proposal)[:500] + "..." if len(str(proposal)) > 500 else str(proposal))
        
        # Add only critical concerns from discussion
        if results.get("discussion_history"):
            output.append("\nKey Concerns:")
            output.append("-"*30)
            critical_concerns = []
            for entry in results["discussion_history"]:
                if isinstance(entry.get("content"), dict):
                    concerns = entry['content'].get('concerns', [])
                    critical_concerns.extend([
                        c.get('description', str(c)) for c in concerns
                        if isinstance(c, dict) and 
                        c.get('severity', '').lower() in ['high', 'critical']
                    ][:2])  # Only take top 2 concerns per expert
            output.append("\n".join(f"- {c}" for c in critical_concerns[:4]))  # Show max 4 total
        
        # Add only final validation decision
        if results.get("validation"):
            output.append("\nValidation:")
            output.append("-"*30)
            validation = str(results["validation"])
            if "APPROVED" in validation:
                output.append("APPROVED - " + validation.split("APPROVED")[1].split(".")[0])
            elif "REJECTED" in validation:
                output.append("REJECTED - " + validation.split("REJECTED")[1].split(".")[0])
            elif "NEEDS REVISION" in validation:
                output.append("NEEDS REVISION - " + validation.split("NEEDS REVISION")[1].split(".")[0])
        
        return "\n".join(output)
        
    except Exception as e:
        logging.error(f"Error formatting results: {str(e)}")
        return "Error formatting results for display"


def find_test_case_by_keyword(keyword: str) -> Optional[Dict[str, Any]]:
    """Find a test case by keyword in name or scenario."""
    keyword = keyword.lower()
    for case in ENHANCEMENT_TEST_CASES:
        if (keyword in case["name"].lower() or 
            keyword in case["trigger_scenario"].lower()):
            return case
    return None


def get_test_case_by_standard_id(standard_id: str) -> Optional[Dict[str, Any]]:
    """Get the first test case for a given standard ID."""
    for case in ENHANCEMENT_TEST_CASES:
        if case["standard_id"] == standard_id:
            return case
    return None


def write_results_to_file(results, standard_id):
    """Write enhancement results to a markdown file."""
    # filepath is the FAS+standard_id + timestamp 
    filepath = f"enhancement_results_FAS_{standard_id}_{int(time.time())}.md"
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            # Write header
            f.write(f"# Standards Enhancement Results - FAS {standard_id}\n\n")
            
            # Write scenario
            f.write("## Trigger Scenario\n\n")
            f.write(str(results.get("trigger_scenario", "")) + "\n\n")
            
            # Write initial analysis
            f.write("## Initial Analysis\n\n")
            f.write(str(results.get("review_analysis_summary", "")) + "\n\n")
            f.write("## Key Findings\n\n")
            
            # Handle reviewer_enhancement_areas - this is likely a list causing the error
            enhancement_areas = results.get('reviewer_enhancement_areas', "")
            if isinstance(enhancement_areas, list):
                # Convert list to formatted string
                enhancement_text = "\n".join(f"- {item}" for item in enhancement_areas)
                f.write(enhancement_text + "\n\n")
            else:
                f.write(str(enhancement_areas) + "\n\n")

            # Write full proposal
            f.write("## Enhancement Proposal\n\n")
            proposal = results.get("initial_proposal_structured", "")
            initial_proposal = ""
            final_proposal = ""
            if isinstance(proposal, dict):
                initial_proposal = proposal.get("initial_proposal_structured", "")
                final_proposal = proposal.get("final_proposal_structured", "")
            # Handle potential non-string types
            f.write(str(initial_proposal) + "\n\n")
            f.write(str(final_proposal) + "\n\n")

            # Write discussion history
            f.write("## Expert Discussion\n\n")
            if results.get("discussion_history"):
                for round_num, entries in _group_discussion_by_round(results["discussion_history"]):
                    f.write(f"### Round {round_num}\n\n")
                    for entry in entries:
                        expert = entry.get("agent", "Unknown Expert")
                        content = entry.get("content", {})
                        
                        f.write(f"#### {expert.title()} Expert\n\n")
                        
                        # Write analysis
                        if isinstance(content.get("analysis"), dict):
                            f.write("**Analysis:**\n\n")
                            f.write(str(content["analysis"].get("text", "")) + "\n\n")
                        
                        # Write concerns
                        if content.get("concerns"):
                            f.write("**Concerns:**\n\n")
                            for concern in content["concerns"]:
                                if isinstance(concern, dict):
                                    f.write(f"- {concern.get('description', str(concern))}\n")
                                else:
                                    f.write(f"- {str(concern)}\n")
                            f.write("\n")
                        
                        # Write recommendations
                        if content.get("recommendations"):
                            f.write("**Recommendations:**\n\n")
                            for rec in content["recommendations"]:
                                if isinstance(rec, dict):
                                    f.write(f"- {rec.get('description', str(rec))}\n")
                                else:
                                    f.write(f"- {str(rec)}\n")
                            f.write("\n")
            
            # Write validation result
            f.write("## Validation Result\n\n")
            if results.get("validation_summary"):
                f.write(str(results["validation_summary"]) + "\n\n")
            
            # Write cross-standard analysis if available
            if results.get("cross_standard_analysis_summary"):
                f.write("## Cross-Standard Impact Analysis\n\n")
                f.write(str(results["cross_standard_analysis_summary"]) + "\n\n")

        return filepath
    except Exception as e:
        logging.error(f"Error writing results to file: {str(e)}")
        # Return the error or handle it as appropriate for your application
        return None


def _group_discussion_by_round(discussion_history):
    """
    Group discussion entries by round number.
    Returns: List of tuples (round_num, [entries])
    """
    # Create dict to group entries by round
    rounds = {}
    for entry in discussion_history:
        round_num = entry.get("round", 0)
        if round_num not in rounds:
            rounds[round_num] = []
        rounds[round_num].append(entry)
    
    # Sort by round number and return
    return sorted(rounds.items())
def _group_discussion_by_round(history: List[Dict]) -> List[tuple]:
    """Group discussion entries by round number."""
    rounds = {}
    for entry in history:
        round_num = entry.get("round", 0)
        if round_num not in rounds:
            rounds[round_num] = []
        rounds[round_num].append(entry)
    
    return sorted(rounds.items())


def run_enhancement_demo():
    """Run an interactive demo of the Standards Enhancement feature."""
    print("Standards Enhancement Demo")
    print("=========================")
    print("Select a test case or enter your own:")
    
    # Show test cases
    for i, case in enumerate(ENHANCEMENT_TEST_CASES, 1):
        print(f"{i}. {case['name']} (FAS {case['standard_id']})")
    
    choice = input("\nChoice (or 'custom' for your own scenario): ")
    
    if choice.lower() == 'custom':
        standard_id = input("Enter standard ID (4, 7, 10, 28, or 32): ")
        trigger = input("Enter trigger scenario: ")
    else:
        try:
            case_idx = int(choice) - 1
            if case_idx < 0 or case_idx >= len(ENHANCEMENT_TEST_CASES):
                raise ValueError("Invalid index")
            
            case = ENHANCEMENT_TEST_CASES[case_idx]
            standard_id = case['standard_id']
            trigger = case['trigger_scenario']
        except:
            print("Invalid choice. Using default case.")
            standard_id = "10"
            trigger = ENHANCEMENT_TEST_CASES[0]['trigger_scenario']
    
    # Ask if cross-standard analysis should be included
    include_cross = input("Include cross-standard impact analysis? (y/n, default: y): ").lower()
    include_cross_analysis = False if include_cross == 'n' else True
    
    # Run enhancement
    result = run_standards_enhancement(standard_id, trigger, include_cross_standard_analysis=include_cross_analysis)
    
    # Write results to file
    output_file = write_results_to_file(result, standard_id)
    
    if output_file:
        print(f"\nEnhancement results have been written to: {output_file}")
    else:
        print("\nError: Could not write results to file")


def validate_committee_edits(
    standard_id: str,
    original_text: str,
    ai_proposed_text: str,
    committee_edited_text: str,
    previous_results: Dict[str, Any],
    progress_callback: Optional[Callable[[str, str], None]] = None
) -> Dict[str, Any]:
    """
    Validate committee-edited text against the original enhancement proposal.
    
    Args:
        standard_id: The ID of the standard (e.g., "10" for FAS 10)
        original_text: The original text from the standard
        ai_proposed_text: The text proposed by the AI enhancement process
        committee_edited_text: The edited text from the committee
        previous_results: The results from the previous enhancement process
        progress_callback: Optional callback function to report progress
        
    Returns:
        Dict with validation results
    """
    print(f"Validating committee edits for FAS {standard_id}...")
    
    # Report progress if callback provided
    if progress_callback:
        progress_callback("committee_validation_start", "Starting committee edit validation")
    
    # Extract trigger scenario from previous results
    trigger_scenario = previous_results.get("trigger_scenario", "")
    
    # Run validation using the committee validation agent
    from agents import committee_validator_agent
    
    validation_result = committee_validator_agent.validate_committee_edit(
        original_text=original_text,
        ai_proposed_text=ai_proposed_text,
        committee_edited_text=committee_edited_text,
        standard_id=standard_id,
        trigger_scenario=trigger_scenario,
        previous_analysis=previous_results
    )
    
    # Report progress if callback provided
    if progress_callback:
        progress_callback("committee_validation_complete", "Committee edit validation completed")
    
    # Add some additional context to the results
    validation_result["original_enhancement_results"] = previous_results
    
    return validation_result


if __name__ == "__main__":
    run_enhancement_demo()