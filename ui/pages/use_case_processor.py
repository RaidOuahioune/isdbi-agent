"""
Use Case Processor page for the Streamlit application (Challenge 1).
"""

import streamlit as st
import sys
from pathlib import Path
import time
import traceback
import re
import json

# Add the parent directory to the path so we can import from the main project
parent_dir = str(Path(__file__).parent.parent.parent)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Local imports
from ui.styles.main import load_css
from ui.states.session_state import init_use_case_state, set_use_case_results, get_use_case_results
from ui.utils.progress_display import display_progress_bar
from retreiver import retriever

def extract_structured_guidance(accounting_guidance):
    """
    Extract structured information from the accounting guidance text.
    
    Args:
        accounting_guidance: The accounting guidance text from the agent
        
    Returns:
        dict: Structured information including product type, standards, etc.
    """
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
    summary_match = re.search(r"(?:\#\#\#|\*\*) ?Summary(?:\#\#\#|\*\*)?\s*(.*?)(?=(?:\#\#\#|\*\*) (?!Summary)|$)", accounting_guidance, re.DOTALL | re.IGNORECASE)
    if summary_match:
        result["summary"] = summary_match.group(1).strip()
    
    # Try to extract product type
    product_match = re.search(r"(?:\*\*)?(?:Islamic Financial Product Type|Product Type|Product|Type)(?:\*\*)?:?\s*(?:\*\*)?([^\n]+?)(?:\*\*)?(?:\n|$)", accounting_guidance, re.IGNORECASE)
    if product_match:
        result["product_type"] = product_match.group(1).strip()
    
    # Try to extract standards
    standards_match = re.search(r"(?:\*\*)?(?:Applicable AAOIFI Standard\(s\)|Applicable Standards|Standards)(?:\*\*)?:?\s*(?:\*\*)?([^\n]+?)(?:\*\*)?(?:\n|$)", accounting_guidance, re.IGNORECASE)
    if standards_match:
        standards_text = standards_match.group(1).strip()
        result["applicable_standards"] = [s.strip() for s in standards_text.split(',')]
    
    # Try to extract method used
    method_match = re.search(r"(?:\*\*)?(?:Method Used)(?:\*\*)?:?\s*(?:\*\*)?([^\n]+?)(?:\*\*)?(?:\n|$)", accounting_guidance, re.IGNORECASE)
    if method_match:
        result["method_used"] = method_match.group(1).strip()
    
    # If no standards found, look for FAS mentions
    if not result["applicable_standards"]:
        fas_matches = re.findall(r"FAS\s+(\d+)", accounting_guidance)
        if fas_matches:
            # Remove duplicates and convert to set for uniqueness
            unique_fas = set(fas_matches)
            result["applicable_standards"] = [f"FAS {fas}" for fas in unique_fas]
    
    # Try to extract calculation methodology
    calc_section = re.search(r"(?:\#\#\#|\*\*) ?Calculation Methodology(?:\#\#\#|\*\*)?\s*(.*?)(?=(?:\#\#\#|\*\*) (?!Calculation)|$)", accounting_guidance, re.DOTALL | re.IGNORECASE)
    if calc_section:
        result["calculation_methodology"] = calc_section.group(1).strip()
    
    # Try to extract journal entries
    journal_section = re.search(r"(?:\#\#\#|\*\*) ?Journal Entries(?:\#\#\#|\*\*)?\s*(.*?)(?=(?:\#\#\#|\*\*) (?!Journal)|$)", accounting_guidance, re.DOTALL | re.IGNORECASE)
    if journal_section:
        result["journal_entries"] = journal_section.group(1).strip()
    
    # Try to extract references
    references_section = re.search(r"(?:\#\#\#|\*\*) ?References(?:\#\#\#|\*\*)?\s*(.*?)(?=$)", accounting_guidance, re.DOTALL | re.IGNORECASE)
    if references_section:
        result["references"] = references_section.group(1).strip()
    
    return result

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
    
    # Add the CSS
    formatted_content = css + formatted_content
    
    return formatted_content

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
        html += f"""
        <div class='summary-item'>
            <div class='summary-label'>Product Type:</div>
            <div class='summary-value'>{summary_data["product_type"]}</div>
        </div>
        """
    
    if summary_data.get("applicable_standards"):
        standards_str = ", ".join(summary_data["applicable_standards"])
        html += f"""
        <div class='summary-item'>
            <div class='summary-label'>Applicable Standards:</div>
            <div class='summary-value'>{standards_str}</div>
        </div>
        """
    
    if summary_data.get("method_used"):
        html += f"""
        <div class='summary-item'>
            <div class='summary-label'>Method Used:</div>
            <div class='summary-value'>{summary_data["method_used"]}</div>
        </div>
        """
    
    # Look for additional summary items - using a more precise pattern
    if summary_data.get("summary"):
        # Get the raw summary text and process it
        summary_text = summary_data["summary"]
        
        # Find bullet points with labels in the summary
        bullet_points = re.findall(r'\*\s+\*\*(.*?):\*\*\s*(.*?)(?=\n\*|\Z)', summary_text, re.DOTALL)
        
        for label, value in bullet_points:
            # Skip items already included
            if label.lower() not in ["islamic financial product type", "product type", "applicable aaoifi standard(s)", "applicable standards", "method used"]:
                cleaned_value = value.strip().replace('\n', '<br>')
                html += f"""
                <div class='summary-item'>
                    <div class='summary-label'>{label}:</div>
                    <div class='summary-value'>{cleaned_value}</div>
                </div>
                """
    
    html += "</div>"
    return html

def render_use_case_processor_page():
    """Render the Use Case Processor page."""
    # Initialize session state
    init_use_case_state()
    
    # Set page configuration
    st.set_page_config(
        page_title="Islamic Finance Use Case Processor",
        page_icon="📒",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Apply CSS
    st.markdown(load_css(), unsafe_allow_html=True)
    
    # Page title
    st.title("📒 Islamic Finance Use Case Processor")
    st.markdown("### Generate accounting guidance for Islamic finance scenarios")
    
    # Sidebar
    st.sidebar.title("Use Case Options")
    
    # Input method selection
    input_method = st.sidebar.radio(
        "Input Method",
        ["Sample Scenarios", "Custom Scenario"]
    )
    
    if input_method == "Sample Scenarios":
        st.sidebar.markdown("### Sample Scenarios")
        # Sample scenarios
        sample_scenarios = [
            {
                "name": "Ijarah MBT Accounting",
                "description": "Accounting for Ijarah Muntahia Bittamleek (lease with ownership transfer)",
                "scenario": """
                An Islamic bank purchases a generator costing $450,000 and pays import tax of $12,000 and freight charges of $30,000.
                The bank leases the generator to a client under an Ijarah Muntahia Bittamleek (IMB) arrangement for 2 years.
                At the end of the Ijarah term, ownership will transfer to the lessee for a nominal amount of $3,000.
                The annual rental is $300,000, payable in equal instalments at the end of each year.
                The estimated residual value of the generator at the end of the lease term is $5,000.
                """
            },
            {
                "name": "Musharakah Profit Distribution",
                "description": "Accounting for profit distribution in a Musharakah arrangement",
                "scenario": """
                An Islamic bank enters into a Musharakah agreement with a business partner to fund a commercial real estate project.
                The bank contributes $800,000 (80%) and the partner contributes $200,000 (20%) to the partnership.
                According to the agreement, profits are to be distributed 70:30 (bank:partner), while losses are to be shared according to capital contribution ratio (80:20).
                At the end of the first year, the partnership generates a profit of $120,000.
                """
            },
            {
                "name": "Sukuk Issuance Accounting",
                "description": "Accounting treatment for Sukuk issuance",
                "scenario": """
                An Islamic financial institution issues Sukuk Al-Ijarah worth $10 million with a 5-year tenure.
                The Sukuk are issued to finance the purchase of a commercial property worth $9.5 million.
                The rental yield is 5% per annum, payable semi-annually.
                The institution acts as the originator and also the servicing agent for the Sukuk.
                Transaction costs for the issuance amount to $200,000.
                At maturity, the institution has committed to repurchase the property at its original value.
                """
            },
            {
                "name": "Murabaha Financing",
                "description": "Accounting for Murabaha financing arrangement",
                "scenario": """
                An Islamic bank enters into a Murabaha financing arrangement with a client for the purchase of industrial equipment.
                The bank purchases the equipment for $750,000 and sells it to the client at a marked-up price of $825,000.
                The client will pay the amount in 3 equal annual instalments of $275,000.
                The bank incurs additional costs of $10,000 for transportation and installation.
                """
            },
            {
                "name": "Istisna'a Contract Accounting",
                "description": "Accounting for an Istisna'a contract from the manufacturer's perspective",
                "scenario": """
                Amanah Construction Co. enters into an Istisna'a contract with Gulf Islamic Bank on 1 January 2021
                to construct a specialized industrial facility for USD 1,000,000, to be completed by 30 June 2022.
                The estimated total cost to complete the project is USD 800,000.
                By 31 December 2021, Amanah has incurred costs of USD 320,000 on the project.
                Determine the appropriate accounting treatment for Amanah Construction Co. (Al-Sani') for the year ended 31 December 2021.
                """
            },
        ]
        
        # Create a dropdown for sample scenarios
        scenario_names = [s["name"] for s in sample_scenarios]
        selected_idx = st.sidebar.selectbox(
            "Select a Sample Scenario",
            range(len(scenario_names)),
            format_func=lambda i: scenario_names[i]
        )
        
        selected_scenario = sample_scenarios[selected_idx]
        
        # Display selected scenario
        st.subheader(f"Scenario: {selected_scenario['name']}")
        st.markdown(f"**Description:** {selected_scenario['description']}")
        
        # Display scenario details
        st.markdown("### Scenario Details")
        st.markdown(f'<div class="diff-container">{selected_scenario["scenario"]}</div>', unsafe_allow_html=True)
        
        # Scenario to process
        scenario_text = selected_scenario["scenario"]
        
    else:  # Custom Scenario
        st.sidebar.markdown("### Custom Scenario")
        
        # Input fields for custom scenario
        scenario_name = st.sidebar.text_input("Scenario Name", "")
        
        st.markdown("### Enter Use Case Details")
        st.markdown("Provide a detailed description of the Islamic finance scenario:")
        
        scenario_text = st.text_area(
            "Scenario",
            "",
            height=200,
            help="Describe the scenario in detail, including amounts, terms, and relevant conditions."
        )
    
    # Process button with additional configuration options
    with st.sidebar.expander("Advanced Settings"):
        show_retrieval = st.checkbox("Show Retrieved Context", value=False, 
                                    help="Display the context retrieved from standards")
        show_raw_guidance = st.checkbox("Show Raw Guidance Output", value=False,
                                       help="Display the raw output from the agent")
        use_streamlit_formatting = st.checkbox("Use Streamlit Native Formatting", value=False,
                                    help="Use Streamlit's native markdown renderer instead of custom HTML")
    
    process_btn = st.button("Generate Accounting Guidance", type="primary")
    
    if process_btn:
        if not scenario_text:
            st.error("Please provide a scenario description.")
        else:
            # Create placeholder containers for progress display
            progress_container = st.empty()
            status_container = st.empty()
            
            with st.spinner("Generating accounting guidance..."):
                try:
                    # Display initial progress
                    display_progress_bar(progress_container, 0.1, "Initializing processing...")
                    status_container.info("Starting scenario analysis...")
                    
                    # Import the use case processor agent directly
                    from components.agents import use_case_processor
                    
                    # Step 1: Retrieve relevant standards information
                    display_progress_bar(progress_container, 0.3, "Retrieving relevant standards...")
                    status_container.info("Searching for applicable AAOIFI standards...")
                    
                    # Use the retriever to get relevant standards information
                    retrieved_nodes = retriever.retrieve(scenario_text)
                    
                    # Optional: Display retrieved chunks if user enabled it
                    if show_retrieval and retrieved_nodes:
                        retrieved_container = st.expander("Retrieved Context from Standards", expanded=False)
                        with retrieved_container:
                            st.markdown("#### Relevant Sections from Standards")
                            for i, node in enumerate(retrieved_nodes[:5]):  # Show only first 5 chunks
                                st.markdown(f"**Chunk {i+1}:**")
                                st.markdown(f"<div class='diff-container'>{node.text[:300]}...</div>", unsafe_allow_html=True)
                    
                    # Step 2: Process the use case
                    display_progress_bar(progress_container, 0.6, "Processing scenario...")
                    status_container.info("Analyzing scenario and applying standards...")
                    
                    # Process the use case directly with the agent
                    results = use_case_processor.process_use_case(scenario_text)
                    
                    # Step 3: Format the results
                    display_progress_bar(progress_container, 0.9, "Preparing results...")
                    status_container.info("Finalizing accounting guidance...")
                    
                    # Extract information from the results
                    accounting_guidance = results["accounting_guidance"]
                    
                    # Parse structured information from the guidance
                    structured_guidance = extract_structured_guidance(accounting_guidance)
                    
                    # Format the guidance for display
                    formatted_guidance = format_content_for_display(accounting_guidance)
                    
                    # Generate summary card HTML
                    summary_card_html = render_summary_card(structured_guidance)
                    
                    # Format final results
                    formatted_results = {
                        "scenario": scenario_text,
                        "identified_product": structured_guidance["product_type"],
                        "applicable_standards": structured_guidance["applicable_standards"],
                        "method_used": structured_guidance.get("method_used", ""),
                        "calculation_methodology": structured_guidance["calculation_methodology"],
                        "journal_entries": structured_guidance["journal_entries"],
                        "references": structured_guidance["references"],
                        "summary": structured_guidance.get("summary", ""),
                        "accounting_guidance": accounting_guidance,  # Keep the original guidance
                        "formatted_guidance": formatted_guidance,    # Format with custom HTML
                        "summary_card_html": summary_card_html,      # The formatted summary card
                        "raw_guidance": accounting_guidance if show_raw_guidance else None
                    }
                    
                    # Save results to session state
                    set_use_case_results(formatted_results)
                    
                    # Mark as complete
                    display_progress_bar(progress_container, 1.0, "Completed!")
                    status_container.success("Accounting guidance generated successfully!")
                    
                except Exception as e:
                    # Clear progress indicators
                    progress_container.empty()
                    status_container.error(f"Error generating accounting guidance: {str(e)}")
                    st.error("An error occurred during processing. Please try again.")
                    # Print the full traceback for debugging
                    st.exception(e)
    
    # Display results if available
    results = get_use_case_results()
    if results:
        st.header("Accounting Guidance")
        
        # Display the enhanced summary card if available
        if results.get("summary_card_html"):
            st.markdown(results["summary_card_html"], unsafe_allow_html=True)
        else:
            # Fallback to simple summary display
            st.subheader("Summary")
            col1, col2 = st.columns([1, 3])
            
            with col1:
                st.markdown(f"**Product Type:**")
                st.markdown(f"<div class='diff-stat-item'><div class='diff-stat-value'>{results['identified_product']}</div></div>", unsafe_allow_html=True)
                
                st.markdown(f"**Applicable Standards:**")
                for standard in results["applicable_standards"]:
                    st.markdown(f"<div class='diff-stat-item'>{standard}</div>", unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"<div class='diff-container'>{results['scenario'][:300]}...</div>", unsafe_allow_html=True)
        
        # Display the content based on user preference
        if use_streamlit_formatting:
            # Use Streamlit's native markdown rendering - often better for simple tables
            # Remove summary section as we've already displayed it separately
            content = re.sub(r"(?:\#\#\#|\*\*) ?Summary(?:\#\#\#|\*\*)?\s*.*?(?=(?:\#\#\#|\*\*) (?!Summary)|$)", "", 
                          results["accounting_guidance"], flags=re.DOTALL | re.IGNORECASE)
            st.markdown(content)
        else:
            # Use our custom HTML formatting with better table handling
            # Remove summary section as we've already displayed it separately
            content = re.sub(r"(?:\#\#\#|\*\*) ?Summary(?:\#\#\#|\*\*)?\s*.*?(?=(?:\#\#\#|\*\*) (?!Summary)|$)", "", 
                          results["formatted_guidance"], flags=re.DOTALL | re.IGNORECASE)
            st.markdown(content, unsafe_allow_html=True)
        
        # Show raw output if enabled
        if results.get("raw_guidance") and show_raw_guidance:
            with st.expander("Raw Guidance Output", expanded=False):
                st.markdown(f'<div class="diff-container">{results["raw_guidance"]}</div>', unsafe_allow_html=True)
        
        # Export options
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                label="Export as Markdown",
                data=f"""# Accounting Guidance for {results['identified_product']}

## Applicable Standards
{chr(10).join(['- ' + std for std in results['applicable_standards']])}

{results['accounting_guidance']}
""",
                file_name="accounting_guidance.md",
                mime="text/markdown"
            )
        
        with col2:
            # Convert results to JSON for export
            json_data = {
                "product_type": results['identified_product'],
                "applicable_standards": results['applicable_standards'],
                "method_used": results.get('method_used', ''),
                "scenario": results['scenario'],
                "accounting_guidance": results['accounting_guidance']
            }
            
            st.download_button(
                label="Export as JSON",
                data=json.dumps(json_data, indent=2),
                file_name="accounting_guidance.json",
                mime="application/json"
            )

if __name__ == "__main__":
    render_use_case_processor_page() 