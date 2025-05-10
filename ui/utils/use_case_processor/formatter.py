"""
Formatting utilities for display of accounting guidance.
"""

import re
from .table_converter import convert_tables_to_html


def format_content_for_display(accounting_guidance):
    """
    Formats the accounting guidance for better display including proper rendering of tables,
    formatting of headers, bullet points, and other markdown elements.
    
    Args:
        accounting_guidance: Raw accounting guidance text
        
    Returns:
        Formatted HTML for display
    """
    # CSS for styling
    css = """
    <style>
    .styled-table {
        border-collapse: collapse;
        margin: 25px 0;
        font-size: 14px;
        font-family: sans-serif;
        width: 100%;
        box-shadow: 0 0 20px rgba(0, 0, 0, 0.15);
    }
    .styled-table thead tr {
        background-color: #3b82f6;
        color: #ffffff;
        text-align: left;
    }
    .styled-table th,
    .styled-table td {
        padding: 12px 15px;
        border: 1px solid #e0e0e0;
        text-align: left;
    }
    .styled-table tbody tr {
        border-bottom: 1px solid #dddddd;
    }
    .styled-table tbody tr:nth-of-type(even) {
        background-color: #f9fafb;
    }
    .styled-table tbody tr:last-of-type {
        border-bottom: 2px solid #3b82f6;
    }
    .styled-table tbody tr:hover {
        background-color: #f0f9ff;
    }
    
    .summary-card {
        background-color: #f0f9ff;
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 30px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        border-left: 5px solid #3b82f6;
    }
    .summary-item {
        display: flex;
        margin-bottom: 15px;
        font-size: 16px;
        align-items: flex-start;
    }
    .summary-label {
        font-weight: bold;
        width: 200px;
        color: #1e3a8a;
        padding-right: 15px;
    }
    .summary-value {
        flex: 1;
    }
    .section-header {
        margin-top: 30px;
        margin-bottom: 15px;
        font-size: 24px;
        font-weight: bold;
        color: #1e3a8a;
        border-bottom: 2px solid #e0e0e0;
        padding-bottom: 8px;
    }
    
    /* Specific styling for calculation methodology */
    .calculation-item {
        margin-bottom: 10px;
        padding-left: 20px;
    }
    .calculation-item strong {
        color: #1e3a8a;
    }
    
    /* Notes and explanations */
    .note-text {
        font-style: italic;
        color: #4b5563;
        margin-top: 15px;
        padding: 10px;
        background-color: #f8fafc;
        border-left: 3px solid #94a3b8;
    }
    
    /* References styling */
    .reference-list {
        margin-top: 10px;
        margin-bottom: 20px;
    }
    .reference-item {
        display: flex;
        margin-bottom: 10px;
        padding: 8px;
        background-color: #f8fafc;
        border-radius: 5px;
        border-left: 3px solid #3b82f6;
    }
    .reference-standard {
        font-weight: bold;
        color: #1e3a8a;
        margin-right: 10px;
        min-width: 120px;
    }
    .reference-description {
        flex: 1;
    }
    </style>
    """
    
    # Process accounting guidance and format it
    formatted_content = accounting_guidance
    
    # Convert markdown tables to HTML tables
    # Look for table patterns
    formatted_content = convert_tables_to_html(formatted_content)
    
    # Format section headers
    formatted_content = re.sub(r'### ([^\n]+)', r'<div class="section-header">\1</div>', formatted_content)
    
    # Format bullet points
    formatted_content = re.sub(r'\* (.*?)(?=\n\*|\n\n|\Z)', r'<div class="calculation-item">• \1</div>', formatted_content, flags=re.DOTALL)
    
    # Format numbered lists
    formatted_content = re.sub(r'(\d+)\. (.*?)(?=\n\d+\.|\n\n|\Z)', r'<div class="calculation-item">\1. \2</div>', formatted_content, flags=re.DOTALL)
    
    # Format notes
    formatted_content = re.sub(r'\*Note: (.*?)\*', r'<div class="note-text">Note: \1</div>', formatted_content)
    
    # Format references section
    references_section = re.search(r'<div class="section-header">References</div>(.*?)(?=<div class="section-header">|$)', formatted_content, re.DOTALL)
    if references_section:
        ref_content = references_section.group(1)
        # Try multiple patterns to match references
        ref_items = re.findall(r'<div class="calculation-item">•\s+\*\*(.*?):\*\*\s+(.*?)</div>', ref_content, re.DOTALL)
        
        # If no matches with the first pattern, try alternative patterns
        if not ref_items:
            # Try to match pattern with bullet points but without bold markers
            ref_items = re.findall(r'<div class="calculation-item">•\s+(.*?):\s+(.*?)</div>', ref_content, re.DOTALL)
            
        # If still no matches, try parsing numbered references
        if not ref_items:
            # Try to match numbered list format
            numbered_items = re.findall(r'<div class="calculation-item">(\d+)\.\s+(.*?)</div>', ref_content, re.DOTALL)
            if numbered_items:
                ref_items = [(f"Reference {num}", desc) for num, desc in numbered_items]
        
        # Process raw bullet points if still no matches
        if not ref_items:
            # Try to match raw bullet points (not formatted yet)
            raw_items = re.findall(r'•\s+\*\*(.*?):\*\*\s+(.*?)(?=\n•|\Z)', ref_content, re.DOTALL)
            if raw_items:
                ref_items = raw_items
                
        # Handle the specific format in the example (FAS X, Para Y: Description)
        if not ref_items:
            fas_refs = re.findall(r'<div class="calculation-item">•\s+\*\*(FAS\s+\d+.*?):\*\*\s+(.*?)</div>', ref_content, re.DOTALL)
            if fas_refs:
                ref_items = fas_refs
                
        # Last fallback for any bullet points with content
        if not ref_items:
            basic_items = re.findall(r'<div class="calculation-item">•\s+(.*?)</div>', ref_content, re.DOTALL)
            if basic_items:
                # Try to split each item into a standard reference and description
                processed_items = []
                for item in basic_items:
                    # Check if the item contains a colon
                    if ":" in item:
                        parts = item.split(":", 1)
                        ref = parts[0].strip()
                        desc = parts[1].strip() if len(parts) > 1 else ""
                        processed_items.append((ref, desc))
                    else:
                        # Just use the whole item as the description
                        processed_items.append(("Reference", item.strip()))
                
                if processed_items:
                    ref_items = processed_items
        
        if ref_items:
            formatted_refs = '<div class="reference-list">'
            for ref, desc in ref_items:
                # Clean the text
                clean_ref = re.sub(r'<[^>]+>', '', ref).strip()
                clean_desc = re.sub(r'<[^>]+>', '', desc).strip()
                formatted_refs += f'<div class="reference-item"><div class="reference-standard">{clean_ref}</div><div class="reference-description">{clean_desc}</div></div>'
            formatted_refs += '</div>'
            
            # Replace the references section with our formatted version
            formatted_content = formatted_content.replace(ref_content, formatted_refs)
    
    # Add the CSS
    formatted_content = css + formatted_content
    
    return formatted_content