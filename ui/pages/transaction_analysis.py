"""
Transaction Analysis page for the Streamlit application (Challenge 2).
"""

import streamlit as st
import sys
import json
from pathlib import Path

# Add the parent directory to the path so we can import from the main project
parent_dir = str(Path(__file__).parent.parent.parent)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Local imports
from ui.styles.main import load_css
from ui.states.session_state import init_transaction_analysis_state, set_transaction_analysis_results, get_transaction_analysis_results

def render_transaction_analysis_page():
    """Render the Transaction Analysis page."""
    # Initialize session state
    init_transaction_analysis_state()
    
    # Set page configuration
    st.set_page_config(
        page_title="Islamic Finance Transaction Analysis",
        page_icon="📝",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Apply CSS
    st.markdown(load_css(), unsafe_allow_html=True)
    
    # Page title
    st.title("📝 Islamic Finance Transaction Analysis")
    st.markdown("### Identify applicable AAOIFI standards from journal entries")
    
    # Sidebar
    st.sidebar.title("Transaction Options")
    
    # Input method selection
    input_method = st.sidebar.radio(
        "Input Method",
        ["Sample Transactions", "Custom Transaction"]
    )
    
    if input_method == "Sample Transactions":
        st.sidebar.markdown("### Sample Transactions")
        # In a real implementation, these would be loaded from a file or database
        sample_transactions = [
            {
                "name": "Partner Equity Buyout",
                "description": "Transaction involves buyout of a partner's stake",
                "journal_entries": [
                    {"account": "Partner's Equity", "debit": 100000, "credit": 0},
                    {"account": "Cash", "debit": 0, "credit": 100000}
                ],
                "context": "Islamic bank buying out a Mudarabah partner's stake."
            },
            {
                "name": "Ijarah Asset Transfer",
                "description": "Transfer of asset at the end of Ijarah term",
                "journal_entries": [
                    {"account": "Ijarah Asset", "debit": 0, "credit": 50000},
                    {"account": "Accumulated Depreciation", "debit": 30000, "credit": 0},
                    {"account": "Cash", "debit": 5000, "credit": 0},
                    {"account": "Gain on Disposal", "debit": 0, "credit": 5000}
                ],
                "context": "Transfer of asset to lessee at the end of Ijarah MBT contract term."
            }
        ]
        
        # Create a dropdown for sample transactions
        transaction_names = [t["name"] for t in sample_transactions]
        selected_idx = st.sidebar.selectbox(
            "Select a Sample Transaction",
            range(len(transaction_names)),
            format_func=lambda i: transaction_names[i]
        )
        
        selected_transaction = sample_transactions[selected_idx]
        
        # Display selected transaction
        st.subheader(f"Transaction: {selected_transaction['name']}")
        st.markdown(f"**Description:** {selected_transaction['description']}")
        st.markdown(f"**Context:** {selected_transaction['context']}")
        
        # Display journal entries
        st.subheader("Journal Entries")
        entries_data = []
        for entry in selected_transaction["journal_entries"]:
            entries_data.append({
                "Account": entry["account"],
                "Debit": f"${entry['debit']:,.2f}" if entry["debit"] > 0 else "",
                "Credit": f"${entry['credit']:,.2f}" if entry["credit"] > 0 else ""
            })
        
        st.table(entries_data)
        
        # Transaction details to analyze
        transaction_details = {
            "name": selected_transaction["name"],
            "context": selected_transaction["context"],
            "journal_entries": selected_transaction["journal_entries"]
        }
        
    else:  # Custom Transaction
        st.sidebar.markdown("### Custom Transaction")
        
        transaction_name = st.sidebar.text_input("Transaction Name", "")
        transaction_context = st.sidebar.text_area(
            "Transaction Context",
            "",
            help="Provide context about the transaction, including its purpose and nature."
        )
        
        # Custom journal entries input
        st.subheader("Journal Entries")
        st.markdown("Enter the journal entries for the transaction:")
        
        # Initialize entries if needed
        if "journal_entries" not in st.session_state:
            st.session_state.journal_entries = [
                {"account": "", "debit": 0, "credit": 0}
            ]
        
        # Function to add a new entry
        def add_entry():
            st.session_state.journal_entries.append({"account": "", "debit": 0, "credit": 0})
        
        # Function to remove an entry
        def remove_entry(idx):
            st.session_state.journal_entries.pop(idx)
        
        # Display entries
        for i, entry in enumerate(st.session_state.journal_entries):
            cols = st.columns([3, 2, 2, 1])
            with cols[0]:
                st.session_state.journal_entries[i]["account"] = st.text_input(
                    "Account", 
                    entry["account"], 
                    key=f"account_{i}"
                )
            with cols[1]:
                st.session_state.journal_entries[i]["debit"] = st.number_input(
                    "Debit", 
                    min_value=0.0, 
                    value=float(entry["debit"]), 
                    key=f"debit_{i}"
                )
            with cols[2]:
                st.session_state.journal_entries[i]["credit"] = st.number_input(
                    "Credit", 
                    min_value=0.0, 
                    value=float(entry["credit"]), 
                    key=f"credit_{i}"
                )
            with cols[3]:
                if i > 0:  # Don't allow removing the first entry
                    st.button("Remove", key=f"remove_{i}", on_click=remove_entry, args=(i,))
        
        # Add entry button
        st.button("Add Entry", on_click=add_entry)
        
        # Validate entries
        total_debits = sum(entry["debit"] for entry in st.session_state.journal_entries)
        total_credits = sum(entry["credit"] for entry in st.session_state.journal_entries)
        
        # Check if entries balance
        if abs(total_debits - total_credits) > 0.01:
            st.warning(f"Journal entries do not balance. Debits: ${total_debits:,.2f}, Credits: ${total_credits:,.2f}")
        else:
            st.success(f"Journal entries balance. Total: ${total_debits:,.2f}")
        
        # Transaction details to analyze
        transaction_details = {
            "name": transaction_name,
            "context": transaction_context,
            "journal_entries": st.session_state.journal_entries
        }
    
    # Analysis button
    analyze_btn = st.button("Analyze Transaction", type="primary")
    
    if analyze_btn:
        if input_method == "Custom Transaction" and (not transaction_details["name"] or not transaction_details["context"]):
            st.error("Please provide a transaction name and context.")
        elif input_method == "Custom Transaction" and abs(total_debits - total_credits) > 0.01:
            st.error("Journal entries must balance before analysis.")
        else:
            with st.spinner("Analyzing transaction..."):
                # In a real implementation, this would call an API or backend function
                # For now, we'll just create a mock response
                
                # Import here to avoid circular imports
                try:
                    # Try to import the actual analyzer if available
                    from components.agents import transaction_analyzer
                    results = transaction_analyzer.analyze_transaction(json.dumps(transaction_details))
                except ImportError:
                    # Mock response for placeholder
                    results = {
                        "analysis": f"Analysis of {transaction_details['name']}:\n\nBased on the journal entries and context provided, this transaction appears to be related to the following Islamic finance concepts:\n\n1. The transaction involves a financial exchange that might be governed by AAOIFI standards.\n2. The nature of the entries suggests a transfer of ownership or rights.",
                        "identified_standards": [
                            {
                                "standard_id": "FAS 28",
                                "name": "Ijarah",
                                "probability": "High",
                                "reasoning": "The entries and context suggest a lease transaction with transfer of ownership (Ijarah Muntahia Bittamleek)."
                            },
                            {
                                "standard_id": "FAS 7",
                                "name": "Musharakah",
                                "probability": "Medium",
                                "reasoning": "The transaction could involve a partnership arrangement given the context."
                            }
                        ]
                    }
                
                # Save results to session state
                set_transaction_analysis_results(results)
                
                # Success message
                st.success("Transaction analysis completed!")
    
    # Display results if available
    results = get_transaction_analysis_results()
    if results:
        st.header("Analysis Results")
        
        # Display analysis
        st.subheader("Transaction Analysis")
        st.markdown(f'<div class="review-container">{results["analysis"]}</div>', unsafe_allow_html=True)
        
        # Display identified standards
        st.subheader("Identified Standards")
        
        for standard in results["identified_standards"]:
            # Set color based on probability
            color = "#f8d7da"  # Red for low
            if standard["probability"].lower() == "high":
                color = "#d4edda"  # Green for high
            elif standard["probability"].lower() == "medium":
                color = "#fff3cd"  # Yellow for medium
                
            # Display the standard card
            st.markdown(
                f"""
                <div style="background-color: {color}; padding: 15px; 
                      border-radius: 5px; margin-bottom: 10px;">
                    <h3>{standard["standard_id"]} - {standard.get("name", "")}</h3>
                    <p><b>Probability:</b> {standard["probability"]}</p>
                    <p><b>Reasoning:</b> {standard["reasoning"]}</p>
                </div>
                """, 
                unsafe_allow_html=True
            )

if __name__ == "__main__":
    render_transaction_analysis_page() 