"""
HTML rendering utilities for displaying accounting guidance summaries and components.
"""

import re


def render_summary_card(summary_data):
    """
    Render a styled summary card with the summary information.
    
    Args:
        summary_data: Dictionary with summary information
        
    Returns:
        HTML string with formatted summary card
    """
    html = "<div class='summary-card'>"
    
    # Add standard summary items
    if summary_data.get("product_type"):
        # Clean the product type value to ensure it doesn't contain HTML tags
        product_type = summary_data["product_type"]
        # Remove any HTML tags that might be present
        product_type = re.sub(r'<[^>]+>', '', product_type)
        # Strip any extra whitespace
        product_type = product_type.strip()
        
        html += f"""
        <div class='summary-item'>
            <div class='summary-label'>Product Type:</div>
            <div class='summary-value'>{product_type}</div>
        </div>
        """
    
    if summary_data.get("applicable_standards"):
        # Clean and join the standards list
        standards = summary_data["applicable_standards"]
        standards_str = ", ".join([re.sub(r'<[^>]+>', '', std).strip() for std in standards])
        
        html += f"""
        <div class='summary-item'>
            <div class='summary-label'>Applicable Standards:</div>
            <div class='summary-value'>{standards_str}</div>
        </div>
        """
    
    if summary_data.get("method_used"):
        # Clean the method used value
        method_used = re.sub(r'<[^>]+>', '', summary_data["method_used"]).strip()
        
        html += f"""
        <div class='summary-item'>
            <div class='summary-label'>Method Used:</div>
            <div class='summary-value'>{method_used}</div>
        </div>
        """
    
    # Look for additional summary items from the summary section
    if summary_data.get("summary"):
        # Get the raw summary text and process it
        summary_text = summary_data["summary"]
        
        # First try the bullet point format with * and ** markers
        bullet_points = re.findall(r'\*\s+\*\*(.*?):\*\*\s*(.*?)(?=\n\*|\Z)', summary_text, re.DOTALL)
        
        # If no bullet points found, try alternative pattern
        if not bullet_points:
            bullet_points = re.findall(r'\*\s+(.*?):\s*(.*?)(?=\n\*|\Z)', summary_text, re.DOTALL)
        
        for label, value in bullet_points:
            # Clean the label and value
            clean_label = re.sub(r'<[^>]+>', '', label).strip()
            clean_value = re.sub(r'<[^>]+>', '', value).strip()
            
            # Skip items already included
            if clean_label.lower() not in ["islamic financial product type", "product type", "applicable aaoifi standard(s)", "applicable standards", "method used"]:
                clean_value = clean_value.replace('\n', '<br>')
                html += f"""
                <div class='summary-item'>
                    <div class='summary-label'>{clean_label}:</div>
                    <div class='summary-value'>{clean_value}</div>
                </div>
                """
    
    html += "</div>"
    return html