import sys
import os
from pathlib import Path

# Add the parent directory to the path so we can import from the main project
parent_dir = str(Path(__file__).parent)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from ui.output_parser import OutputParser

def test_extract_original_and_proposed():
    """Test the extract_original_and_proposed method with the challenge3_output.txt file."""
    # Path to the challenge3 output file
    file_path = os.path.join(parent_dir, "documentation", "agent_outputs_text_files", "challenge3_output.txt")
    
    # Read the file
    with open(file_path, "r") as f:
        output_text = f.read()
    
    # Parse the sections
    sections = OutputParser.parse_markdown_sections(output_text)
    
    # Extract the proposal section
    proposal_text = sections.get("proposal", "")
    
    # Extract original and proposed text
    original_text, proposed_text = OutputParser.extract_original_and_proposed(proposal_text)
    
    # Print the results
    print("ORIGINAL TEXT LENGTH:", len(original_text))
    print("PROPOSED TEXT LENGTH:", len(proposed_text))
    
    print("\nORIGINAL TEXT (first 200 chars):")
    print(original_text[:200])
    
    print("\nPROPOSED TEXT (first 200 chars):")
    print(proposed_text[:200])
    
    # Generate diff and verify results 
    enhanced_diff = OutputParser.generate_enhanced_diff(original_text, proposed_text)
    
    # Print diff stats
    if "stats" in enhanced_diff:
        stats = enhanced_diff["stats"]
        print("\nDIFF STATS:")
        print(f"Words Added: {stats['words_added']}")
        print(f"Words Deleted: {stats['words_deleted']}")
        print(f"Words Unchanged: {stats['words_unchanged']}")
        print(f"Total Words Original: {stats['total_words_original']}")
        print(f"Total Words Proposed: {stats['total_words_proposed']}")
        print(f"Percent Changed: {stats['percent_changed']:.2f}%")
    
    # Return results for further analysis if needed
    return {
        "original_text": original_text,
        "proposed_text": proposed_text,
        "enhanced_diff": enhanced_diff
    }

if __name__ == "__main__":
    test_extract_original_and_proposed() 