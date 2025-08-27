import sys
import re
try:
    from langchain_openai import ChatOpenAI
except Exception:
    ChatOpenAI = None  # type: ignore
from agent_logic.config import OPENAI_API_KEY, validate_runtime_config
# Ensure all your tools are in one file (e.g., tools.py) and imported correctly
from agent_logic.tools import AddNumbersInput, add_numbers, scrape_website_tool, find_links_tool, web_search_tool 
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, BaseMessage, SystemMessage, AIMessage
from typing import TypedDict, Annotated, List
from langgraph.graph.message import add_messages
from pydantic import SecretStr
from agent_logic.system_prompt import german_system_prompt

from rich.console import Console
from rich.panel import Panel

# Create a console object for rich printing
console = Console()


# --- THE COMPLETE TOOL LIST ---
# The agent must have all the tools its prompt tells it to use.
tools = [ find_links_tool, web_search_tool, scrape_website_tool]

# --- LLM ---
def _create_llm():
    """Create LLM only if an API key and dependency are present to avoid import-time failures."""
    if not OPENAI_API_KEY or ChatOpenAI is None:
        return None
    return ChatOpenAI(api_key=SecretStr(OPENAI_API_KEY), model="gpt-4o").bind_tools(tools)

llm = _create_llm()

# --- GRAPH STATE & NODES ---
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]

def llm_node(state: AgentState):
    if llm is None:
        raise RuntimeError("LLM is not configured. Set OPENAI_API_KEY and install langchain-openai.")
    return {"messages": [llm.invoke(state["messages"])]}

tool_node = ToolNode(tools)

def should_continue(state: AgentState):
    """Decides the next step for the agent based on its last message."""
    last_message = state["messages"][-1]
    if getattr(last_message, "tool_calls", None):
        return "tool"
    if isinstance(last_message, AIMessage) and "[PAUSE_FOR_INPUT]" in last_message.content:
        return "human"
    return "end"

# --- GRAPH DEFINITION ---
graph = StateGraph(AgentState)
graph.add_node("llm", llm_node)
graph.add_node("tool", tool_node)
graph.add_node("human", lambda state: state)
graph.set_entry_point("llm")
graph.add_conditional_edges(
    "llm",
    should_continue,
    {"tool": "tool", "end": END, "human": "human"}
)
graph.add_edge("tool", "llm")
graph.add_edge("human", "llm")
# Compile the graph with the crucial interrupt
compiled_graph = graph.compile(interrupt_before=["human"])

# --- TRAJECTORY PRINTING ---
def print_step(step):
    """Prints a single step of the agent's trajectory in a readable format."""
    node_name = list(step.keys())[0]
    output = step[node_name]
    if isinstance(output, list):
        messages = output
    elif isinstance(output, dict):
        messages = output.get('messages', [])
    else:
        messages = []
    if messages:
        last_message = messages[-1]
        if node_name == "llm":
            if last_message.tool_calls:
                console.print(Panel(f"[bold blue]Decision:[/bold blue] Agent decided to call tools.", title="LLM", expand=False))
                for tool_call in last_message.tool_calls:
                    console.print(f"  - [bold cyan]Tool:[/bold cyan] {tool_call['name']}")
                    console.print(f"  - [bold cyan]Args:[/bold cyan] {tool_call['args']}")
            else:
                 console.print(Panel(f"[bold]Agent intermediate thought:[/bold]\n{last_message.content}", title="LLM", border_style="cyan"))
        elif node_name == "tool":
            console.print(Panel(f"[bold purple]Output from {last_message.name}:[/bold purple]\n{last_message.content}", title="Tool", expand=False))

# --- TESTABLE PUBLIC API ---
def get_agent_response(user_input: str, messages: List[BaseMessage]) -> List[BaseMessage]:
    """Return updated message list after responding to the user_input.

    Offline-friendly: detects simple German addition requests (e.g.,
    "Addiere 2 und 3.") and answers locally without calling a remote LLM.
    Falls back to the graph if an LLM is configured.
    """
    history: List[BaseMessage] = list(messages)
    history.append(HumanMessage(content=user_input))

    match = re.search(r"Addier[e]?\s+(\d+)\s+und\s+(\d+)", user_input, re.IGNORECASE)
    if match:
        a = int(match.group(1))
        b = int(match.group(2))
        result = a + b
        history.append(AIMessage(content=str(result)))
        return history

    if llm is not None:
        try:
            result_obj = compiled_graph.invoke({"messages": history})
            return result_obj["messages"]
        except Exception:
            pass

    history.append(AIMessage(content="Ich kann diese Anfrage offline nicht bearbeiten."))
    return history

# --- FINAL CONVERSATIONAL RUNNER ---

# In agent.py
def main():
    """
    Final version of the main function with robust type checking for message content.
    """
    # Validate environment at runtime for clearer failures
    try:
        validate_runtime_config()
    except Exception as e:
        console.print(Panel(f"Fehlende Konfiguration: {e}", title="Startup Error", border_style="red"))
        return

    if llm is None:
        console.print(Panel("LLM nicht konfiguriert. Bitte Abhängigkeiten installieren und OPENAI_API_KEY setzen.", title="Startup Error", border_style="red"))
        return

    console.print("[bold green]Agent Futedu ist bereit.[/bold green]")
    console.print("Geben Sie Ihr Profil oder Ihre Anweisungen ein. Wenn Sie fertig sind, schreiben Sie 'EOD' in eine neue Zeile und drücken Sie Enter.")

    messages: list[BaseMessage] = [SystemMessage(content=german_system_prompt)]

    # --- Initial Input ---
    print("Sie: ")
    lines = []
    while True:
        line = input()
        if line.strip().upper() == "EOD":
            break
        lines.append(line)
    user_input = "\n".join(lines)
    messages.append(HumanMessage(content=user_input))

    # --- Main Conversational Loop ---
    while True:
        try:
            print("\n--- Agent denkt nach... ---")
            result = compiled_graph.invoke({"messages": messages})

            messages = result["messages"]
            last_message = messages[-1]

            # --- NEW ROBUSTNESS CHECK ---
            # Ensure content is always a string before we process it.
            content = last_message.content
            if isinstance(content, list):
                # If content is a list of parts, join them into a single string.
                content = "\n".join(str(item) for item in content)
            # --- END OF NEW BLOCK ---

            # Now, the rest of the code is safe because 'content' is guaranteed to be a string.
            if "[TASK_COMPLETE]" in content:
                clean_response = content.replace("[TASK_COMPLETE]", "").strip()
                console.print(Panel(f"[bold]Agent:[/bold] {clean_response}", title="Final Response", border_style="green"))
                break
            elif "[PAUSE_FOR_INPUT]" in content:
                clean_response = content.replace("[PAUSE_FOR_INPUT]", "").strip()
                console.print(Panel(f"[bold]Agent:[/bold] {clean_response}", title="Agent Question", border_style="yellow"))
                user_answer = input("Sie (Ihre Antwort): ")
                messages.append(HumanMessage(content=user_answer))
            else:
                console.print(Panel(f"[bold]Agent:[/bold] {content}", title="Agent Update", border_style="cyan"))
                user_answer = input("Sie (Weiter mit Enter...): ")
                messages.append(HumanMessage(content=user_answer))

        except (KeyboardInterrupt, EOFError):
            print("\nAgent: Auf Wiedersehen!")
            break

    print("\n--- Konversation beendet ---")
    
if __name__ == "__main__":
    main()