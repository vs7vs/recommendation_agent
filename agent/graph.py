from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage, AIMessage
from typing import TypedDict, Annotated, List
from pydantic import SecretStr

# --- Import project-specific components ---
from agent.config import OPENAI_API_KEY
# vvv FIX IS HERE vvv
from agent.tools import tools, human_feedback_tool # Import the specific tool function

# --- Helper function to create the LLM ---
def _create_llm(tools_to_bind):
    """Creates and configures the LLM, keeping setup logic within this module."""
    if not OPENAI_API_KEY:
        return None
    try:
        from langchain_openai import ChatOpenAI
    except ImportError:
        raise ImportError("Please install langchain-openai with 'poetry add langchain-openai'")

    llm = ChatOpenAI(
        api_key=SecretStr(OPENAI_API_KEY),
        model="gpt-4o",
        temperature=0.7
    )
    return llm.bind_tools(tools_to_bind)

# --- 1. Define the Agent State ---
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]

# --- 2. Define the Nodes ---
llm = _create_llm(tools)
tool_node = ToolNode(tools)

def llm_node(state: AgentState):
    """Invokes the LLM with the current state's messages."""
    if llm is None:
        raise RuntimeError("LLM could not be created. Is OPENAI_API_KEY set?")
    return {"messages": [llm.invoke(state["messages"])]}

# --- 3. Define the Conditional Edge Logic ---
def should_continue(state: AgentState) -> str:
    """
    Determines the next step for the agent.
    This is the router that decides between using tools, asking for human feedback, or finishing.
    """
    last_message = state["messages"][-1]
    
    if tool_calls := getattr(last_message, "tool_calls", None):
        # Now this check will work correctly because human_feedback_tool is defined
        if tool_calls[0]['name'] == human_feedback_tool.name:
            return "human"
        else:
            return "tools"
        
    return END

# --- 4. Assemble the Graph ---
def create_agent_graph():
    """Creates and compiles the LangGraph agent."""
    graph = StateGraph(AgentState)
    graph.add_node("llm", llm_node)
    graph.add_node("tools", tool_node)
    graph.add_node("human", lambda state: state)
    graph.set_entry_point("llm")
    graph.add_conditional_edges(
        "llm", should_continue, {"tools": "tools", "human": "human", END: END}
    )
    graph.add_edge("tools", "llm")
    graph.add_edge("human", "llm")
    return graph.compile(interrupt_before=["human"])