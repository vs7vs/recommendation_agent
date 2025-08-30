from rich.console import Console
from rich.panel import Panel
from langchain_core.messages import SystemMessage, HumanMessage

# --- Import project-specific components ---
from agent.graph import create_agent_graph
from agent.system_prompt import german_system_prompt
from agent.config import validate_runtime_config

# --- Setup ---
console = Console()
# Create the agent by calling the factory function
try:
    compiled_graph = create_agent_graph()
except Exception as e:
    console.print(Panel(f"Error creating agent: {e}", title="Startup Error", border_style="red"))
    exit()

def main():
    """Runs the main conversational loop for the agent."""
    try:
        validate_runtime_config()
    except Exception as e:
        console.print(Panel(f"Missing Configuration: {e}", title="Startup Error", border_style="red"))
        return

    console.print("[bold green]Agent Futedu is ready.[/bold green]")
    console.print("Enter your profile or instructions. When done, write 'EOD' on a new line and press Enter.")

    messages = [SystemMessage(content=german_system_prompt)]

    # --- Initial Multi-line Input ---
    console.print("You: ")
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
            console.print("\n--- [dim]Agent is thinking...[/dim] ---")
            # Invoke the graph with the current message state
            result = compiled_graph.invoke({"messages": messages})
            messages = result["messages"]
            last_message = messages[-1]
            content = last_message.content

            # Handle the agent's final answer
            if "[TASK_COMPLETE]" in content:
                clean_response = content.replace("[TASK_COMPLETE]", "").strip()
                console.print(Panel(f"[bold]Agent:[/bold] {clean_response}", title="Final Response", border_style="green"))
                break # End conversation

            # Handle the agent pausing for human input
            elif "[PAUSE_FOR_INPUT]" in content:
                clean_response = content.replace("[PAUSE_FOR_INPUT]", "").strip()
                console.print(Panel(f"[bold]Agent:[/bold] {clean_response}", title="Agent Question", border_style="yellow"))
                user_answer = input("You (your answer): ")
                messages.append(HumanMessage(content=user_answer))

            # Handle intermediate updates (not used in your logic, but good practice)
            else:
                console.print(Panel(f"[bold]Agent:[/bold] {content}", title="Agent Update", border_style="cyan"))
                user_answer = input("You (Press Enter to continue...): ")
                messages.append(HumanMessage(content=user_answer))

        except (KeyboardInterrupt, EOFError):
            console.print("\nAgent: Goodbye!")
            break

    console.print("\n--- Conversation Ended ---")

if __name__ == "__main__":
    main()