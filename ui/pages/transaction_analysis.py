"""
Transaction Analysis page for the Streamlit application (Challenge 2).
"""

import streamlit as st
import sys
import json
from pathlib import Path
import traceback
import requests
import time
import threading

# Add the parent directory to the path so we can import from the main project
parent_dir = str(Path(__file__).parent.parent.parent)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Local imports
from ui.styles.main import load_css
from ui.states.session_state import (
    init_transaction_analysis_state, 
    set_transaction_analysis_results, 
    get_transaction_analysis_results,
    set_transaction_analysis_results_dual,
    get_transaction_analysis_results_dual,
    set_selected_transaction_answer,
    get_selected_transaction_answer,
    save_feedback
)

# Import our improved utils for transaction analysis
from ui.utils.transaction_utils import analyze_transaction, DIRECT_IMPORT_AVAILABLE

# API endpoint as fallback - but we'll try to use local methods first
API_ENDPOINT = "http://localhost:8000/api/agent"

def render_transaction_analysis_page():
    """Render the Transaction Analysis page for Challenge 2: Reverse Transactions."""
    # Initialize session state
    init_transaction_analysis_state()
    
    # Page title and description
    st.title("📝 Islamic Finance Transaction Analysis")
    st.markdown("""
    ### Identify applicable AAOIFI standards from journal entries (Challenge 2)
    
    This module analyzes financial journal entries to identify which AAOIFI Financial Accounting 
    Standards (FAS) are most applicable. Enter transaction details or select from samples 
    to receive a detailed analysis.
    """)
    
    # Create sidebar for options
    st.sidebar.title("Transaction Options")
    
    # Input method selection
    input_method = st.sidebar.radio(
        "Input Method",
        ["Sample Transactions", "Structured Input", "Free-text Input"]
    )
    
    if input_method == "Sample Transactions":
        # Load sample transactions from a predefined list
        sample_transactions = load_sample_transactions()
        
        # Create a dropdown for sample transactions
        transaction_names = [t["name"] for t in sample_transactions]
        selected_idx = st.sidebar.selectbox(
            "Select a Sample Transaction",
            range(len(transaction_names)),
            format_func=lambda i: transaction_names[i]
        )
        
        selected_transaction = sample_transactions[selected_idx]
        display_transaction(selected_transaction)
        transaction_details = selected_transaction
        
    elif input_method == "Structured Input":
        transaction_details = handle_custom_transaction_input()
    else:  # Free-text Input
        transaction_details = handle_free_text_input()
    
    # Analysis button
    analyze_col1, analyze_col2 = st.columns([1, 3])
    with analyze_col1:
        analyze_btn = st.button("Analyze Transaction", type="primary", use_container_width=True)
    
    with analyze_col2:
        st.markdown("""
        <div style="padding: 10px 0px 0px 10px; color: #6c757d; font-size: 0.9em;">
        Analysis will identify applicable AAOIFI standards with detailed rationale.
        </div>
        """, unsafe_allow_html=True)
    
    # Method selection for analysis (hidden in sidebar)
    st.sidebar.markdown("### Advanced Settings")
    analysis_method = st.sidebar.radio(
        "Analysis Method",
        ["File-Based (Fastest)", "Direct (Fast)", "API (Fallback)"],
        help="File-Based reads from pre-analyzed results. Direct calls the agent directly. API uses the server endpoint."
    )
    
    # Add new options for dual answers
    generate_dual_answers = st.sidebar.checkbox(
        "Generate Dual Answers", 
        value=True,
        help="Generate two different analysis versions for comparison"
    )
    
    # Handle analysis button click
    if analyze_btn:
        if input_method == "Free-text Input" and not transaction_details.get("context", "").strip():
            st.error("Please provide some transaction details to analyze.")
        elif input_method == "Structured Input" and not is_balanced(transaction_details.get("journal_entries", [])):
            st.warning("Journal entries are not balanced. Analysis may be less accurate.")
            # Continue anyway - don't enforce balance for jury testing
            with st.spinner("Analyzing transaction..."):
                process_analysis(transaction_details, analysis_method, generate_dual=generate_dual_answers)
        else:
            with st.spinner("Analyzing transaction..."):
                process_analysis(transaction_details, analysis_method, generate_dual=generate_dual_answers)
    
    # Display results if available
    if generate_dual_answers:
        results_1, results_2 = get_transaction_analysis_results_dual()
        if results_1 and results_2:
            display_dual_analysis_results(results_1, results_2)
    else:
        results = get_transaction_analysis_results()
        if results:
            display_analysis_results(results)

def process_analysis(transaction_details, analysis_method, generate_dual=False):
    """Process the transaction analysis based on the selected method."""
    try:
        # Process based on selected method using our helper
        use_api = False
        if analysis_method == "API (Fallback)":
            use_api = True
        elif analysis_method == "Direct (Fast)":
            # Force direct method by removing name to skip file-based method
            if isinstance(transaction_details, dict) and "name" in transaction_details:
                transaction_copy = transaction_details.copy()
                transaction_copy.pop("name", None)
                transaction_details = transaction_copy
        
        if generate_dual:
            # Create two slightly different analyses
            results_ready = {"is_ready": False, "results_1": None, "results_2": None}
            
            # Run analyses in parallel threads
            def process_analysis_1():
                results = analyze_transaction(transaction_details, use_api=use_api)
                results_ready["results_1"] = results
                check_if_both_ready()
                
            def process_analysis_2():
                # Add a slight variation for the second analysis to get different results
                modified_details = transaction_details.copy() if isinstance(transaction_details, dict) else {"context": transaction_details}
                
                # Add a hint to generate a different perspective
                if isinstance(modified_details, dict):
                    if "context" in modified_details:
                        modified_details["context"] = modified_details["context"] + "\n\nPlease provide an alternative analysis with more emphasis on practical implications."
                    else:
                        modified_details["analysis_perspective"] = "alternative_perspective"
                
                results = analyze_transaction(modified_details, use_api=use_api)
                results_ready["results_2"] = results
                check_if_both_ready()
                
            def check_if_both_ready():
                if results_ready["results_1"] and results_ready["results_2"]:
                    results_ready["is_ready"] = True
            
            # Start threads
            thread1 = threading.Thread(target=process_analysis_1)
            thread2 = threading.Thread(target=process_analysis_2)
            
            thread1.start()
            thread2.start()
            
            # Wait for both threads to complete with progress indicator
            progress_placeholder = st.empty()
            while not results_ready["is_ready"]:
                for i in range(10):
                    progress_placeholder.progress((i+1)/10)
                    time.sleep(0.1)
                    if results_ready["is_ready"]:
                        break
            
            progress_placeholder.empty()
            
            # Store results
            set_transaction_analysis_results_dual(results_ready["results_1"], results_ready["results_2"])
            
            # Success message
            st.success("Transaction analysis completed with dual perspectives!")
        else:
            # Call the analyzer with the appropriate method
            results = analyze_transaction(transaction_details, use_api=use_api)
            
            # Check if results are valid
            if not results or (isinstance(results, dict) and "error" in results):
                error_msg = results.get("error", "Unknown error") if isinstance(results, dict) else "Failed to analyze transaction"
                st.error(f"Analysis failed: {error_msg}")
            else:
                # Save results to session state
                set_transaction_analysis_results(results)
                
                # Success message
                st.success("Transaction analysis completed!")
    except Exception as e:
        st.error(f"Error analyzing transaction: {str(e)}")
        st.error(traceback.format_exc())

def load_sample_transactions():
    """Load sample transactions for demo purposes."""
    return [
        {
            "name": "Salam Contract Cancellation",
            "description": "Al-Falah Agricultural Bank cancels a Salam agreement with Sunrise Farms due to crop failure",
            "journal_entries": [
                {"account": "Cash", "debit": 825000, "credit": 0},
                {"account": "Cancellation Income", "debit": 25000, "credit": 0},
                {"account": "Commodity Receivables", "debit": 0, "credit": 850000},
                {"account": "Cash", "debit": 0, "credit": 15000},
                {"account": "Termination Fee Expense", "debit": 15000, "credit": 0}
            ],
            "context": """
            Al-Falah Agricultural Bank had entered into an advance purchase agreement (Salam) with Sunrise Farms for wheat.
            Terms: 
            - Advance payment: $850,000
            - Quantity: 10,000 bushels of wheat
            - Delivery Date: Originally scheduled for 6 months after payment
            - Reason for Cancellation: Crop failure at Sunrise Farms, preventing delivery
            - The bank had a parallel agreement to sell the wheat to a third party

            The parties agree to cancel the contract, with Sunrise Farms returning the advance minus $25,000 as cancellation income.
            Al-Falah pays a $15,000 termination fee related to its parallel agreement.
            """
        },
        {
            "name": "Contract Change Order Reversal",
            "description": "The client cancels the change order, reverting to the original contract terms",
            "journal_entries": [
                {"account": "Accounts Payable", "debit": 1000000, "credit": 0},
                {"account": "Work-in-Progress", "debit": 0, "credit": 1000000}
            ],
            "context": """
            Context: The client cancels the change order, reverting to the original contract terms.
            Adjustments:
            - Revised Contract Value: Back to $5,000,000 (from $6,000,000)
            - Timeline Restored: 2 years (from 2.5 years)
            - Accounting Treatment:
              - Adjustment of revenue and cost projections
              - Reversal of additional cost accruals
            This restores the original contract cost.
            """
        },
        {
            "name": "Partner Equity Buyout",
            "description": "GreenTech exits in Year 3, and Al Baraka Bank buys out its stake",
            "journal_entries": [
                {"account": "GreenTech Equity", "debit": 1750000, "credit": 0},
                {"account": "Cash", "debit": 0, "credit": 1750000}
            ],
            "context": """
            Context: GreenTech exits in Year 3, and Al Baraka Bank buys out its stake.
            Adjustments:
            - Buyout Price: $1,750,000
            - Bank Ownership: 100%
            - Accounting Treatment:
              - Derecognition of GreenTech's equity
              - Recognition of acquisition expense
            """
        }
    ]

def display_transaction(transaction):
    """Display transaction details in a structured format."""
    # Create expander for transaction details
    with st.expander("Transaction Details", expanded=True):
        # Title and description
        st.subheader(f"{transaction['name']}")
        st.markdown(f"**Description:** {transaction['description']}")
        
        # Context in a formatted box
        st.markdown("### Context")
        st.markdown(f"""
        <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin-bottom: 15px;">
            {transaction['context']}
        </div>
        """, unsafe_allow_html=True)
        
        # Journal entries in a table
        st.markdown("### Journal Entries")
        entries_data = []
        for entry in transaction["journal_entries"]:
            entries_data.append({
                "Account": entry["account"],
                "Debit": f"${entry['debit']:,.2f}" if entry["debit"] > 0 else "",
                "Credit": f"${entry['credit']:,.2f}" if entry["credit"] > 0 else ""
            })
        
        st.table(entries_data)
        
        # Calculate and display totals
        total_debits = sum(entry["debit"] for entry in transaction["journal_entries"])
        total_credits = sum(entry["credit"] for entry in transaction["journal_entries"])
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Total Debits:** ${total_debits:,.2f}")
        with col2:
            st.markdown(f"**Total Credits:** ${total_credits:,.2f}")
        
        # Check if balanced
        if abs(total_debits - total_credits) <= 0.01:
            st.success("Journal entries are balanced.")
        else:
            st.warning("Journal entries are not balanced.")

def handle_custom_transaction_input():
    """Handle input for custom transaction details."""
    st.sidebar.markdown("### Structured Transaction Input")
    
    transaction_name = st.sidebar.text_input("Transaction Name", "")
    transaction_context = st.sidebar.text_area(
        "Transaction Context",
        "",
        help="Provide context about the transaction, including its purpose and nature."
    )
    
    # Custom journal entries input
    st.markdown("## Enter Journal Entries")
    st.markdown("Add the journal entries for your transaction:")
    
    # Initialize entries if needed
    if "journal_entries" not in st.session_state:
        st.session_state.journal_entries = [
            {"account": "", "debit": 0, "credit": 0}
        ]
    
    # Display header row
    header_cols = st.columns([3, 2, 2, 1])
    with header_cols[0]:
        st.markdown("**Account**")
    with header_cols[1]:
        st.markdown("**Debit**")
    with header_cols[2]:
        st.markdown("**Credit**")
    
    # Display entries
    for i, entry in enumerate(st.session_state.journal_entries):
        cols = st.columns([3, 2, 2, 1])
        with cols[0]:
            st.session_state.journal_entries[i]["account"] = st.text_input(
                "Account", 
                entry["account"], 
                key=f"account_{i}",
                label_visibility="collapsed"
            )
        with cols[1]:
            st.session_state.journal_entries[i]["debit"] = st.number_input(
                "Debit", 
                min_value=0.0, 
                value=float(entry["debit"]), 
                key=f"debit_{i}",
                label_visibility="collapsed"
            )
        with cols[2]:
            st.session_state.journal_entries[i]["credit"] = st.number_input(
                "Credit", 
                min_value=0.0, 
                value=float(entry["credit"]), 
                key=f"credit_{i}",
                label_visibility="collapsed"
            )
        with cols[3]:
            if i > 0:  # Don't allow removing the first entry
                st.button("✕", key=f"remove_{i}", on_click=remove_entry, args=(i,), help="Remove this entry")
    
    # Add entry button
    st.button("Add Entry", on_click=add_entry)
    
    # Validate entries
    entries = st.session_state.journal_entries
    total_debits = sum(entry["debit"] for entry in entries)
    total_credits = sum(entry["credit"] for entry in entries)
    
    # Display totals
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**Total Debits:** ${total_debits:,.2f}")
    with col2:
        st.markdown(f"**Total Credits:** ${total_credits:,.2f}")
    
    # Check if entries balance
    if abs(total_debits - total_credits) > 0.01:
        st.warning(f"Journal entries do not balance. Debits: ${total_debits:,.2f}, Credits: ${total_credits:,.2f}")
    else:
        st.success(f"Journal entries balance. Total: ${total_debits:,.2f}")
    
    # Filter out empty entries
    valid_entries = [
        entry for entry in entries 
        if entry["account"] and (entry["debit"] > 0 or entry["credit"] > 0)
    ]
    
    # Return transaction details
    return {
        "name": transaction_name,
        "context": transaction_context,
        "journal_entries": valid_entries,
        "description": "Custom transaction"
    }

def handle_free_text_input():
    """Handle free-text input for maximal flexibility."""
    st.markdown("## Free-text Transaction Input")
    st.markdown("""
    Enter any transaction details below. You can use any format or structure you prefer.
    There are no constraints - paste or type your transaction description, journal entries, 
    or any other information in whatever format is most convenient.
    
    Your input will be analyzed to identify applicable AAOIFI standards.
    """)
    
    # Text area for free-text input with large height for jury convenience
    transaction_text = st.text_area(
        "Enter Transaction Details",
        "",
        height=400,
        help="Enter transaction details in any format. Complete flexibility for your analysis needs."
    )
    
    return {"context": transaction_text}

def add_entry():
    """Add a new journal entry."""
    st.session_state.journal_entries.append({"account": "", "debit": 0, "credit": 0})

def remove_entry(idx):
    """Remove a journal entry at the given index."""
    st.session_state.journal_entries.pop(idx)

def is_balanced(entries):
    """Check if journal entries are balanced."""
    if not entries:
        return False
        
    total_debits = sum(entry["debit"] for entry in entries)
    total_credits = sum(entry["credit"] for entry in entries)
    return abs(total_debits - total_credits) <= 0.01

def display_dual_analysis_results(results_1, results_2):
    """Display two sets of transaction analysis results with tabs and feedback collection."""
    st.header("Analysis Results")
    
    # Create tabs for the two different answers
    answer_tabs = st.tabs(["Analysis Option 1", "Analysis Option 2"])
    
    selected_answer = get_selected_transaction_answer()
    
    # Display first analysis
    with answer_tabs[0]:
        if selected_answer == 1:
            st.success("✓ You selected this analysis as preferred")
        
        # Display the content
        display_analysis_content(results_1)
        
        # Add selection and feedback buttons
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            if st.button("Select as Preferred", key=f"select_1_{id(results_1)}"):
                set_selected_transaction_answer(1)
                
                # Save feedback
                feedback_data = {
                    "transaction": results_1.get("transaction_summary", ""),
                    "selected_analysis": 1,
                    "feedback_type": "selection"
                }
                save_feedback("transaction_analysis", feedback_data)
                
                st.rerun()
        
        with col2:
            if st.button("👍 Helpful", key=f"thumbs_up_1_{id(results_1)}"):
                # Save positive feedback
                feedback_data = {
                    "transaction": results_1.get("transaction_summary", ""),
                    "analysis_option": 1,
                    "feedback_type": "helpful",
                    "rating": "positive"
                }
                save_feedback("transaction_analysis", feedback_data)
                st.success("Thank you for your feedback!")
        
        with col3:
            if st.button("👎 Not Helpful", key=f"thumbs_down_1_{id(results_1)}"):
                # Save negative feedback
                feedback_data = {
                    "transaction": results_1.get("transaction_summary", ""),
                    "analysis_option": 1,
                    "feedback_type": "helpful",
                    "rating": "negative"
                }
                save_feedback("transaction_analysis", feedback_data)
                st.error("Thank you for your feedback!")
    
    # Display second analysis
    with answer_tabs[1]:
        if selected_answer == 2:
            st.success("✓ You selected this analysis as preferred")
            
        # Display the content
        display_analysis_content(results_2)
        
        # Add selection and feedback buttons
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            if st.button("Select as Preferred", key=f"select_2_{id(results_2)}"):
                set_selected_transaction_answer(2)
                
                # Save feedback
                feedback_data = {
                    "transaction": results_2.get("transaction_summary", ""),
                    "selected_analysis": 2,
                    "feedback_type": "selection"
                }
                save_feedback("transaction_analysis", feedback_data)
                
                st.rerun()
        
        with col2:
            if st.button("👍 Helpful", key=f"thumbs_up_2_{id(results_2)}"):
                # Save positive feedback
                feedback_data = {
                    "transaction": results_2.get("transaction_summary", ""),
                    "analysis_option": 2,
                    "feedback_type": "helpful",
                    "rating": "positive"
                }
                save_feedback("transaction_analysis", feedback_data)
                st.success("Thank you for your feedback!")
        
        with col3:
            if st.button("👎 Not Helpful", key=f"thumbs_down_2_{id(results_2)}"):
                # Save negative feedback
                feedback_data = {
                    "transaction": results_2.get("transaction_summary", ""),
                    "analysis_option": 2,
                    "feedback_type": "helpful",
                    "rating": "negative"
                }
                save_feedback("transaction_analysis", feedback_data)
                st.error("Thank you for your feedback!")

def display_analysis_content(results):
    """Display the analysis content (used by both single and dual display)."""
    # Create tabs for different sections of the analysis
    tab1, tab2, tab3 = st.tabs(["Transaction Analysis", "Applicable Standards", "Detailed Rationale"])
    
    with tab1:
        st.subheader("Transaction Summary")
        st.markdown(f"""
        <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin-bottom: 15px;">
            {results.get("transaction_summary", "No summary provided.")}
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div style="background-color: #e8f4f8; padding: 15px; border-radius: 5px; margin-top: 20px;">
            <h3 style="margin-top: 0;">Correct Standard: {results.get("correct_standard", "Not determined")}</h3>
        </div>
        """, unsafe_allow_html=True)
    
    with tab2:
        st.subheader("Applicable Standards (Ranked by Probability)")
        
        for standard in results.get("applicable_standards", []):
            # Set color based on probability
            probability = standard.get("probability", "0%")
            prob_value = 0
            
            if isinstance(probability, str):
                # Handle percentage string
                if "%" in probability:
                    try:
                        prob_value = float(probability.strip("%"))
                    except ValueError:
                        pass
                # Handle text-based probability
                elif probability.lower() in ["high", "very high"]:
                    prob_value = 80
                elif probability.lower() == "medium":
                    prob_value = 50
                elif probability.lower() in ["low", "very low"]:
                    prob_value = 20
            
            if prob_value >= 70:
                color = "#d4edda"  # Green for high
            elif prob_value >= 30:
                color = "#fff3cd"  # Yellow for medium
            else:
                color = "#f8d7da"  # Red for low
                
            # Display the standard card
            st.markdown(
                f"""
                <div style="background-color: {color}; padding: 15px; 
                      border-radius: 5px; margin-bottom: 15px;">
                    <h3>{standard.get("standard_id", "")} - {standard.get("name", "")}</h3>
                    <p><b>Probability:</b> {probability}</p>
                    <p><b>Reasoning:</b> {standard.get("reasoning", "No reasoning provided.")}</p>
                </div>
                """, 
                unsafe_allow_html=True
            )
    
    with tab3:
        st.subheader("Standard Application Rationale")
        st.markdown(f"""
        <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin-bottom: 15px; white-space: pre-line;">
            {results.get("standard_rationale", "No detailed rationale provided.")}
        </div>
        """, unsafe_allow_html=True)
        
        # Add a citation/reference section if available
        if results.get("citations"):
            st.subheader("Citations & References")
            for citation in results["citations"]:
                st.markdown(f"- **{citation['source']}:** {citation['text']}")
        
        # Add complete analysis in expander for reference
        if results.get("analysis"):
            with st.expander("Show Complete Analysis", expanded=False):
                st.markdown("```\n" + results["analysis"][:10000] + "\n... [truncated if longer than 10000 chars]```")
        
        # Add retrieval stats for transparency
        if results.get("retrieval_stats"):
            with st.expander("Retrieval Statistics", expanded=False):
                st.markdown(f"**Number of chunks retrieved:** {results['retrieval_stats'].get('chunk_count', 0)}")
                if results['retrieval_stats'].get('chunks_summary'):
                    st.markdown("**Sample chunks:**")
                    for i, chunk in enumerate(results['retrieval_stats']['chunks_summary'][:3]):
                        st.markdown(f"{i+1}. {chunk}")

def display_analysis_results(results):
    """Display single transaction analysis results with feedback collection."""
    st.header("Analysis Results")
    
    # Display the analysis content
    display_analysis_content(results)
    
    # Add feedback buttons at the bottom
    st.markdown("### Was this analysis helpful?")
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("👍 Helpful", key="single_thumbs_up"):
            # Save positive feedback
            feedback_data = {
                "transaction": results.get("transaction_summary", ""),
                "feedback_type": "helpful",
                "rating": "positive"
            }
            save_feedback("transaction_analysis", feedback_data)
            st.success("Thank you for your feedback!")
    
    with col2:
        if st.button("👎 Not Helpful", key="single_thumbs_down"):
            # Save negative feedback
            feedback_data = {
                "transaction": results.get("transaction_summary", ""),
                "feedback_type": "helpful",
                "rating": "negative"
            }
            save_feedback("transaction_analysis", feedback_data)
            st.error("Thank you for your feedback!")

if __name__ == "__main__":
    render_transaction_analysis_page()