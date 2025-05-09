from sqlite3 import Connection
from langgraph.checkpoint.sqlite import SqliteSaver

memory = SqliteSaver(conn=Connection("memory.db", check_same_thread=False))
