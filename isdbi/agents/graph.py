from langgraph.graph import StateGraph, END

from state import State
from agent_graph import agent_graph
from memory import memory

# Use our agent graph as the main graph
graph = agent_graph
