import json
import re
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
    tool_call_id: Optional[str] = None

# --- Chat Endpoint ---
@app.post("/chat")
def chat_with_agent(request: ChatRequest):
    messages: List[BaseMessage] = [SystemMessage(content=german_system_prompt)]
    for item in request.chat_history:
        if item.type == "human":
            messages.append(HumanMessage(content=item.content))
        elif item.type == "ai":
            try:
                json.loads(item.content)
                messages.append(AIMessage(content=item.content))
            except (json.JSONDecodeError, TypeError):
                messages.append(AIMessage(content=item.content))
    
    if request.tool_call_id:
        messages.append(ToolMessage(content=request.user_input, tool_call_id=request.tool_call_id))
    else:
        messages.append(HumanMessage(content=request.user_input))

    final_state = {}
    for step in agent.stream({"messages": messages}):
        final_state = step

    last_step_output = list(final_state.values())[0] 
    last_message = last_step_output["messages"][-1]
    final_response_str = last_message.content

    if not final_response_str and hasattr(last_message, "tool_calls") and last_message.tool_calls:
        tool_call = last_message.tool_calls[0]
        if tool_call['name'] == 'human_feedback_tool':
            question = tool_call['args'].get('question', 'I have a question.')
            return {"response": question, "tool_call_id": tool_call['id']}

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

