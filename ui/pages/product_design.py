"""
Financial Product Design page for the Streamlit application (Challenge 4).
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

# Add the parent directory to the path so we can import from the main project
parent_dir = str(Path(__file__).parent.parent.parent)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Local imports
from ui.styles.main import load_css
from ui.states.session_state import (
    init_product_design_state, 
    set_product_design_results, 
    get_product_design_results,
    add_saved_design,
    get_saved_designs
)
from ui.utils.product_design_utils import design_product, save_product_design, load_past_designs
from models.product_design import (
    ISLAMIC_CONTRACTS,
    PRODUCT_FEATURE_OPTIONS,
    RISK_APPETITE_LEVELS,
    INVESTMENT_TENOR_OPTIONS,
    TARGET_AUDIENCE_OPTIONS,
    ASSET_FOCUS_OPTIONS
)

def render_product_design_page(standalone=False):
    """Render the Financial Product Design page for Challenge 4."""
    # Initialize session state
    init_product_design_state()
    
    # Set page configuration only if running in standalone mode
    if standalone:
        st.set_page_config(
            page_title="Islamic Finance Product Design",
            page_icon="💼",
            layout="wide",
            initial_sidebar_state="expanded"
        )
    
    # Apply CSS
    st.markdown(load_css(), unsafe_allow_html=True)
    
    # Page title and description
    st.title("💼 Financial Product Design Advisor")
    st.markdown("""
    ### Design Shariah-compliant financial products aligned with AAOIFI standards
    
    This advisor helps you conceptualize new Islamic financial products based on your requirements. 
    It suggests suitable Islamic contract structures, highlights relevant AAOIFI FAS implications, 
    and provides initial Shariah compliance considerations.
    """)
    
    # Create sidebar for options
    st.sidebar.title("Design Options")
    
    # Mode selection
    mode = st.sidebar.radio(
        "Mode",
        ["New Product Design", "View Saved Designs"]
    )
    
    if mode == "New Product Design":
        render_new_design_form()
    else:
        render_saved_designs()

def render_new_design_form():
    """Render the form for creating a new product design."""
    # Create form container
    with st.form("product_design_form"):
        st.subheader("Product Requirements")
        
        # Main requirements section
        col1, col2 = st.columns(2)
        
        with col1:
            product_objective = st.text_input(
                "Product Objective",
                placeholder="e.g., Capital growth investment, Asset financing, etc."
            )
            
            risk_appetite = st.radio(
                "Risk Appetite",
                options=RISK_APPETITE_LEVELS
            )
            
            investment_tenor = st.selectbox(
                "Investment Tenor",
                options=INVESTMENT_TENOR_OPTIONS
            )
        
        with col2:
            target_audience = st.selectbox(
                "Target Audience",
                options=TARGET_AUDIENCE_OPTIONS
            )
            
            asset_focus = st.selectbox(
                "Asset Focus (optional)",
                options=ASSET_FOCUS_OPTIONS
            )
        
        # Features section
        st.subheader("Product Features")
        
        desired_features = st.multiselect(
            "Desired Features",
            options=PRODUCT_FEATURE_OPTIONS,
            default=["Asset-backed"]
        )
        
        specific_exclusions = st.multiselect(
            "Specific Exclusions (optional)",
            options=[
                "Avoid contracts involving significant debt",
                "Prefer non-speculative instruments",
                "Avoid high market risk exposure",
                "Minimal currency risk",
                "Avoid complex multi-layer structures"
            ]
        )
        
        # Additional notes
        additional_notes = st.text_area(
            "Additional Requirements or Notes (optional)",
            placeholder="Enter any additional specific requirements or constraints..."
        )
        
        # Submit button
        submit_button = st.form_submit_button("Design Product", type="primary")
    
    # Handle form submission
    if submit_button:
        if not product_objective:
            st.error("Please provide a product objective.")
        else:
            with st.spinner("Designing your product..."):
                # Prepare input data
                input_data = {
                    "product_objective": product_objective,
                    "risk_appetite": risk_appetite,
                    "investment_tenor": investment_tenor,
                    "target_audience": target_audience,
                    "asset_focus": asset_focus,
                    "desired_features": desired_features,
                    "specific_exclusions": specific_exclusions,
                    "additional_notes": additional_notes
                }
                
                # Call the product design function
                results = design_product(input_data)
                
                # Save results to session state
                set_product_design_results(results)
                
                # Display success message
                st.success("Product design completed!")
    
    # Display results if available
    results = get_product_design_results()
    if results:
        display_design_results(results)

def display_design_results(results):
    """Display the product design results."""
    st.markdown("---")
    
    # Summary section
    st.header(f"💼 {results['suggested_product_concept_name']}")
    
    # Create tabs for different sections
    tabs = st.tabs([
        "Product Overview", 
        "Structure & Contracts", 
        "AAOIFI Standards", 
        "Shariah Compliance", 
        "Implementation Steps"
    ])
    
    # Tab 1: Product Overview
    with tabs[0]:
        st.subheader("Product Concept Summary")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Based on:** {', '.join(results['recommended_islamic_contracts'])}")
            st.markdown(f"**Risk Profile:** {results.get('original_requirements', {}).get('risk_appetite', 'Not specified')}")
            st.markdown(f"**Target Audience:** {results.get('original_requirements', {}).get('target_audience', 'Not specified')}")
        
        with col2:
            st.markdown(f"**Investment Tenor:** {results.get('original_requirements', {}).get('investment_tenor', 'Not specified')}")
            st.markdown(f"**Asset Focus:** {results.get('original_requirements', {}).get('asset_focus', 'Not specified')}")
        
        st.subheader("Contract Selection Rationale")
        st.markdown(results["rationale_for_contract_selection"])
        
        # Save button
        if st.button("💾 Save Design"):
            # Create a summary of the design for saving
            design_summary = {
                "id": f"design_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "name": results['suggested_product_concept_name'],
                "date_created": datetime.now().strftime("%Y-%m-%d"),
                "contract_type": ", ".join(results['recommended_islamic_contracts']),
                "risk_profile": results.get('original_requirements', {}).get('risk_appetite', 'Not specified'),
                "full_design": results
            }
            
            # Add to saved designs
            add_saved_design(design_summary)
            
            # Show success message
            st.success("Design saved successfully!")
    
    # Tab 2: Structure & Contracts
    with tabs[1]:
        st.subheader("Product Structure")
        st.markdown(results["proposed_product_structure_overview"])
        
        # Add a visual diagram of the structure
        st.subheader("Structure Diagram")
        display_structure_diagram(results)
        
        # Show contract information
        st.subheader("Contract Information")
        for contract in results["recommended_islamic_contracts"]:
            if contract in ISLAMIC_CONTRACTS:
                contract_info = ISLAMIC_CONTRACTS[contract]
                with st.expander(f"{contract} Details", expanded=True):
                    st.markdown(f"**Description:** {contract_info['description']}")
                    st.markdown(f"**Risk Profile:** {contract_info['risk_profile']}")
                    st.markdown("**Suitable For:**")
                    for use_case in contract_info['suitable_for']:
                        st.markdown(f"- {use_case}")
                    st.markdown(f"**Primary Standard:** {contract_info['primary_standard']}")
    
    # Tab 3: AAOIFI Standards
    with tabs[2]:
        st.subheader("Key AAOIFI Standards Considerations")
        
        # Loop through the standards information for each contract
        for std_id, info in results["key_aaoifi_fas_considerations"].items():
            with st.expander(f"FAS {std_id} Considerations", expanded=True):
                st.markdown(info)
    
    # Tab 4: Shariah Compliance
    with tabs[3]:
        st.subheader("Shariah Compliance Checkpoints")
        
        for checkpoint in results["shariah_compliance_checkpoints"]:
            st.markdown(f"✓ {checkpoint}")
        
        st.subheader("Potential Areas of Concern")
        
        for concern in results["potential_areas_of_concern"]:
            st.markdown(f"⚠️ {concern}")
        
        st.subheader("Risk Mitigation")
        st.markdown(results["potential_risks_and_mitigation_notes"])
    
    # Tab 5: Implementation Steps
    with tabs[4]:
        st.subheader("Next Steps for Detailed Design")
        
        # Create a timeline chart
        steps = results["next_steps_for_detailed_design"]
        if steps:
            # Create a dataframe for the timeline
            timeline_df = pd.DataFrame({
                'Task': steps,
                'Start': range(len(steps)),
                'Duration': [1] * len(steps)
            })
            
            # Create a Gantt chart
            fig = px.timeline(
                timeline_df, 
                x_start="Start", 
                x_end=timeline_df["Start"] + timeline_df["Duration"], 
                y="Task",
                color_discrete_sequence=["#3b82f6"]
            )
            
            fig.update_layout(
                title="Implementation Timeline",
                xaxis_title="Weeks",
                yaxis_title="",
                height=300,
                margin=dict(l=10, r=10, t=40, b=10)
            )
            
            # Display the chart
            st.plotly_chart(fig, use_container_width=True)
        
        # Display the steps as a list
        for i, step in enumerate(steps, 1):
            st.markdown(f"**Step {i}:** {step}")
        
        # Add a downloadable report option
        st.markdown("### Generate Implementation Report")
        st.markdown("Download a detailed implementation roadmap for your product design.")
        
        if st.button("📄 Generate Implementation Roadmap"):
            st.info("Implementation roadmap generation would be implemented in a production version.")

def display_structure_diagram(results):
    """Display a visual diagram of the product structure."""
    # Get the contract type
    contracts = results.get("recommended_islamic_contracts", ["Unknown"])
    contract_type = contracts[0] if contracts else "Unknown"
    
    # Create a simple flow diagram based on the contract type
    if contract_type in ["Mudarabah", "Musharakah"]:
        create_partnership_diagram(contract_type, results)
    elif contract_type in ["Ijarah", "Ijarah Muntahia Bittamleek"]:
        create_lease_diagram(contract_type, results)
    elif contract_type in ["Murabaha"]:
        create_sale_diagram(contract_type, results)
    else:
        create_generic_diagram(contract_type, results)

def create_partnership_diagram(contract_type, results):
    """Create a diagram for partnership-based contracts."""
    # Create nodes and edges for the diagram
    nodes = ["Investors", "Islamic Bank", "Investment Pool", "Projects/Assets", "Returns"]
    
    # Create a figure
    fig = go.Figure()
    
    # Define node positions
    x_positions = [1, 3, 5, 7, 5]
    y_positions = [1, 1, 1, 1, -1]
    
    # Add nodes
    for i, node in enumerate(nodes):
        fig.add_trace(go.Scatter(
            x=[x_positions[i]],
            y=[y_positions[i]],
            mode="markers+text",
            marker=dict(size=30, color="#3b82f6"),
            text=node,
            textposition="bottom center",
            name=node
        ))
    
    # Add edges (arrows)
    # Investors to Bank
    add_arrow(fig, x_positions[0], y_positions[0], x_positions[1], y_positions[1], "Capital")
    
    # Bank to Investment Pool
    add_arrow(fig, x_positions[1], y_positions[1], x_positions[2], y_positions[2], "Management")
    
    # Investment Pool to Projects
    add_arrow(fig, x_positions[2], y_positions[2], x_positions[3], y_positions[3], "Investment")
    
    # Projects to Returns
    add_arrow(fig, x_positions[3], y_positions[3], x_positions[4], y_positions[4], "Profits")
    
    # Returns to Bank
    add_arrow(fig, x_positions[4], y_positions[4], x_positions[1], y_positions[1], "Share")
    
    # Returns to Investors
    add_arrow(fig, x_positions[1], y_positions[1], x_positions[0], y_positions[0], "Distribution")
    
    # Update layout
    fig.update_layout(
        title=f"{contract_type} Structure",
        showlegend=False,
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        plot_bgcolor="rgba(0,0,0,0)",
        height=400,
        width=800,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    
    # Display the figure
    st.plotly_chart(fig, use_container_width=True)

def create_lease_diagram(contract_type, results):
    """Create a diagram for lease-based contracts."""
    # Create nodes and edges for the diagram
    nodes = ["Islamic Bank (Lessor)", "Client (Lessee)", "Asset", "Rental Payments"]
    
    # Create a figure
    fig = go.Figure()
    
    # Define node positions
    x_positions = [1, 5, 3, 3]
    y_positions = [1, 1, 3, -1]
    
    # Add nodes
    for i, node in enumerate(nodes):
        fig.add_trace(go.Scatter(
            x=[x_positions[i]],
            y=[y_positions[i]],
            mode="markers+text",
            marker=dict(size=30, color="#22c55e"),
            text=node,
            textposition="bottom center",
            name=node
        ))
    
    # Add edges (arrows)
    # Bank to Asset (Ownership)
    add_arrow(fig, x_positions[0], y_positions[0], x_positions[2], y_positions[2], "Ownership")
    
    # Asset to Client (Usufruct)
    add_arrow(fig, x_positions[2], y_positions[2], x_positions[1], y_positions[1], "Usufruct")
    
    # Client to Rental Payments
    add_arrow(fig, x_positions[1], y_positions[1], x_positions[3], y_positions[3], "Pays")
    
    # Rental Payments to Bank
    add_arrow(fig, x_positions[3], y_positions[3], x_positions[0], y_positions[0], "Receives")
    
    # Add transfer of ownership for IMB
    if contract_type == "Ijarah Muntahia Bittamleek":
        add_arrow(fig, x_positions[0], y_positions[0], x_positions[1], y_positions[1], "Transfer at end")
    
    # Update layout
    fig.update_layout(
        title=f"{contract_type} Structure",
        showlegend=False,
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        plot_bgcolor="rgba(0,0,0,0)",
        height=400,
        width=800,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    
    # Display the figure
    st.plotly_chart(fig, use_container_width=True)

def create_sale_diagram(contract_type, results):
    """Create a diagram for sale-based contracts."""
    # Create nodes and edges for the diagram
    nodes = ["Islamic Bank", "Supplier", "Asset", "Client", "Payments"]
    
    # Create a figure
    fig = go.Figure()
    
    # Define node positions
    x_positions = [3, 1, 3, 5, 3]
    y_positions = [1, 3, 3, 3, -1]
    
    # Add nodes
    for i, node in enumerate(nodes):
        fig.add_trace(go.Scatter(
            x=[x_positions[i]],
            y=[y_positions[i]],
            mode="markers+text",
            marker=dict(size=30, color="#f59e0b"),
            text=node,
            textposition="bottom center",
            name=node
        ))
    
    # Add edges (arrows)
    # Bank to Supplier (Cash)
    add_arrow(fig, x_positions[0], y_positions[0], x_positions[1], y_positions[1], "Cash")
    
    # Supplier to Asset (Sells)
    add_arrow(fig, x_positions[1], y_positions[1], x_positions[2], y_positions[2], "Sells")
    
    # Asset to Bank (Ownership)
    add_arrow(fig, x_positions[2], y_positions[2], x_positions[0], y_positions[0], "Ownership")
    
    # Bank to Client (Sells at markup)
    add_arrow(fig, x_positions[0], y_positions[0], x_positions[3], y_positions[3], "Sells at markup")
    
    # Client to Payments
    add_arrow(fig, x_positions[3], y_positions[3], x_positions[4], y_positions[4], "Pays")
    
    # Payments to Bank
    add_arrow(fig, x_positions[4], y_positions[4], x_positions[0], y_positions[0], "Receives")
    
    # Update layout
    fig.update_layout(
        title=f"{contract_type} Structure",
        showlegend=False,
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        plot_bgcolor="rgba(0,0,0,0)",
        height=400,
        width=800,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    
    # Display the figure
    st.plotly_chart(fig, use_container_width=True)

def create_generic_diagram(contract_type, results):
    """Create a generic diagram for other contract types."""
    # Create nodes and edges for the diagram
    nodes = ["Islamic Bank", "Client", "Asset/Project", "Cash Flow"]
    
    # Create a figure
    fig = go.Figure()
    
    # Define node positions
    x_positions = [1, 5, 3, 3]
    y_positions = [1, 1, 3, -1]
    
    # Add nodes
    for i, node in enumerate(nodes):
        fig.add_trace(go.Scatter(
            x=[x_positions[i]],
            y=[y_positions[i]],
            mode="markers+text",
            marker=dict(size=30, color="#a855f7"),
            text=node,
            textposition="bottom center",
            name=node
        ))
    
    # Add edges (arrows)
    # Bank to Asset
    add_arrow(fig, x_positions[0], y_positions[0], x_positions[2], y_positions[2], "Finances")
    
    # Client to Asset
    add_arrow(fig, x_positions[1], y_positions[1], x_positions[2], y_positions[2], "Utilizes")
    
    # Asset to Cash Flow
    add_arrow(fig, x_positions[2], y_positions[2], x_positions[3], y_positions[3], "Generates")
    
    # Cash Flow to Bank
    add_arrow(fig, x_positions[3], y_positions[3], x_positions[0], y_positions[0], "Returns")
    
    # Cash Flow to Client
    add_arrow(fig, x_positions[3], y_positions[3], x_positions[1], y_positions[1], "Returns")
    
    # Update layout
    fig.update_layout(
        title=f"{contract_type} Structure",
        showlegend=False,
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        plot_bgcolor="rgba(0,0,0,0)",
        height=400,
        width=800,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    
    # Display the figure
    st.plotly_chart(fig, use_container_width=True)

def add_arrow(fig, x_start, y_start, x_end, y_end, label=""):
    """Add an arrow to the figure."""
    fig.add_annotation(
        x=x_end,
        y=y_end,
        ax=x_start,
        ay=y_start,
        xref="x",
        yref="y",
        axref="x",
        ayref="y",
        showarrow=True,
        arrowhead=2,
        arrowsize=1,
        arrowwidth=2,
        arrowcolor="#64748b",
        text=label,
        font=dict(size=10),
        textangle=0,
        align="center"
    )

def render_saved_designs():
    """Render the saved designs page."""
    st.subheader("Saved Product Designs")
    
    # Get saved designs
    saved_designs = get_saved_designs()
    
    # If there are no saved designs, load sample designs
    if not saved_designs:
        saved_designs = load_past_designs()
    
    if not saved_designs:
        st.info("No saved designs found. Create a new design to save it here.")
        return
    
    # Display saved designs as cards
    for i, design in enumerate(saved_designs):
        with st.expander(f"{design['name']} ({design['date_created']})", expanded=i==0):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"**Contract Type:** {design['contract_type']}")
                st.markdown(f"**Risk Profile:** {design['risk_profile']}")
                
                # If we have the full design, show a button to view it
                if "full_design" in design:
                    if st.button(f"View Full Design", key=f"view_{design['id']}"):
                        set_product_design_results(design["full_design"])
                        st.experimental_rerun()
            
            with col2:
                # Create a simple pie chart for contract types
                if "contract_type" in design:
                    contract_types = [ct.strip() for ct in design["contract_type"].split(",")]
                    fig = go.Figure(data=[go.Pie(
                        labels=contract_types,
                        values=[1] * len(contract_types),
                        hole=.3
                    )])
                    fig.update_layout(
                        height=150,
                        margin=dict(l=0, r=0, t=0, b=0),
                        showlegend=False
                    )
                    st.plotly_chart(fig, use_container_width=True)

# Add main block to allow running as standalone file
if __name__ == "__main__":
    render_product_design_page(standalone=True)