from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage

from state import State
from tools.index import tools
import os
from dotenv import load_dotenv
from base_prompt import SYSTEM_PROMPT

load_dotenv()
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-preview-04-17",
    api_key=os.environ["GEMINI_API_KEY"],
)

llm_with_tools = llm.bind_tools(tools)


def chatbot(state: State):
    # Create a copy of the messages list to avoid modifying the original
    messages = state["messages"].copy()
    
    # Insert the system message at the beginning if it doesn't already exist
    if not messages or not (
        hasattr(messages[0], "type") and messages[0].type == "system"
    ):
        messages.insert(0, SystemMessage(content=SYSTEM_PROMPT))
    
    # Process with model and return response
    return {"messages": [llm_with_tools.invoke(messages)]}
