import json
from rich.console import Console
from rich.panel import Panel
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage

# --- Import project-specific components ---
from agent.graph import create_agent_graph
from agent.system_prompt import german_system_prompt
from agent.config import validate_runtime_config

# --- Setup ---
console = Console()
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
            result = compiled_graph.invoke({"messages": messages})
            messages = result["messages"]
            last_message = messages[-1]
            content = last_message.content

            # --- vvv CORRECTED LOGIC vvv ---
            # First, check for tool calls that cause an interruption (human feedback).
            if not content and hasattr(last_message, "tool_calls") and last_message.tool_calls:
                tool_call = last_message.tool_calls[0]
                if tool_call['name'] == 'human_feedback_tool':
                    # Extract the question from the tool call arguments
                    question = tool_call['args'].get('question', 'I have a question for you.')
                    
                    console.print(Panel(f"[bold]Agent:[/bold] {question}", title="Agent Question", border_style="yellow"))
                    user_answer = input("You (your answer): ")
                    
                    # Respond with a ToolMessage to continue the graph flow correctly
                    messages.append(ToolMessage(content=user_answer, tool_call_id=tool_call['id']))
                    # Continue to the next loop iteration to let the agent process the answer
                    continue

            # If no tool call interruption, check for a final JSON answer.
            try:
                final_json = json.loads(content)
                console.print(Panel("[bold]Agent's Final Recommendations:[/bold]", border_style="green"))
                
                if "summary" in final_json:
                    console.print(f"[italic]{final_json['summary']}[/italic]\n")
                
                for rec in final_json.get("recommendations", []):
                    rec_panel = Panel(
                        f"[bold]Income:[/bold] {rec.get('income', 'N/A')}\n"
                        f"[bold]Reasoning:[/bold] {rec.get('reasoning', 'N/A')}",
                        title=f"[bold cyan]{rec.get('title', 'Recommendation')}[/bold cyan]",
                        expand=False
                    )
                    console.print(rec_panel)
                
                break # End the conversation

            except (json.JSONDecodeError, TypeError):
                # If it's neither a tool call nor JSON, it's an intermediate "Gedanke/Aktion" step.
                if content: # Only print if there is content
                    console.print(Panel(f"{content}", title="Agent Update", border_style="cyan"))
                
                user_answer = input("You (Press Enter to continue...): ")
                # If the user provides an answer, add it as a human message
                if user_answer:
                    messages.append(HumanMessage(content=user_answer))
                # If the user just presses Enter, the loop continues, letting the agent think again.

        except (KeyboardInterrupt, EOFError):
            console.print("\nAgent: Goodbye!")
            break

    console.print("\n--- Conversation Ended ---")

if __name__ == "__main__":
    main()

