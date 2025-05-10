"""
Use Case Processor page for the Streamlit application (Challenge 1).
"""

import streamlit as st
import sys
from pathlib import Path

# Add the parent directory to the path so we can import from the main project
parent_dir = str(Path(__file__).parent.parent.parent)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Local imports
from ui.styles.main import load_css
from ui.state.session_state import init_use_case_state, set_use_case_results, get_use_case_results

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
        # In a real implementation, these would be loaded from a file or database
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
            }
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
    
    # Process button
    process_btn = st.button("Generate Accounting Guidance", type="primary")
    
    if process_btn:
        if not scenario_text:
            st.error("Please provide a scenario description.")
        else:
            with st.spinner("Generating accounting guidance..."):
                # In a real implementation, this would call an API or backend function
                # For now, we'll just create a mock response
                
                # Import here to avoid circular imports
                try:
                    # Try to import the actual processor if available
                    from components.agents import use_case_processor
                    results = use_case_processor.process_use_case(scenario_text)
                except ImportError:
                    # Mock response for placeholder
                    if "Ijarah" in scenario_text:
                        results = {
                            "identified_product": "Ijarah Muntahia Bittamleek (IMB)",
                            "applicable_standards": ["FAS 28 - Ijarah"],
                            "accounting_guidance": """
                            ## Accounting Treatment for Ijarah Muntahia Bittamleek (IMB)
                            
                            Based on the scenario described and according to FAS 28 (Ijarah), the following accounting treatment should be applied:
                            
                            ### Initial Recognition
                            
                            1. The cost of the generator includes the purchase price plus import tax and freight charges:
                               - Purchase price: $450,000
                               - Import tax: $12,000
                               - Freight charges: $30,000
                               - Total cost: $492,000
                            
                            2. Since this is an Ijarah Muntahia Bittamleek arrangement:
                               - The asset should be recognized at cost minus the nominal transfer amount
                               - Right-of-Use (ROU) asset value: $492,000 - $3,000 = $489,000
                               - Deferred Ijarah Cost (representing future rentals): $600,000 - $489,000 = $111,000
                            
                            ### Journal Entries
                            
                            **Initial Recognition:**
                            ```
                            Dr. Right of Use Asset (ROU)    $489,000
                            Dr. Deferred Ijarah Cost        $111,000
                               Cr. Ijarah Liability         $600,000
                            ```
                            
                            **First Year Annual Rental Payment:**
                            ```
                            Dr. Ijarah Liability            $300,000
                               Cr. Cash                      $300,000
                            ```
                            
                            **First Year Amortization of ROU Asset:**
                            Amortizable amount: $489,000 - $5,000 (residual) = $484,000
                            Annual amortization: $484,000 ÷ 2 years = $242,000
                            
                            ```
                            Dr. Amortization Expense        $242,000
                               Cr. Accumulated Amortization  $242,000
                            ```
                            
                            ### Notes
                            
                            - The deferred Ijarah cost represents the difference between the total Ijarah payments and the cost of the asset (minus nominal transfer amount).
                            - The asset is amortized over the Ijarah term, considering the residual value.
                            - According to FAS 28, the entity should assess the ROU asset for impairment at each reporting date.
                            """
                        }
                    elif "Musharakah" in scenario_text:
                        results = {
                            "identified_product": "Musharakah (Partnership)",
                            "applicable_standards": ["FAS 4 - Musharakah"],
                            "accounting_guidance": """
                            ## Accounting Treatment for Musharakah Profit Distribution
                            
                            Based on the scenario described and according to FAS 4 (Musharakah), the following accounting treatment should be applied:
                            
                            ### Profit Distribution Calculation
                            
                            1. Total profit generated: $120,000
                            2. Profit distribution ratio per agreement: 70:30 (bank:partner)
                            3. Bank's share of profit: $120,000 × 70% = $84,000
                            4. Partner's share of profit: $120,000 × 30% = $36,000
                            
                            ### Journal Entries
                            
                            **Initial Investment:**
                            ```
                            Dr. Musharakah Investment      $800,000
                               Cr. Cash                     $800,000
                            ```
                            
                            **Profit Recognition:**
                            ```
                            Dr. Musharakah Profit Receivable  $84,000
                               Cr. Income from Musharakah      $84,000
                            ```
                            
                            **Profit Collection (assuming profit is distributed):**
                            ```
                            Dr. Cash                        $84,000
                               Cr. Musharakah Profit Receivable $84,000
                            ```
                            
                            ### Notes
                            
                            - According to FAS 4, the Islamic bank's share in the Musharakah capital is recognized when it is paid to the partner or made available for use in the Musharakah venture.
                            - The bank's share of profits is recognized in the period in which they are earned.
                            - The bank's share of losses is recognized in the period in which they occur.
                            - If the Musharakah continues for more than one financial period, the bank's share of profits for each period is recognized to the extent that profits are distributed.
                            """
                        }
                    else:
                        results = {
                            "identified_product": "Generic Islamic Financial Product",
                            "applicable_standards": ["To be determined based on specific details"],
                            "accounting_guidance": """
                            ## Accounting Guidance
                            
                            To provide specific accounting guidance for this scenario, more details would be needed about:
                            
                            1. The specific Islamic financial product involved
                            2. Terms and conditions of the arrangement
                            3. Amounts and payment schedules
                            4. Duration of the arrangement
                            
                            Generally, the accounting treatment would involve:
                            
                            1. Initial recognition of the financial instrument
                            2. Subsequent measurement
                            3. Profit/loss recognition
                            4. Disclosure requirements
                            
                            Please provide additional details for more specific guidance.
                            """
                        }
                
                # Save results to session state
                set_use_case_results(results)
                
                # Success message
                st.success("Accounting guidance generated successfully!")
    
    # Display results if available
    results = get_use_case_results()
    if results:
        st.header("Accounting Guidance")
        
        st.subheader("Identified Product")
        st.markdown(f"**{results['identified_product']}**")
        
        st.subheader("Applicable Standards")
        for standard in results["applicable_standards"]:
            st.markdown(f"- {standard}")
        
        st.subheader("Accounting Treatment")
        st.markdown(f'<div class="proposal-container">{results["accounting_guidance"]}</div>', unsafe_allow_html=True)
        
        # Export option
        st.download_button(
            label="Export as Markdown",
            data=f"""# Accounting Guidance for {results['identified_product']}

## Applicable Standards
{chr(10).join(['- ' + std for std in results['applicable_standards']])}

## Accounting Treatment
{results['accounting_guidance']}
""",
            file_name="accounting_guidance.md",
            mime="text/markdown"
        )

if __name__ == "__main__":
    render_use_case_processor_page() 