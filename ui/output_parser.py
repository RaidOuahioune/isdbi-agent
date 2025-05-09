import re
from typing import Tuple, Dict, Any

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
            "validation": r'## Validation Results\n(.*?)(?=\n## |\Z)'
        }
        
        for section_name, pattern in section_patterns.items():
            match = re.search(pattern, output_text, re.DOTALL)
            if match:
                sections[section_name] = match.group(1).strip()
            else:
                sections[section_name] = f"Section '{section_name}' not found in the output"
                
        # If regex approach fails for any section, try alternative parsing
        if any(v.startswith("Section '") for k, v in sections.items() if k != "standard_id"):
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
        # Try to find sections labeled as original/existing and proposed/enhanced
        original_patterns = [
            r"Original text:(.*?)(?:Proposed text:|$)",
            r"Existing text:(.*?)(?:Proposed text:|$)",
            r"Current text:(.*?)(?:Proposed text:|$)",
            r"Original clause:(.*?)(?:Proposed clause:|$)",
            r"Original section:(.*?)(?:Proposed section:|$)",
            r"Original Text:(.*?)(?:Proposed Text:|$)",
            r"Original Modified Text \(3/1/1\):(.*?)(?:Proposed|$)",
            r"> 3/1/1 (.*?)(?:Proposed|$)",
            r">\s*3/1/1(.*?)(?:>|$)",
            r">\s*3/2/1(.*?)(?:>|$)",
            r">\s*2/2/1(.*?)(?:>|$)"
        ]
        
        proposed_patterns = [
            r"Proposed text:(.*?)(?:Rationale:|$)",
            r"Enhanced text:(.*?)(?:Rationale:|$)",
            r"Modified text:(.*?)(?:Rationale:|$)",
            r"Proposed clause:(.*?)(?:Rationale:|$)",
            r"Proposed section:(.*?)(?:Rationale:|$)",
            r"Proposed Text:(.*?)(?:Rationale:|$)",
            r"Proposed Modified Text \(3/1/1\):(.*?)(?:Rationale:|$)",
            r"> 3/1/1 An Istisna'a contract is permissible for the creation(.*?)(?:Rationale:|$)",
            r">\s*Modify 3/1/1:(.*?)(?:Modify|$)",
            r">\s*Modify 3/2/1:(.*?)(?:Modify|$)",
            r">\s*Modify 2/2/1:(.*?)(?:Modify|$)"
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
            proposals = re.findall(r'Enhancement Proposal \d+:(.*?)(?=Enhancement Proposal \d+:|$)', 
                                 proposal_text, re.DOTALL)
            
            if proposals:
                # For the first proposal, try to find original and proposed text
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
        
        return '\n'.join(diff_lines)
        
    @staticmethod
    def format_diff_html(diff_text: str) -> str:
        """
        Format diff text with HTML styling for better display.
        
        Args:
            diff_text: Text containing the diff
            
        Returns:
            HTML-formatted diff for display
        """
        if not diff_text:
            return "No diff available"
        
        html = []
        for line in diff_text.split('\n'):
            if line.startswith('+'):
                html.append(f'<div class="addition">{line}</div>')
            elif line.startswith('-'):
                html.append(f'<div class="deletion">{line}</div>')
            else:
                html.append(f'<div>{line}</div>')
        
        return ''.join(html)
    
    @staticmethod
    def parse_results_from_agents(results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse results directly from the agents output.
        
        Args:
            results: The raw results dictionary from run_standards_enhancement
            
        Returns:
            Dict with properly parsed sections
        """
        # First format the results as markdown
        # This typically comes from enhancement.format_results_for_display
        output = []
        
        # Header information
        output.append(f"# Standards Enhancement Results for FAS {results['standard_id']}")
        output.append("\n## Trigger Scenario")
        output.append(results['trigger_scenario'])
        
        # Review findings
        output.append("\n## Review Findings")
        output.append(results['review'])
        
        # Proposed enhancements
        output.append("\n## Proposed Enhancements")
        output.append(results['proposal'])
        
        # Validation results
        output.append("\n## Validation Results")
        output.append(results['validation'])
        
        formatted_output = "\n".join(output)
        
        # Now parse the formatted output
        return OutputParser.parse_markdown_sections(formatted_output) 