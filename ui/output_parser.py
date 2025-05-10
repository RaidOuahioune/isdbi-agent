import re
from typing import Tuple, Dict, Any
from ui.word_diff import generate_complete_diff

class OutputParser:
    """Parser for agent output files and enhancement results"""
    
    @staticmethod
    def parse_markdown_sections(output_text):
        """Parse markdown text into sections using regex"""
        # Dictionary to store section content
        sections = {}
        
        # Extract standard ID
        standard_id_match = re.search(r'Standards Enhancement Results for FAS (\d+)', output_text)
        if standard_id_match:
            sections["standard_id"] = standard_id_match.group(1)
        else:
            sections["standard_id"] = "Unknown"
            
        # Extract all major sections using regex patterns
        section_patterns = {
            "trigger_scenario": r'## Trigger Scenario\n(.*?)(?=\n## |\Z)',
            "review": r'## Review Findings\n(.*?)(?=\n## |\Z)',
            "proposal": r'## Proposed Enhancements\n(.*?)(?=\n## |\Z)',
            "validation": r'## Validation Results\n(.*?)(?=\n## |\Z)',
            "cross_standard_analysis": r'## Cross-Standard Impact Analysis\n(.*?)(?=\n## |\Z)'
        }
        
        for section_name, pattern in section_patterns.items():
            match = re.search(pattern, output_text, re.DOTALL)
            if match:
                sections[section_name] = match.group(1).strip()
            else:
                # Only include section if found in the document
                if section_name != "cross_standard_analysis":  # This is optional
                    sections[section_name] = f"Section '{section_name}' not found in the output"
                
        # If regex approach fails for any section, try alternative parsing
        if any(v.startswith("Section '") for k, v in sections.items() if k != "standard_id" and k != "cross_standard_analysis"):
            return OutputParser.parse_markdown_sections_fallback(output_text)
                
        return sections
    
    @staticmethod
    def parse_markdown_sections_fallback(output_text):
        """Fallback method to parse markdown text into sections using string splitting"""
        sections = {"standard_id": "Unknown"}
        
        # Extract standard ID
        standard_id_match = re.search(r'Standards Enhancement Results for FAS (\d+)', output_text)
        if standard_id_match:
            sections["standard_id"] = standard_id_match.group(1)
        
        # Remove the title line if present
        if output_text.startswith("# Standards Enhancement Results"):
            lines = output_text.split("\n")
            if len(lines) > 1:
                output_text = "\n".join(lines[1:]).strip()
                
        # Split by section headers and process each section
        parts = re.split(r'## (.*?)\n', output_text)
        
        # First part is empty or contains content before the first header
        if parts and len(parts) > 1:
            # Parts will be [content_before_first_header, header1, content1, header2, content2, ...]
            for i in range(1, len(parts), 2):
                if i + 1 < len(parts):
                    header = parts[i].lower().strip()
                    content = parts[i+1].strip()
                    
                    if "trigger" in header or "scenario" in header:
                        sections["trigger_scenario"] = content
                    elif "review" in header or "findings" in header:
                        sections["review"] = content
                    elif "propos" in header or "enhancement" in header:
                        sections["proposal"] = content
                    elif "valid" in header or "result" in header:
                        sections["validation"] = content
                    elif "cross" in header or "impact" in header:
                        sections["cross_standard_analysis"] = content
        
        # Ensure all required sections exist
        required_sections = ["trigger_scenario", "review", "proposal", "validation"]
        for section in required_sections:
            if section not in sections:
                sections[section] = f"Section '{section}' not found in the output"
                
        return sections
    
    @staticmethod
    def extract_original_and_proposed(proposal_text: str) -> Tuple[str, str]:
        """
        Extract original text and proposed text from a proposal description.
        
        Args:
            proposal_text: Text containing both original and proposed sections
            
        Returns:
            Tuple of (original_text, proposed_text)
        """
        # Return early if the proposal text is empty or None
        if not proposal_text:
            return "", ""
        
        # Extract proposals that follow the standardized format
        original_text = ""
        proposed_text = ""
        
        # Check for our standardized format first (highest priority)
        orig_pattern = r"## Original Text\s*\n\*\*Original Text:\*\*\s*(.*?)(?=##|\Z)"
        prop_pattern = r"## Proposed Modified Text\s*\n\*\*Proposed Modified Text:\*\*\s*(.*?)(?=##|\Z)"
        
        orig_match = re.search(orig_pattern, proposal_text, re.DOTALL)
        prop_match = re.search(prop_pattern, proposal_text, re.DOTALL)
        
        if orig_match and prop_match:
            original_text = orig_match.group(1).strip()
            proposed_text = prop_match.group(1).strip()
            return original_text, proposed_text
        
        # Backup patterns for the markdown header format
        orig_pattern2 = r"\*\*Original Text:\*\*\s*(.*?)(?=\*\*Proposed|##|\Z)"
        prop_pattern2 = r"\*\*Proposed Modified Text:\*\*\s*(.*?)(?=##|\*\*Rationale|\Z)"
        
        orig_match = re.search(orig_pattern2, proposal_text, re.DOTALL)
        prop_match = re.search(prop_pattern2, proposal_text, re.DOTALL)
        
        if orig_match and prop_match:
            original_text = orig_match.group(1).strip()
            proposed_text = prop_match.group(1).strip()
            return original_text, proposed_text
        
        # Find proposals with numbered format
        proposals = re.findall(r'(?:Proposal|Enhancement) (?:\d+):(.*?)(?=(?:Proposal|Enhancement) (?:\d+):|$)', 
                              proposal_text, re.DOTALL | re.IGNORECASE)
        
        if proposals:
            # Try to find Original Text and Proposed Modified Text in the proposals
            for proposal in proposals:
                # Try the standardized format first
                orig_match = re.search(r'## Original Text\s*\n\*\*Original Text:\*\*\s*(.*?)(?=##|\Z)', proposal, re.DOTALL)
                prop_match = re.search(r'## Proposed Modified Text\s*\n\*\*Proposed Modified Text:\*\*\s*(.*?)(?=##|\Z)', proposal, re.DOTALL)
                
                if orig_match and prop_match:
                    original_text = orig_match.group(1).strip()
                    proposed_text = prop_match.group(1).strip()
                    return original_text, proposed_text
                
                # Try the simpler format
                orig_match = re.search(r'\*\*Original Text:\*\*\s*(.*?)(?=\*\*Proposed|##|\Z)', proposal, re.DOTALL)
                prop_match = re.search(r'\*\*Proposed Modified Text:\*\*\s*(.*?)(?=##|\*\*Rationale|\Z)', proposal, re.DOTALL)
                
                if orig_match and prop_match:
                    original_text = orig_match.group(1).strip()
                    proposed_text = prop_match.group(1).strip()
                    return original_text, proposed_text
        
        # If we haven't found original and proposed text, try other patterns
        if not original_text or not proposed_text:
            # Try to find sections labeled as original/existing and proposed/enhanced
            original_patterns = [
                # Standard patterns
                r"Original text:(.*?)(?:Proposed text:|$)",
                r"Existing text:(.*?)(?:Proposed text:|$)",
                r"Current text:(.*?)(?:Proposed text:|$)",
                r"Original clause:(.*?)(?:Proposed clause:|$)",
                r"Original section:(.*?)(?:Proposed section:|$)",
                r"Original Text:(.*?)(?:Proposed Text:|Proposed Modified Text:|$)",
                # Section-specific patterns
                r"Original Text \(.*?\):(.*?)(?:Proposed|$)",
                r"\*\*Original Text\*\*\s*(?:\(.*?\))?\s*:(.*?)(?:\*\*Proposed|$)",
                r"\*\*Original Text\*\*\s*(?:\(.*?\))?\s*(.*?)(?:\*\*Proposed|$)",
                r"> 3/1/1 (.*?)(?:>|Proposed|$)",
                r">\s*3/1/1(.*?)(?:>|Proposed|$)",
                r">\s*3/2/1(.*?)(?:>|Proposed|$)",
                r">\s*2/2/1(.*?)(?:>|Proposed|$)",
            ]
            
            proposed_patterns = [
                # Standard patterns
                r"Proposed text:(.*?)(?:Rationale:|$)",
                r"Enhanced text:(.*?)(?:Rationale:|$)",
                r"Modified text:(.*?)(?:Rationale:|$)",
                r"Proposed clause:(.*?)(?:Rationale:|$)",
                r"Proposed section:(.*?)(?:Rationale:|$)",
                r"Proposed Text:(.*?)(?:Rationale:|$)",
                r"Proposed Modified Text:(.*?)(?:Rationale:|$)",
                # Section-specific patterns
                r"Proposed Modified Text \(.*?\):(.*?)(?:Rationale:|$)",
                r"\*\*Proposed (?:Modified )?Text\*\*\s*(?:\(.*?\))?\s*:(.*?)(?:\*\*Rationale|$)",
                r"\*\*Proposed (?:Modified )?Text\*\*\s*(?:\(.*?\))?\s*(.*?)(?:\*\*Rationale|$)",
                r"> 3/1/1 An Istisna'a contract is permissible for the creation(.*?)(?:Rationale:|$)",
                r">\s*Modify 3/1/1:(.*?)(?:Modify|$)",
                r">\s*Modify 3/2/1:(.*?)(?:Modify|$)",
                r">\s*Modify 2/2/1:(.*?)(?:Modify|$)",
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
                    
            # Additional processing if we have multiline proposals with numbering
            if not original_text or not proposed_text:
                # Look for proposals with "Enhancement Proposal 1:" style headers
                proposals = re.findall(r'(?:Enhancement|Proposal) (?:Proposal )?\d+:(.*?)(?=(?:Enhancement|Proposal) (?:Proposal )?\d+:|$)', 
                                     proposal_text, re.DOTALL | re.IGNORECASE)
                
                if proposals:
                    # Try finding original and proposed text in each proposal
                    for proposal in proposals:
                        orig = ""
                        prop = ""
                        
                        # Try all patterns on this specific proposal
                        for pattern in original_patterns:
                            match = re.search(pattern, proposal, re.DOTALL | re.IGNORECASE)
                            if match:
                                orig = match.group(1).strip()
                                break
                                
                        for pattern in proposed_patterns:
                            match = re.search(pattern, proposal, re.DOTALL | re.IGNORECASE)
                            if match:
                                prop = match.group(1).strip()
                                break
                                
                        if orig and prop:
                            original_text = orig
                            proposed_text = prop
                            break
        
        # If still not found, look for markdown quote blocks (often used in proposals)
        if not original_text or not proposed_text:
            # Find text between markdown quote indicators (>)
            quote_blocks = re.findall(r'>\s*(.*?)(?=\n[^>]|\Z)', proposal_text, re.DOTALL)
            
            if len(quote_blocks) >= 2:
                # Assume first quote block is original, second is proposed
                original_text = quote_blocks[0].strip()
                proposed_text = quote_blocks[1].strip()
            
            # Alternatively, check for code blocks (```)
            if not original_text or not proposed_text:
                code_blocks = re.findall(r'```(?:\w+)?\n(.*?)```', proposal_text, re.DOTALL)
                if len(code_blocks) >= 2:
                    original_text = code_blocks[0].strip()
                    proposed_text = code_blocks[1].strip()
        
        # Last resort: try to extract from "Original" and "Proposed" keywords
        if not original_text or not proposed_text:
            # Look for paragraphs or sections that begin with keywords
            paragraphs = re.split(r'\n\s*\n', proposal_text)
            
            for paragraph in paragraphs:
                if re.match(r'(?:Original|Current|Existing)', paragraph, re.IGNORECASE) and not original_text:
                    # Extract text after first colon or first line
                    colon_match = re.search(r':(.*)', paragraph, re.DOTALL)
                    if colon_match:
                        original_text = colon_match.group(1).strip()
                    else:
                        lines = paragraph.split('\n')
                        if len(lines) > 1:
                            original_text = '\n'.join(lines[1:]).strip()
                            
                if re.match(r'(?:Proposed|Enhanced|Modified)', paragraph, re.IGNORECASE) and not proposed_text:
                    # Extract text after first colon or first line
                    colon_match = re.search(r':(.*)', paragraph, re.DOTALL)
                    if colon_match:
                        proposed_text = colon_match.group(1).strip()
                    else:
                        lines = paragraph.split('\n')
                        if len(lines) > 1:
                            proposed_text = '\n'.join(lines[1:]).strip()
        
        # Super fallback: If no extraction worked, log the issue and provide empty strings
        if not original_text and not proposed_text and proposal_text:
            print("WARNING: Could not extract original and proposed text from proposal")
            print(f"First 200 chars of proposal: {proposal_text[:200]}...")
            
            # As absolute last resort, try to split the proposal in half
            if len(proposal_text) > 200:  # Only for reasonably long texts
                middle = len(proposal_text) // 2
                # Try to find a paragraph break near the middle
                paragraph_breaks = [m.start() for m in re.finditer(r'\n\s*\n', proposal_text)]
                if paragraph_breaks:
                    # Find the break closest to the middle
                    middle = min(paragraph_breaks, key=lambda x: abs(x - middle))
                
                original_text = proposal_text[:middle].strip()
                proposed_text = proposal_text[middle:].strip()
                
                # Add a note so users know this is a fallback 
                original_text = "EXTRACTION FALLBACK (may not be accurate):\n\n" + original_text
                proposed_text = "EXTRACTION FALLBACK (may not be accurate):\n\n" + proposed_text
        
        return original_text, proposed_text

    @staticmethod
    def format_text_diff(original_text: str, proposed_text: str) -> str:
        """
        Generate a simple diff between original and proposed text.
        
        Args:
            original_text: The original standard text
            proposed_text: The proposed enhancement
            
        Returns:
            String representation of the differences
        """
        if not original_text or not proposed_text:
            return ""
            
        diff_lines = []
        
        # Add a simple diff header
        diff_lines.append("--- Original")
        diff_lines.append("+++ Proposed")
        diff_lines.append("@@ -1,1 +1,1 @@")
        
        # Add the original text with minus signs
        for line in original_text.split('\n'):
            diff_lines.append(f"- {line}")
        
        # Add the proposed text with plus signs
        for line in proposed_text.split('\n'):
            diff_lines.append(f"+ {line}")
            
        return "\n".join(diff_lines)
    
    @staticmethod
    def format_diff_html(diff_text: str) -> str:
        """
        Convert a simple diff format to HTML for display.
        
        Args:
            diff_text: Text in diff format with +/- signs
            
        Returns:
            HTML formatted diff
        """
        if not diff_text:
            return ""
            
        html_lines = []
        
        for line in diff_text.split('\n'):
            if line.startswith('---') or line.startswith('+++') or line.startswith('@@'):
                html_lines.append(f"<div class='diff-header'>{line}</div>")
            elif line.startswith('- '):
                html_lines.append(f"<div class='deletion'>{line[2:]}</div>")
            elif line.startswith('+ '):
                html_lines.append(f"<div class='addition'>{line[2:]}</div>")
            else:
                html_lines.append(f"<div>{line}</div>")
                
        return "\n".join(html_lines)
    
    @staticmethod
    def generate_enhanced_diff(original_text: str, proposed_text: str) -> Dict[str, Any]:
        """
        Generate enhanced diff between original and proposed text using the word_diff module.
        
        Args:
            original_text: The original standard text
            proposed_text: The proposed enhancement
            
        Returns:
            Dictionary with different diff formats and analysis
        """
        # Handle None values
        if original_text is None:
            original_text = ""
        if proposed_text is None:
            proposed_text = ""
            
        # Log warning if texts are empty
        if not original_text or not proposed_text:
            print("WARNING: Empty text provided for diff generation")
            print(f"Original text length: {len(original_text)}")
            print(f"Proposed text length: {len(proposed_text)}")
            
            # Return a minimal result if either text is empty
            if not original_text and not proposed_text:
                return {
                    "word_diff_html": "<div class='diff-warning'>No text available for comparison</div>",
                    "inline_diff_html": "<div class='diff-warning'>No text available for comparison</div>",
                    "sentence_diff_html": "<div class='diff-warning'>No text available for comparison</div>",
                    "stats": {
                        "words_added": 0,
                        "words_deleted": 0,
                        "words_unchanged": 0,
                        "total_words_original": 0,
                        "total_words_proposed": 0,
                        "percent_changed": 0
                    },
                    "change_summary": "No text available for comparison"
                }
            
        # Try to import word_diff, fall back to simple diff if not available
        try:
            # Call the generate_complete_diff from the word_diff module
            diff_result = generate_complete_diff(original_text, proposed_text)
            return diff_result
        except ImportError:
            print("WARNING: word_diff module not available, falling back to simple diff")
            # Create a simplified diff result with basic HTML
            simple_diff = OutputParser.format_text_diff(original_text, proposed_text)
            simple_diff_html = OutputParser.format_diff_html(simple_diff)
            
            # Count words as basic stats
            original_words = len(re.findall(r'\w+', original_text))
            proposed_words = len(re.findall(r'\w+', proposed_text))
            
            return {
                "word_diff_html": simple_diff_html,
                "inline_diff_html": simple_diff_html,
                "sentence_diff_html": simple_diff_html,
                "stats": {
                    "words_added": max(0, proposed_words - original_words),
                    "words_deleted": max(0, original_words - proposed_words),
                    "words_unchanged": min(original_words, proposed_words),
                    "total_words_original": original_words,
                    "total_words_proposed": proposed_words,
                    "percent_changed": 100 if original_words == 0 else abs(proposed_words - original_words) / original_words * 100
                },
                "change_summary": "Basic comparison (word_diff module not available)"
            }
        except Exception as e:
            print(f"ERROR generating diff: {e}")
            # Return a minimal result with the error message
            return {
                "word_diff_html": f"<div class='diff-error'>Error generating diff: {e}</div>",
                "inline_diff_html": f"<div class='diff-error'>Error generating diff: {e}</div>",
                "sentence_diff_html": f"<div class='diff-error'>Error generating diff: {e}</div>",
                "stats": {
                    "words_added": 0,
                    "words_deleted": 0,
                    "words_unchanged": 0,
                    "total_words_original": len(re.findall(r'\w+', original_text)) if original_text else 0,
                    "total_words_proposed": len(re.findall(r'\w+', proposed_text)) if proposed_text else 0,
                    "percent_changed": 0
                },
                "change_summary": f"Error: {e}"
            }
    
    @staticmethod
    def parse_results_from_agents(results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse the results from the agents into a structure suitable for display.
        
        Args:
            results: The raw results from the enhancement process
            
        Returns:
            Dictionary with structured sections
        """
        try:
            # Extract key pieces, providing defaults for missing values
            standard_id = results.get("standard_id", "Unknown")
            trigger_scenario = results.get("trigger_scenario", "")
            review = results.get("review", "")
            proposal = results.get("proposal", "")
            validation = results.get("validation", "")
            cross_standard_analysis = results.get("cross_standard_analysis", "")
            
            # Check for missing critical values and add warnings
            missing_sections = []
            if not trigger_scenario:
                missing_sections.append("trigger_scenario")
            if not review:
                missing_sections.append("review")
            if not proposal:
                missing_sections.append("proposal")
            if not validation:
                missing_sections.append("validation")
                
            if missing_sections:
                warning = f"WARNING: Missing content for: {', '.join(missing_sections)}"
                print(warning)
            
            # Extract original and proposed text, using cache if available
            if "original_text" in results and "proposed_text" in results:
                original_text = results.get("original_text", "")
                proposed_text = results.get("proposed_text", "")
            else:
                original_text, proposed_text = OutputParser.extract_original_and_proposed(proposal)
                # Store extracted text back in results for future use
                results["original_text"] = original_text
                results["proposed_text"] = proposed_text
            
            # Generate both simple and enhanced diffs if not already present
            if "simple_diff" not in results or "simple_diff_html" not in results:
                simple_diff = OutputParser.format_text_diff(original_text, proposed_text)
                simple_diff_html = OutputParser.format_diff_html(simple_diff)
                results["simple_diff"] = simple_diff
                results["simple_diff_html"] = simple_diff_html
            
            # Generate enhanced diff if not already present
            if "enhanced_diff" not in results:
                enhanced_diff = OutputParser.generate_enhanced_diff(original_text, proposed_text)
                results["enhanced_diff"] = enhanced_diff
            
            # Process compatibility matrix if present
            if "compatibility_matrix" in results:
                # Make sure the compatibility matrix is in the right format 
                matrix = results["compatibility_matrix"]
                # Convert string JSON to actual data if needed
                if isinstance(matrix, str):
                    try:
                        import json
                        matrix = json.loads(matrix) 
                        results["compatibility_matrix"] = matrix
                    except:
                        print("Warning: Could not parse compatibility matrix JSON")
                
                # Ensure it's a list
                if not isinstance(matrix, list):
                    print(f"Warning: Compatibility matrix is not a list: {type(matrix)}")
                    # Create a default one
                    results["compatibility_matrix"] = [
                        {"standard_id": "4", "impact_level": "Unknown", "impact_type": "Unknown"},
                        {"standard_id": "7", "impact_level": "Unknown", "impact_type": "Unknown"},
                        {"standard_id": "10", "impact_level": "Unknown", "impact_type": "Unknown"},
                        {"standard_id": "28", "impact_level": "Unknown", "impact_type": "Unknown"},
                        {"standard_id": "32", "impact_level": "Unknown", "impact_type": "Unknown"}
                    ]
            
            # Add cross-standard analysis if present
            if cross_standard_analysis:
                results["cross_standard_analysis"] = cross_standard_analysis
                
            return results
        except Exception as e:
            # If parsing fails, return a minimal but valid structure with the error
            print(f"ERROR parsing results: {e}")
            return {
                "standard_id": results.get("standard_id", "Unknown"),
                "trigger_scenario": results.get("trigger_scenario", ""),
                "review": results.get("review", f"Error parsing results: {e}"),
                "proposal": results.get("proposal", ""),
                "validation": results.get("validation", ""),
                "original_text": results.get("original_text", ""),
                "proposed_text": results.get("proposed_text", ""),
                "simple_diff": "",
                "simple_diff_html": f"<div class='diff-error'>Error generating diff: {e}</div>",
                "enhanced_diff": {
                    "word_diff_html": f"<div class='diff-error'>Error generating diff: {e}</div>",
                    "stats": {
                        "words_added": 0,
                        "words_deleted": 0,
                        "words_unchanged": 0,
                        "total_words_original": 0,
                        "total_words_proposed": 0,
                        "percent_changed": 0
                    },
                    "change_summary": f"Error: {e}"
                }
            } 