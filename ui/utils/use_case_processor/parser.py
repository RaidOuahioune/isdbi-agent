"""
Parser functions for extracting structured information from accounting guidance.
"""

import re


def clean_guidance_text(accounting_guidance):
    """
    Clean up the accounting guidance text by removing content after the References section.
    
    Args:
        accounting_guidance: The raw accounting guidance text
        
    Returns:
        str: Cleaned guidance text without extra sections after References
    """
    clean_guidance = accounting_guidance
    
    # Find the References section
    references_end = re.search(r"(?:\#\#\#|\*\*) ?References(?:\#\#\#|\*\*)?\s*(.*?)(?=(?:\#\#\# |\*\*|\Z))", accounting_guidance, re.DOTALL | re.IGNORECASE)
    if references_end:
        # Find any content after References that looks like additional sections
        post_refs_section = re.search(r"(?:\#\#\#|\*\*) ?(?:Transaction Information|Extracted Financial Amount|\w+ Information).*?$", accounting_guidance, re.DOTALL | re.IGNORECASE)
        if post_refs_section:
            # Truncate the guidance at this point
            start_idx = post_refs_section.start()
            clean_guidance = accounting_guidance[:start_idx].strip()
    
    return clean_guidance


def extract_structured_guidance(accounting_guidance):
    """
    Extract structured information from the accounting guidance text.
    
    Args:
        accounting_guidance: The accounting guidance text from the agent
        
    Returns:
        dict: Structured information including product type, standards, etc.
    """
    # First, clean up the accounting guidance to remove anything after the references section
    clean_guidance = clean_guidance_text(accounting_guidance)
    
    result = {
        "product_type": "Islamic Financial Product",
        "applicable_standards": [],
        "method_used": "",
        "calculation_methodology": "",
        "journal_entries": "",
        "references": "",
        "summary": "",
    }
    
    # Extract summary section
    summary_match = re.search(r"(?:\#\#\#|\*\*) ?Summary(?:\#\#\#|\*\*)?\s*(.*?)(?=(?:\#\#\#|\*\*) (?!Summary)|$)", clean_guidance, re.DOTALL | re.IGNORECASE)
    if summary_match:
        result["summary"] = summary_match.group(1).strip()
    
    # Try to extract product type from summary section
    if result["summary"]:
        # Look for product type in bullet format: * **Islamic Financial Product Type:** Istisna'a
        product_match = re.search(r'\*\s+\*\*(?:Islamic Financial Product Type|Product Type|Product|Type)\*\*:\s*(.*?)(?=\n\*|\Z)', result["summary"], re.IGNORECASE | re.DOTALL)
        if product_match:
            result["product_type"] = product_match.group(1).strip()
    
    # Fallback to older pattern if not found in summary
    if result["product_type"] == "Islamic Financial Product":
        product_match = re.search(r"(?:\*\*)?(?:Islamic Financial Product Type|Product Type|Product|Type)(?:\*\*)?:?\s*(?:\*\*)?([^\n]+?)(?:\*\*)?(?:\n|$)", clean_guidance, re.IGNORECASE)
        if product_match:
            result["product_type"] = product_match.group(1).strip()
    
    # Try to extract standards from summary section
    if result["summary"]:
        # Look for standards in bullet format: * **Applicable AAOIFI Standard(s):** FAS 10
        standards_match = re.search(r'\*\s+\*\*(?:Applicable AAOIFI Standard\(s\)|Applicable Standards|Standards)\*\*:\s*(.*?)(?=\n\*|\Z)', result["summary"], re.IGNORECASE | re.DOTALL)
        if standards_match:
            standards_text = standards_match.group(1).strip()
            # Handle both comma-separated and parentheses format: FAS 10 (Istisna'a and Parallel Istisna'a)
            if ',' in standards_text:
                result["applicable_standards"] = [s.strip() for s in standards_text.split(',')]
            else:
                result["applicable_standards"] = [standards_text.strip()]
    
    # Fallback to older pattern if not found in summary
    if not result["applicable_standards"]:
        standards_match = re.search(r"(?:\*\*)?(?:Applicable AAOIFI Standard\(s\)|Applicable Standards|Standards)(?:\*\*)?:?\s*(?:\*\*)?([^\n]+?)(?:\*\*)?(?:\n|$)", clean_guidance, re.IGNORECASE)
        if standards_match:
            standards_text = standards_match.group(1).strip()
            result["applicable_standards"] = [s.strip() for s in standards_text.split(',')]
    
    # Try to extract method used from summary section
    if result["summary"]:
        # Look for method in bullet format: * **Method Used:** Percentage-of-Completion Method
        method_match = re.search(r'\*\s+\*\*(?:Method Used)\*\*:\s*(.*?)(?=\n\*|\Z)', result["summary"], re.IGNORECASE | re.DOTALL)
        if method_match:
            result["method_used"] = method_match.group(1).strip()
    
    # Fallback to older pattern if not found in summary
    if not result["method_used"]:
        method_match = re.search(r"(?:\*\*)?(?:Method Used)(?:\*\*)?:?\s*(?:\*\*)?([^\n]+?)(?:\*\*)?(?:\n|$)", clean_guidance, re.IGNORECASE)
        if method_match:
            result["method_used"] = method_match.group(1).strip()
    
    # If no standards found, look for FAS mentions
    if not result["applicable_standards"]:
        fas_matches = re.findall(r"FAS\s+(\d+)", clean_guidance)
        if fas_matches:
            # Remove duplicates and convert to set for uniqueness
            unique_fas = set(fas_matches)
            result["applicable_standards"] = [f"FAS {fas}" for fas in unique_fas]
    
    # Try to extract calculation methodology
    calc_section = re.search(r"(?:\#\#\#|\*\*) ?Calculation Methodology(?:\#\#\#|\*\*)?\s*(.*?)(?=(?:\#\#\#|\*\*) (?!Calculation)|$)", clean_guidance, re.DOTALL | re.IGNORECASE)
    if calc_section:
        result["calculation_methodology"] = calc_section.group(1).strip()
    
    # Try to extract journal entries
    journal_section = re.search(r"(?:\#\#\#|\*\*) ?Journal Entries(?:\#\#\#|\*\*)?\s*(.*?)(?=(?:\#\#\#|\*\*) (?!Journal)|$)", clean_guidance, re.DOTALL | re.IGNORECASE)
    if journal_section:
        result["journal_entries"] = journal_section.group(1).strip()
    
    # Try to extract references
    references_section = re.search(r"(?:\#\#\#|\*\*) ?References(?:\#\#\#|\*\*)?\s*(.*?)(?=(?:\#\#\#|\*\*)|$)", clean_guidance, re.DOTALL | re.IGNORECASE)
    if references_section:
        result["references"] = references_section.group(1).strip()
    
    return result