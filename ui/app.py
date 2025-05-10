"""
Main Streamlit application for the Islamic Finance Standards Multi-Agent System.
This is the home page and navigation hub for the different challenges.
"""

import streamlit as st
import sys
import os
from pathlib import Path

# Add the parent directory to the path so we can import from the main project
parent_dir = str(Path(__file__).parent.parent)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Local imports
from styles.main import load_css
from pages.standards_enhancement import render_standards_enhancement_page
from states.session_state import init_all_states, set_current_page, get_current_page
# Imp page rendering functions
from pages.transaction_analysis import render_transaction_analysis_page
from pages.use_case_processor import render_use_case_processor_page

def main():
    """Main function for the Streamlit application."""
    # Initialize all session states
    init_all_states()
    
    # Set page configuration
    st.set_page_config(
        page_title="Islamic Finance Standards System",
        page_icon="🏦",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Apply CSS
    st.markdown(load_css(), unsafe_allow_html=True)
    
    # Header
    st.title("Islamic Finance Standards Multi-Agent System")
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    
    pages = {
        "home": "🏠 Home",
        "use_case_processor": "📒 Use Case Processor (Challenge 1)",
        "transaction_analysis": "📝 Transaction Analysis (Challenge 2)",
        "standards_enhancement": "📊 Standards Enhancement (Challenge 3)"
    }
    
    selected_page = st.sidebar.radio("Select a Page", list(pages.values()))
    
    # Set the current page in the session state
    for key, value in pages.items():
        if value == selected_page:
            set_current_page(key)
    
    # Display the selected page
    current_page = get_current_page()
    
    if current_page == "home":
        render_home_page()
    elif current_page == "standards_enhancement":
        render_standards_enhancement_page()
    elif current_page == "transaction_analysis":
        render_transaction_analysis_page()
    elif current_page == "use_case_processor":
        render_use_case_processor_page()

def render_home_page():
    """Render the home page of the application."""
    st.markdown("""
    Welcome to the Islamic Finance Standards Multi-Agent System, a comprehensive solution for 
    working with AAOIFI Financial Accounting Standards (FAS).
    
    This system addresses three key challenges in Islamic finance:
    """)
    
    # Create columns for the challenge cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="border-radius: 10px; border: 1px solid #e0e0e0; padding: 20px; margin: 10px; text-align: center; height: 350px; background-color: #f0f9ff;">
            <h3>📒 Challenge 1: Use Case Processor</h3>
            <p style="text-align: left;">Generate accounting guidance for Islamic finance scenarios:</p>
            <ul style="text-align: left;">
                <li>Process practical financial scenarios</li>
                <li>Apply AAOIFI standards to specific use cases</li>
                <li>Generate journal entries and accounting treatment</li>
                <li>Provide detailed explanations and calculations</li>
            </ul>
            <div style="position: absolute; bottom: 20px; left: 0; right: 0; text-align: center;">
                <a href="#" onclick="parent.document.getElementsByClassName('st-bk')[1].click(); return false;" 
                   style="background-color: #3b82f6; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                   Launch Use Case Processor
                </a>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="border-radius: 10px; border: 1px solid #e0e0e0; padding: 20px; margin: 10px; text-align: center; height: 350px; background-color: #f0fdf4;">
            <h3>📝 Challenge 2: Transaction Analysis</h3>
            <p style="text-align: left;">Identify applicable AAOIFI standards from journal entries:</p>
            <ul style="text-align: left;">
                <li>Analyze journal entries and transaction details</li>
                <li>Identify applicable FAS standards</li>
                <li>Provide reasoning and confidence levels</li>
                <li>Offer accounting guidance based on identified standards</li>
            </ul>
            <div style="position: absolute; bottom: 20px; left: 0; right: 0; text-align: center;">
                <a href="#" onclick="parent.document.getElementsByClassName('st-bk')[2].click(); return false;" 
                   style="background-color: #22c55e; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                   Launch Transaction Analysis
                </a>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="border-radius: 10px; border: 1px solid #e0e0e0; padding: 20px; margin: 10px; text-align: center; height: 350px; background-color: #fff7ed;">
            <h3>📊 Challenge 3: Standards Enhancement</h3>
            <p style="text-align: left;">Enhance AAOIFI standards for modern scenarios:</p>
            <ul style="text-align: left;">
                <li>Analyze standards for enhancement opportunities</li>
                <li>Propose specific changes to standards text</li>
                <li>Validate proposals against Shariah principles</li>
                <li>Analyze cross-standard impacts and compatibility</li>
            </ul>
            <div style="position: absolute; bottom: 20px; left: 0; right: 0; text-align: center;">
                <a href="#" onclick="parent.document.getElementsByClassName('st-bk')[3].click(); return false;" 
                   style="background-color: #f59e0b; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                   Launch Standards Enhancement
                </a>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # System architecture
    st.header("System Architecture")
    st.markdown("""
    This system uses a multi-agent architecture powered by Large Language Models to process and analyze
    Islamic finance standards and scenarios. The architecture includes:
    
    1. **Orchestrator Agent** - Routes user queries to specialized agents
    2. **Standards Extractor Agent** - Extracts relevant information from AAOIFI standards
    3. **Use Case Processor Agent** - Analyzes financial scenarios and provides accounting guidance
    4. **Transaction Analyzer Agent** - Identifies applicable standards from journal entries
    5. **Standards Enhancement Agent** - Proposes improvements to existing standards
    
    The system is integrated with a vector database containing AAOIFI standards for accurate referencing
    and uses retrieval-augmented generation (RAG) to ensure compliance with Shariah principles.
    """)

if __name__ == "__main__":
    main() 