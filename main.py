import os
from typing import Dict, List, Any
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from agent_graph import agent_graph
from state import create_empty_state
from agents import orchestrator, standards_extractor, use_case_processor

# Load environment variables
load_dotenv()


def process_query(query: str) -> AIMessage:
    """
    Process a user query through the multi-agent system.
    
    Args:
        query: The user's query about Islamic finance standards or scenarios.
        
    Returns:
        AIMessage: The response from the agent system.
    """
    # Create a new message
    message = HumanMessage(content=query)
    
    # Create initial state with the user message
    state = create_empty_state()
    state["messages"] = [message]
    
    # Process the message through the agent graph
    result = agent_graph.invoke(state)
    
    # Extract and return the AI's response
    messages = result["messages"]
    return messages[-1] if messages else AIMessage(content="No response was generated.")


def run_interactive_session():
    """
    Run an interactive session with the multi-agent system.
    """
    print("Islamic Finance Standards Multi-Agent System")
    print("===========================================")
    print("Type 'exit' to quit.")
    print("\nAvailable commands:")
    print("- /standards <id>: Get information about a specific standard (e.g., /standards 28)")
    print("- /agents: List the available agents")
    print("- /clear: Clear the conversation history")
    print()
    
    while True:
        query = input("\nYou: ")
        
        if query.lower() in ["exit", "quit", "q"]:
            print("Goodbye!")
            break
        
        elif query.lower() == "/agents":
            print("\nAvailable Agents:")
            print("1. Orchestrator Agent - Coordinates agent interactions and routes queries")
            print("2. Standards Extractor Agent - Extracts information from AAOIFI standards")
            print("3. Use Case Processor Agent - Analyzes financial scenarios and provides accounting guidance")
            continue
            
        elif query.lower() == "/clear":
            os.system('cls' if os.name == 'nt' else 'clear')
            print("Conversation cleared.")
            continue
            
        elif query.lower().startswith("/standards "):
            # Extract standard ID
            std_id = query.split(" ")[1].strip()
            print(f"\nFetching information about FAS {std_id}...")
            
            # Create a more specific query for standards information
            query = f"Please provide detailed information about AAOIFI Financial Accounting Standard (FAS) {std_id}."
        
        # Process the query through our agent system
        try:
            response = process_query(query)
            print(f"\nAssistant: {response.content}")
        except Exception as e:
            print(f"\nError processing query: {e}")
            print("Please try again with a different query.")


def sample_queries() -> List[Dict[str, str]]:
    """
    Return a list of sample queries to test the system.
    """
    return [
        {
            "name": "Basic Ijarah Scenario",
            "query": """
            A bank enters into an Ijarah agreement with a customer for equipment 
            valued at $100,000 for a 5-year lease term with annual payments of $25,000. 
            How should the bank account for this transaction according to AAOIFI standards?
            """
        },
        {
            "name": "Murabaha Transaction",
            "query": """
            A customer approaches an Islamic bank to finance the purchase of a vehicle 
            worth $50,000. The bank agrees to purchase the vehicle and sell it to the 
            customer at a marked-up price of $55,000, to be paid in 12 monthly installments.
            What are the journal entries for this Murabaha transaction?
            """
        },
        {
            "name": "Specific Standard Information",
            "query": "What are the key requirements in FAS 28 for Murabaha accounting?"
        },
        {
            "name": "Multiple Standards Scenario",
            "query": """
            A company needs to acquire manufacturing equipment worth $500,000. They are 
            considering either an Ijarah arrangement or an Istisna'a contract. What are 
            the accounting implications of each approach according to AAOIFI standards?
            """
        }
    ]


def run_sample_tests():
    """
    Run a series of sample tests to demonstrate the system capabilities.
    """
    samples = sample_queries()
    
    for i, sample in enumerate(samples, 1):
        print(f"\n\n===== SAMPLE TEST {i}: {sample['name']} =====\n")
        print(f"Query: {sample['query'].strip()}")
        print("\n----- RESPONSE -----")
        
        try:
            response = process_query(sample['query'])
            print(response.content)
        except Exception as e:
            print(f"Error processing sample: {e}")
        
        print("\n==========================================================")
        
        # Ask if user wants to continue with next sample
        if i < len(samples):
            cont = input("\nContinue to next sample? (y/n): ")
            if cont.lower() not in ['y', 'yes']:
                break


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Islamic Finance Standards Multi-Agent System")
    parser.add_argument("--samples", action="store_true", help="Run sample test queries")
    args = parser.parse_args()
    
    if args.samples:
        run_sample_tests()
    else:
        run_interactive_session()