from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import List, Dict, Any

# --- 1. Import and Load the Agent ---
from agent.graph import create_agent_graph
from agent.system_prompt import german_system_prompt
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, BaseMessage

agent = create_agent_graph()

# --- 2. Define the API Application ---
app = FastAPI(
    title="Futedu Agent API",
    description="An API for interacting with the conversational Futedu agent.",
    version="1.0.0"
)

# --- 3. Define the Request and Response Models ---
class ChatHistoryItem(BaseModel):
    """Represents a single message in the chat history."""
    type: str  # e.g., "human", "ai"
    content: str

class ChatRequest(BaseModel):
    """The request model now includes conversation history."""
    user_input: str
    chat_history: List[ChatHistoryItem] = Field(default_factory=list)

# --- 4. Create the Chat Endpoint ---
@app.post("/chat")
def chat_with_agent(request: ChatRequest):
    """
    Receives user input and conversation history, processes it with the
    LangGraph agent, and returns the agent's final response.
    """
    print(f"Received input: {request.user_input}")
    print(f"Received history: {request.chat_history}")

    # Reconstruct the LangChain message objects from the chat history
    messages: List[BaseMessage] = [SystemMessage(content=german_system_prompt)]
    for item in request.chat_history:
        if item.type == "human":
            messages.append(HumanMessage(content=item.content))
        elif item.type == "ai":
            messages.append(AIMessage(content=item.content))
    
    # Add the new user input
    messages.append(HumanMessage(content=request.user_input))

    # Invoke the agent with the full conversation history
    result = agent.invoke({"messages": messages})

    # Extract the last message from the agent's response
    final_response = result["messages"][-1].content
    
    print(f"Agent response: {final_response}")
    return {"response": final_response}