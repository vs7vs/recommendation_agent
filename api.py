import json # <-- Import the json module
from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import List
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, BaseMessage
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
    result = agent.invoke({"messages": messages})
    final_response_str = result["messages"][-1].content
    
    # vvv IMPORTANT CHANGE HERE vvv
    try:
        # Try to parse the agent's response as JSON
        final_response_json = json.loads(final_response_str)
        return {"response": final_response_json}
    except json.JSONDecodeError:
        # If it's not valid JSON, send it as plain text
        return {"response": final_response_str}

@app.get("/")
def read_root():
    return {"message": "API is running."}
