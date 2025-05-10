"""
Compliance Verifier page for the Streamlit application (Challenge 5).
"""

import streamlit as st
import sys
import json
from pathlib import Path
import time
from datetime import datetime
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import io

# Add the parent directory to the path so we can import from the main project
parent_dir = str(Path(__file__).parent.parent.parent)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Local imports
from ui.styles.main import load_css
from ui.states.session_state import (
    init_compliance_verifier_state, 
    set_compliance_verifier_results, 
    get_compliance_verifier_results,
    add_saved_verification,
    get_saved_verifications
)
from ui.utils.compliance_utils import (
    process_uploaded_file,
    verify_compliance,
    calculate_compliance_stats,
    save_verification_result,
    load_past_verifications
)

def render_compliance_verifier_page(standalone=False):
    """Render the Compliance Verifier page for Challenge 5."""
    # Initialize session state
    init_compliance_verifier_state()
    
    # Set page configuration only if running in standalone mode
    if standalone:
        st.set_page_config(
            page_title="Islamic Finance Compliance Verifier",
            page_icon="📋",
            layout="wide",
            initial_sidebar_state="expanded"
        )
    
    # Apply CSS
    st.markdown(load_css(), unsafe_allow_html=True)
    
    # Page title and description
    st.title("📋 Compliance Verifier")
    st.markdown("""
    ### Verify compliance of financial reports with AAOIFI standards
    
    This tool analyzes financial reports and documents for compliance with AAOIFI (Accounting and 
    Auditing Organization for Islamic Financial Institutions) standards. It provides detailed 
    compliance reports with recommendations for improvement.
    """)
    
    # Create sidebar for options
    st.sidebar.title("Verification Options")
    
    # Mode selection
    mode = st.sidebar.radio(
        "Mode",
        ["New Verification", "View Saved Verifications"]
    )
    
    if mode == "New Verification":
        render_new_verification_form()
    else:
        render_saved_verifications()

def render_new_verification_form():
    """Render the form for creating a new compliance verification."""
    st.subheader("Document Upload")
    
    # Document upload
    uploaded_file = st.file_uploader(
        "Upload Financial Report",
        type=["pdf", "txt"],
        help="Upload a financial report in PDF or text format for compliance verification."
    )
    
    # Optional document name
    document_name = st.text_input(
        "Document Name (optional)",
        value="",
        placeholder="e.g., Q2 2023 Financial Report"
    )
    
    # Sample documents option
    st.subheader("Or Use a Sample Document")
    sample_option = st.selectbox(
        "Select Sample Document",
        [
            "None",
            "Sample Islamic Bank Annual Report",
            "Sample Sukuk Offering Circular"
        ]
    )
    
    # Process sample selection
    sample_content = None
    if sample_option != "None":
        # In a real implementation, you would load these from files
        if sample_option == "Sample Islamic Bank Annual Report":
            sample_content = """
            Al-Baraka Islamic Bank
            Annual Financial Report 2023
            
            Statement of Financial Position
            As of December 31, 2023
            (All amounts in thousands of USD)
            
                                            2023        2022
            Assets
            Cash and balances with banks    125,000     110,000
            Murabaha receivables            450,000     420,000
            Ijara assets                    320,000     280,000
            Istisna' assets                 180,000     150,000
            Sukuk investments               220,000     200,000
            Property and equipment           50,000      45,000
            Other assets                     55,000      48,000
            Total Assets                  1,400,000   1,253,000
            
            Liabilities
            Customer current accounts       320,000     290,000
            Due to banks                     80,000      75,000
            Other liabilities                65,000      58,000
            Total Liabilities               465,000     423,000
            
            Equity of Investment Account Holders
            Investment accounts             800,000     720,000
            
            Owners' Equity
            Share capital                    85,000      85,000
            Reserves                         25,000      15,000
            Retained earnings                25,000      10,000
            Total Owners' Equity            135,000     110,000
            
            Total Liabilities, Equity of IAH, and Owners' Equity  1,400,000  1,253,000
            
            Income Statement
            For the year ended December 31, 2023
            (All amounts in thousands of USD)
            
                                                        2023        2022
            Income
            Income from Murabaha                        45,000      40,000
            Income from Ijara                           32,000      28,000
            Income from Istisna'                        18,000      15,000
            Income from Sukuk                           22,000      20,000
            Fee and commission income                   15,000      12,000
            Total Income                               132,000     115,000
            
            Less: Return to Investment Account Holders  (70,000)    (60,000)
            Bank's share of income as Mudarib           62,000      55,000
            
            Expenses
            Staff costs                                (20,000)    (18,000)
            Depreciation                                (5,000)     (4,500)
            General and administrative expenses        (12,000)    (11,000)
            Provision for credit losses                 (5,000)     (6,000)
            Total Expenses                             (42,000)    (39,500)
            
            Net Income for the Year                     20,000      15,500
            
            Notes to the Financial Statements:
            
            Note 1: Basis of Preparation
            These financial statements have been prepared in accordance with generally accepted accounting principles.
            
            Note 2: Significant Accounting Policies
            The accounting policies applied are consistent with those used in the previous financial year.
            
            Note 3: Ijara
            Ijara assets represent properties leased under operating lease agreements.
            
            Note 4: Financing Assets
            Financing assets consist of Murabaha receivables, Istisna' assets, and Sukuk investments.
            """
        elif sample_option == "Sample Sukuk Offering Circular":
            sample_content = """
            Al-Noor Sukuk Trust
            Sukuk Al-Ijara Offering Circular
            USD 500 Million Trust Certificates due 2028
            
            Financial Information:
            
            Use of Proceeds:
            The proceeds of the Sukuk will be used by the Trustee to purchase certain assets from the Originator, which will be leased back to the Originator under a master Ijara agreement.
            
            Summary of Financial Terms:
            - Issue Size: USD 500 million
            - Tenor: 5 years
            - Expected Profit Rate: 4.5% per annum
            - Payment Frequency: Semi-annual
            - Issue Date: March 15, 2023
            - Maturity Date: March 15, 2028
            
            Structure:
            The Sukuk is structured as an Ijara (lease) and is considered asset-backed. The underlying assets are a portfolio of real estate properties with a total value of USD 650 million.
            
            Profit Distribution:
            Profit will be distributed semi-annually to certificate holders, derived from lease payments made by the Originator.
            
            Transaction Documents:
            - Declaration of Trust
            - Master Purchase Agreement
            - Master Lease Agreement
            - Purchase Undertaking
            - Sale Undertaking
            - Service Agency Agreement
            
            Financial Statements of the Originator (Summary):
            
            Statement of Financial Position
            As of December 31, 2022
            (All amounts in millions of USD)
            
            Assets
            Total Assets: 2,500
            
            Liabilities
            Total Liabilities: 1,800
            
            Equity
            Total Equity: 700
            
            Income Statement
            For the year ended December 31, 2022
            (All amounts in millions of USD)
            
            Total Revenue: 850
            Total Expenses: (650)
            Net Income: 200
            """
    
    # Verification button
    col1, col2 = st.columns([1, 3])
    with col1:
        verify_button = st.button("Verify Compliance", type="primary", use_container_width=True)
    
    with col2:
        st.markdown("""
        <div style="padding: 10px 0px 0px 10px; color: #6c757d; font-size: 0.9em;">
        Verification will analyze the document against AAOIFI standards FAS 4, 7, 10, 28, and 32.
        </div>
        """, unsafe_allow_html=True)
    
    # Handle verification
    if verify_button:
        if uploaded_file is None and sample_content is None:
            st.error("Please upload a document or select a sample document.")
        else:
            with st.spinner("Verifying compliance..."):
                try:
                    # Process the document
                    if uploaded_file:
                        result = process_uploaded_file(uploaded_file)
                        doc_content = result["content"]
                        doc_name = document_name if document_name else uploaded_file.name
                    else:
                        doc_content = sample_content
                        doc_name = document_name if document_name else sample_option
                    
                    # Verify compliance
                    verification_result = verify_compliance(doc_content, doc_name)
                    
                    # Save results to session state
                    set_compliance_verifier_results(verification_result)
                    
                    # Display success message
                    st.success("Compliance verification completed!")
                    
                    # Save to saved verifications
                    add_saved_verification(verification_result)
                except Exception as e:
                    st.error(f"Error during compliance verification: {str(e)}")
    
    # Display results if available
    results = get_compliance_verifier_results()
    if results:
        display_verification_results(results)

def display_verification_results(results):
    """Display the compliance verification results."""
    st.markdown("---")
    
    # Calculate compliance statistics
    stats = calculate_compliance_stats(results.get("structured_report", []))
    
    # Summary section
    st.header(f"📋 Compliance Verification for: {results['document_name']}")
    st.markdown(f"*Verification completed on: {datetime.fromisoformat(results['timestamp']).strftime('%B %d, %Y at %H:%M')}*")
    
    # Create tabs for different sections
    tabs = st.tabs([
        "Summary", 
        "Detailed Report", 
        "Statistics", 
        "Raw Document"
    ])
    
    # Tab 1: Summary
    with tabs[0]:
        st.subheader("Compliance Summary")
        
        # Create columns for stats
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Overall Compliance Rate",
                f"{stats['compliance_rate']:.1f}%",
                delta=None
            )
        
        with col2:
            st.metric(
                "Compliant Requirements",
                f"{stats['compliant']} / {stats['total_requirements']}",
                delta=None
            )
        
        with col3:
            st.metric(
                "Non-Compliant Requirements",
                f"{stats['missing'] + stats['partial']} / {stats['total_requirements']}",
                delta=None
            )
        
        # Create compliance gauge chart
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=stats['compliance_rate'],
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Compliance Rate"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "royalblue"},
                'steps': [
                    {'range': [0, 33], 'color': "red"},
                    {'range': [33, 67], 'color': "orange"},
                    {'range': [67, 100], 'color': "green"}
                ],
                'threshold': {
                    'line': {'color': "black", 'width': 4},
                    'thickness': 0.75,
                    'value': stats['compliance_rate']
                }
            }
        ))
        
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
        
        # Summary per standard
        st.subheader("Compliance by Standard")
        
        # Create dataframe for standards
        standards_data = []
        for std, data in stats['standards'].items():
            standards_data.append({
                "Standard": std,
                "Compliance Rate": data['compliance_rate'],
                "Compliant": data['compliant'],
                "Partial": data['partial'],
                "Missing": data['missing'],
                "Total": data['total']
            })
        
        # Sort by compliance rate
        standards_df = pd.DataFrame(standards_data)
        standards_df = standards_df.sort_values("Compliance Rate", ascending=False)
        
        # Create bar chart
        fig = px.bar(
            standards_df,
            x="Standard",
            y="Compliance Rate",
            color="Compliance Rate",
            color_continuous_scale=["red", "orange", "green"],
            range_color=[0, 100],
            labels={"Compliance Rate": "Compliance Rate (%)"}
        )
        
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        # Show standards table
        st.dataframe(
            standards_df,
            hide_index=True,
            column_config={
                "Compliance Rate": st.column_config.ProgressColumn(
                    "Compliance Rate",
                    format="%.1f%%",
                    min_value=0,
                    max_value=100
                )
            }
        )
    
    # Tab 2: Detailed Report
    with tabs[1]:
        st.subheader("Detailed Compliance Report")
        
        # Process structured report for display
        report_data = []
        for item in results.get("structured_report", []):
            # Determine status icon
            status_icon = "❌"
            status_color = "red"
            if item["status_code"] == "compliant":
                status_icon = "✅"
                status_color = "green"
            elif item["status_code"] == "partial":
                status_icon = "⚠️"
                status_color = "orange"
            
            report_data.append({
                "Standard": item["standard"],
                "Requirement": item["requirement"],
                "Status": f"<span style='color: {status_color};'>{status_icon} {item['status']}</span>",
                "Comments or Suggestions": item["comments"]
            })
        
        # Create dataframe
        report_df = pd.DataFrame(report_data)
        
        # Show dataframe
        st.markdown(
            report_df.style.hide(axis="index")
            .format(escape="html")
            .to_html(),
            unsafe_allow_html=True
        )
        
        # Export options
        export_col1, export_col2 = st.columns(2)
        
        with export_col1:
            # CSV export
            csv_data = report_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download as CSV",
                data=csv_data,
                file_name=f"compliance_report_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with export_col2:
            # Excel export
            excel_buffer = io.BytesIO()
            report_df.to_excel(excel_buffer, index=False, engine='openpyxl')
            excel_data = excel_buffer.getvalue()
            
            st.download_button(
                label="Download as Excel",
                data=excel_data,
                file_name=f"compliance_report_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
    
    # Tab 3: Statistics
    with tabs[2]:
        st.subheader("Compliance Statistics")
        
        # Create pie chart for overall compliance
        fig = px.pie(
            values=[stats['compliant'], stats['partial'], stats['missing']],
            names=["Compliant", "Partial", "Missing"],
            title="Compliance Status Distribution",
            color_discrete_map={
                "Compliant": "green",
                "Partial": "orange",
                "Missing": "red"
            }
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Create stacked bar chart for standards
        standards_stack_data = []
        for std, data in stats['standards'].items():
            standards_stack_data.append({
                "Standard": std,
                "Status": "Compliant",
                "Count": data['compliant']
            })
            standards_stack_data.append({
                "Standard": std,
                "Status": "Partial",
                "Count": data['partial']
            })
            standards_stack_data.append({
                "Standard": std,
                "Status": "Missing",
                "Count": data['missing']
            })
        
        stack_df = pd.DataFrame(standards_stack_data)
        
        fig = px.bar(
            stack_df,
            x="Standard",
            y="Count",
            color="Status",
            title="Compliance Status by Standard",
            barmode="stack",
            color_discrete_map={
                "Compliant": "green",
                "Partial": "orange",
                "Missing": "red"
            }
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Tab 4: Raw Document
    with tabs[3]:
        st.subheader("Document Content")
        
        # Display the raw document
        st.text_area(
            "Document Content",
            value=results['document'],
            height=400,
            disabled=True
        )

def render_saved_verifications():
    """Render the saved verifications page."""
    st.subheader("Saved Compliance Verifications")
    
    # Get saved verifications
    saved_verifications = get_saved_verifications()
    
    if not saved_verifications:
        st.info("No saved verifications found. Verify a document to save results.")
        return
    
    # Create a selection box for the saved verifications
    verification_names = [f"{v.get('document_name', 'Unnamed')} ({datetime.fromisoformat(v.get('timestamp', '')).strftime('%Y-%m-%d %H:%M')})" for v in saved_verifications]
    selected_idx = st.selectbox(
        "Select a Saved Verification",
        range(len(verification_names)),
        format_func=lambda i: verification_names[i]
    )
    
    # Get the selected verification
    selected_verification = saved_verifications[selected_idx]
    
    # Load and display the verification
    display_verification_results(selected_verification)

if __name__ == "__main__":
    render_compliance_verifier_page(standalone=True) 