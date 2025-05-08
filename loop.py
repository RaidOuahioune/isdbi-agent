from graph import graph
from threads import create_config
import traceback
from db import Database
import os
import uuid
from dotenv import load_dotenv

# Load environment variables 
load_dotenv()

def stream_graph_updates(user_input: str, thread_id: str = "1") -> None:
    # Skip empty messages to avoid Gemini API errors
    if not user_input or not user_input.strip():
        print("Assistant: Please provide a non-empty message.")
        return

    try:
        config = create_config(thread_id)
        # Proper message formatting
        message = {"messages": [{"role": "user", "content": user_input}]}
        
        # Debug info
        print("Sending message to agent...")
        
        response_received = False
        for event in graph.stream(message, config=config):
         
            for key, value in event.items():
             
                
                if "messages" in value:
                    #print(f"Debug - Message count: {len(value['messages'])}")
                    
                    if value["messages"]:
                        last_message = value["messages"][-1]
                        #print(f"Debug - Message type: {type(last_message)}")
                        
                        if hasattr(last_message, 'content') and last_message.content:
                            print("Assistant:", last_message.content)
                            response_received = True
                        elif isinstance(last_message, dict) and "content" in last_message and last_message["content"]:
                            print("Assistant:", last_message["content"])
                            response_received = True
        
        if not response_received:
            print("Debug - No response was generated or printed")
            
    except Exception as e:
        print(f"Error in stream_graph_updates: {str(e)}")
        # Print detailed traceback for debugging
        traceback.print_exc()


def main():
    print("Initializing Fly Numedia Travel Agent...")
    
    # Initialize the database connection pool
    try:
        Database.initialize()
        print("Database initialized successfully.")
    except Exception as e:
        print(f"Database initialization error (falling back to memory storage): {str(e)}")
    
    # Print welcome message
    print("\n" + "="*50)
    print("Welcome to Fly Numedia AI Travel Agent!")
    print("Ask about flights, hotels, or find travel companions with similar interests.")
    print("="*50 + "\n")
    
    thread_id =  uuid.uuid4().hex
    while True:
        try:
            user_input = input("User: ")

            if user_input.lower() in ["quit", "exit", "q"]:
                print("Goodbye!")
                break
            stream_graph_updates(user_input, thread_id)
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            print("Continuing with a new interaction...")

    # Close all database connections when exiting
    try:
        Database.close_all_connections()
    except:
        pass


if __name__ == "__main__":
    main()
