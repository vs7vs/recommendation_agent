import json
from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import List, Optional

from fastapi.middleware.cors import CORSMiddleware
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, BaseMessage, ToolMessage
from agent.graph import create_agent_graph
from agent.system_prompt import german_system_prompt

agent = create_agent_graph()
app = FastAPI(title="Futedu Agent API", version="1.0.0")

# --- CORS Middleware ---
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Define Models ---
class ChatHistoryItem(BaseModel):
    type: str
    content: str

class ChatRequest(BaseModel):
    user_input: str
    chat_history: List[ChatHistoryItem] = Field(default_factory=list)
    # This optional field will carry the ID of the tool call we need to respond to
    tool_call_id: Optional[str] = None

# --- Chat Endpoint ---
@app.post("/chat")
def chat_with_agent(request: ChatRequest):
    messages: List[BaseMessage] = [SystemMessage(content=german_system_prompt)]
    for item in request.chat_history:
        if item.type == "human":
            messages.append(HumanMessage(content=item.content))
        elif item.type == "ai":
            # When reconstructing history, we must handle both plain text and JSON strings
            try:
                # If the AI content is a JSON string, keep it as a plain AIMessage
                json.loads(item.content)
                messages.append(AIMessage(content=item.content))
            except (json.JSONDecodeError, TypeError):
                # If it's just plain text, it's a regular AIMessage
                messages.append(AIMessage(content=item.content))
    
    # If a tool_call_id is provided, the user is answering a tool's question.
    # We must construct a ToolMessage instead of a HumanMessage.
    if request.tool_call_id:
        messages.append(ToolMessage(content=request.user_input, tool_call_id=request.tool_call_id))
    else:
        messages.append(HumanMessage(content=request.user_input))

    result = agent.invoke({"messages": messages})
    last_message = result["messages"][-1]
    content = last_message.content

    # Check if the agent's response is a tool call to ask a question.
    if not content and hasattr(last_message, "tool_calls") and last_message.tool_calls:
        tool_call = last_message.tool_calls[0]
        if tool_call['name'] == 'human_feedback_tool':
            question = tool_call['args'].get('question', 'I have a question.')
            # Return the question AND the tool_call_id to the frontend
            return {"response": question, "tool_call_id": tool_call['id']}

    # Handle final JSON or intermediate text responses as before
    try:
        final_response_json = json.loads(content)
        return {"response": final_response_json}
    except (json.JSONDecodeError, TypeError):
        return {"response": content if content is not None else ""}

@app.get("/")
def read_root():
    return {"message": "API is running."}

