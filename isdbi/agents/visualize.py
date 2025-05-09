"""
Visualization Utilities for Standards Enhancement

This module contains functions to visualize the differences between
original standard text and proposed enhanced versions.
"""

import difflib
import re
from typing import Tuple


def extract_original_and_proposed(proposal_text: str) -> Tuple[str, str]:
    """
    Extract original text and proposed text from a proposal description.
    
    Args:
        proposal_text: Text containing both original and proposed sections
        
    Returns:
        Tuple of (original_text, proposed_text)
    """
    # Try to find sections labeled as original/existing and proposed/enhanced
    original_patterns = [
        r"Original text:(.*?)(?:Proposed text:|$)",
        r"Existing text:(.*?)(?:Proposed text:|$)",
        r"Current text:(.*?)(?:Proposed text:|$)",
        r"Original clause:(.*?)(?:Proposed clause:|$)",
        r"Original section:(.*?)(?:Proposed section:|$)"
    ]
    
    proposed_patterns = [
        r"Proposed text:(.*?)(?:Rationale:|$)",
        r"Enhanced text:(.*?)(?:Rationale:|$)",
        r"Modified text:(.*?)(?:Rationale:|$)",
        r"Proposed clause:(.*?)(?:Rationale:|$)",
        r"Proposed section:(.*?)(?:Rationale:|$)"
    ]
    
    # Try to extract original text
    original_text = ""
    for pattern in original_patterns:
        match = re.search(pattern, proposal_text, re.DOTALL | re.IGNORECASE)
        if match:
            original_text = match.group(1).strip()
            break
    
    # Try to extract proposed text
    proposed_text = ""
    for pattern in proposed_patterns:
        match = re.search(pattern, proposal_text, re.DOTALL | re.IGNORECASE)
        if match:
            proposed_text = match.group(1).strip()
            break
    
    return original_text, proposed_text


def generate_html_diff(original_text: str, proposed_text: str) -> str:
    """
    Generate an HTML visualization of the differences between original and proposed text.
    
    Args:
        original_text: The original standard text
        proposed_text: The proposed enhancement
        
    Returns:
        HTML string showing the differences
    """
    # Create a diff
    diff = difflib.HtmlDiff()
    html_diff = diff.make_file(
        original_text.splitlines(),
        proposed_text.splitlines(),
        fromdesc="Original Standard",
        todesc="Proposed Enhancement"
    )
    
    return html_diff


def save_html_diff(original_text: str, proposed_text: str, output_file: str):
    """
    Generate and save an HTML diff visualization to a file.
    
    Args:
        original_text: The original standard text
        proposed_text: The proposed enhancement
        output_file: Path to save the HTML file
    """
    html_diff = generate_html_diff(original_text, proposed_text)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_diff)
    
    print(f"HTML diff saved to {output_file}")


def format_text_diff(original_text: str, proposed_text: str) -> str:
    """
    Generate a text-based visualization of the differences.
    
    Args:
        original_text: The original standard text
        proposed_text: The proposed enhancement
        
    Returns:
        String representation of the differences
    """
    diff = difflib.unified_diff(
        original_text.splitlines(),
        proposed_text.splitlines(),
        lineterm='',
        fromfile='Original',
        tofile='Proposed'
    )
    
    return '\n'.join(diff)


def visualize_proposal(proposal_text: str, output_format: str = 'text', output_file: str = None) -> str:
    """
    Visualize the differences in a proposal.
    
    Args:
        proposal_text: Text containing both original and proposed sections
        output_format: Either 'text' or 'html'
        output_file: File to save HTML output (if format is 'html')
        
    Returns:
        String visualization or path to saved HTML file
    """
    original_text, proposed_text = extract_original_and_proposed(proposal_text)
    
    if not original_text or not proposed_text:
        return "Could not extract clear original and proposed text sections."
    
    if output_format == 'html':
        if output_file:
            save_html_diff(original_text, proposed_text, output_file)
            return f"HTML diff saved to {output_file}"
        else:
            return generate_html_diff(original_text, proposed_text)
    else:  # text format
        return format_text_diff(original_text, proposed_text)


if __name__ == "__main__":
    # Example of using the visualization
    sample_proposal = """
    Original text:
    The subject matter of the Istisna'a must be precisely specified in terms of its kind, type, quantity, and quality. It must be possible to exactly identify the object of sale when contracting to rule out significant gharar (uncertainty).
    
    Proposed text:
    The subject matter of the Istisna'a must be precisely specified in terms of its kind, type, quantity, and quality, with consideration for the nature of the asset. For tangible assets, full specifications must be provided. For intangible assets like software development, the subject matter may be defined through comprehensive functional requirements, milestones, and acceptance criteria that allow for appropriate measurement of completion while minimizing gharar (uncertainty).
    
    Rationale:
    This enhancement clarifies how the principle of "precise specification" applies differently to intangible assets like software, where complete upfront specification might not be practical but can be managed through defined milestones and acceptance criteria.
    """
    
    diff_result = visualize_proposal(sample_proposal)
    print(diff_result)
    
    # HTML example (commented out)
    # visualize_proposal(sample_proposal, 'html', 'sample_diff.html') 