"""
Table conversion utilities for formatting markdown tables to HTML.
"""

import re


def convert_tables_to_html(text):
    """
    Converts markdown tables to HTML tables with proper styling.
    
    Args:
        text: Text containing markdown tables
        
    Returns:
        Text with markdown tables replaced by HTML tables
    """
    # Function to process a single table
    def process_table(table_match):
        lines = table_match.strip().split('\n')
        
        # Find the separator row which has dashes
        separator_row_idx = -1
        for i, line in enumerate(lines):
            if '|' in line and re.search(r'\|[\s\-:]+\|', line):
                separator_row_idx = i
                break
        
        if separator_row_idx == -1 or separator_row_idx == 0:
            # No valid separator row found or it's the first row
            return table_match
        
        # The header row is the one before the separator
        header_row = lines[separator_row_idx - 1]
        data_rows = lines[separator_row_idx + 1:]
        
        # Start building the HTML table
        html = '<table class="styled-table"><thead><tr>'
        
        # Process header cells
        header_cells = [cell.strip() for cell in header_row.split('|')[1:-1]]  # Skip first and last empty cells
        for cell in header_cells:
            html += f'<th>{cell}</th>'
        
        html += '</tr></thead><tbody>'
        
        # Process data rows
        for row in data_rows:
            if '|' not in row:
                continue
            
            cells = [cell.strip() for cell in row.split('|')[1:-1]]  # Skip first and last empty cells
            
            # Skip empty rows or rows that are just explanatory text
            if not cells or all(not cell for cell in cells):
                continue
                
            html += '<tr>'
            for cell in cells:
                # Handle markdown formatting in cell content
                cell = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', cell)
                cell = re.sub(r'\*(.*?)\*', r'<em>\1</em>', cell)
                html += f'<td>{cell}</td>'
            html += '</tr>'
        
        html += '</tbody></table>'
        return html
    
    # Find all tables in the text
    # This pattern looks for a line with pipes, followed by a separator row, followed by at least one data row
    table_pattern = r'(\|[^\n]*\|\n\|[\s\-:]+\|[\s\-:]+\|[\s\-:]*\|\n(?:\|[^\n]*\|\n)+)'
    
    # Replace all tables with HTML
    processed_text = re.sub(table_pattern, lambda m: process_table(m.group(0)), text)
    
    return processed_text