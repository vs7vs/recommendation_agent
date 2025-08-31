import json
import re
from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import List

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

# --- Chat Endpoint ---
@app.post("/chat")
def chat_with_agent(request: ChatRequest):
    messages: List[BaseMessage] = [SystemMessage(content=german_system_prompt)]
    for item in request.chat_history:
        if item.type == "human":
            messages.append(HumanMessage(content=item.content))
        elif item.type == "ai":
            messages.append(AIMessage(content=item.content))
    
    messages.append(HumanMessage(content=request.user_input))

    # --- vvv IMPROVED LOGIC vvv ---
    # Use agent.stream() to let the agent run its internal thought process
    # until it reaches a stopping point (a final answer or needs human input).
    final_state = {}
    for step in agent.stream({"messages": messages}):
        # The stream yields the state of each node as it executes.
        # We capture the final state when the loop finishes.
        final_state = step

    # Extract the last message from the final state of the graph
    last_message = next(iter(final_state.values()))["messages"][-1]
    final_response_str = last_message.content

    # Check if the agent paused to ask a question
    if not final_response_str and hasattr(last_message, "tool_calls") and last_message.tool_calls:
        tool_call = last_message.tool_calls[0]
        if tool_call['name'] == 'human_feedback_tool':
            question = tool_call['args'].get('question', 'I have a question.')
            return {"response": question, "tool_call_id": tool_call['id']}

    # Handle the final answer (JSON or plain text)
    json_match = re.search(r'\{.*\}', final_response_str, re.DOTALL)
    if json_match:
        json_string = json_match.group(0)
        try:
            final_response_json = json.loads(json_string)
            return {"response": final_response_json}
        except json.JSONDecodeError:
            return {"response": final_response_str}
    else:
        return {"response": final_response_str}

@app.get("/")
def read_root():
    return {"message": "API is running."}

