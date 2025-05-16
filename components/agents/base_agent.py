from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import List, Dict, Any, Optional
import os
from dotenv import load_dotenv

# Set up logging
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

# Load environment variables
load_dotenv()

# Base LLM setup
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-preview-04-17",
    api_key=os.environ["GEMINI_API_KEY"],
)


class Agent:
    """Base Agent class that all specialized agents will inherit from."""

    def __init__(self, system_prompt: str, tools: Optional[List] = None):
        self.system_prompt = system_prompt
        self.memory = []

        # Set up LLM with or without tools
        if tools:
            self.llm = llm.bind_tools(tools)
        else:
            self.llm = llm

    def __call__(self, state) -> Dict[str, Any]:
        """Process the current state and return a response."""
        # Create a copy of the messages list
        messages = state["messages"].copy()

        # Insert the system message if it doesn't exist
        if not messages or not (
            hasattr(messages[0], "type") and messages[0].type == "system"
        ):
            messages.insert(0, SystemMessage(content=self.system_prompt))

        # Process with model and return response
        response = self.llm.invoke(messages)
        return {"messages": [response]}

    def add_to_memory(self, message):
        """Add a message to agent's memory."""
        self.memory.append(message)
