from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import List

from fastapi.middleware.cors import CORSMiddleware

from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, BaseMessage
from agent.graph import create_agent_graph
from agent.system_prompt import german_system_prompt

agent = create_agent_graph()
app = FastAPI(
    title="Futedu Agent API",
    description="An API for interacting with the conversational Futedu agent.",
    version="1.0.0"
)

# --- CORS-Middleware hinzufügen (Vollständige Konfiguration) ---
origins = ["*"] # Erlaubt Anfragen von jeder Herkunft

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # vvv FIX: Erlaubt alle Methoden (GET, POST, etc.)
    allow_headers=["*"],  # vvv FIX: Erlaubt alle Header (wie Content-Type)
)

# --- Anforderungs- und Antwortmodelle definieren ---
class ChatHistoryItem(BaseModel):
    type: str
    content: str

class ChatRequest(BaseModel):
    user_input: str
    chat_history: List[ChatHistoryItem] = Field(default_factory=list)

# --- Chat-Endpunkt erstellen ---
@app.post("/chat")
def chat_with_agent(request: ChatRequest):
    # (Der Rest Ihres Codes bleibt exakt gleich)
    print(f"Received input: {request.user_input}")
    print(f"Received history: {request.chat_history}")

    messages: List[BaseMessage] = [SystemMessage(content=german_system_prompt)]
    for item in request.chat_history:
        if item.type == "human":
            messages.append(HumanMessage(content=item.content))
        elif item.type == "ai":
            messages.append(AIMessage(content=item.content))
    
    messages.append(HumanMessage(content=request.user_input))
    result = agent.invoke({"messages": messages})
    final_response = result["messages"][-1].content
    
    print(f"Agent response: {final_response}")
    return {"response": final_response}

# (Optional) Root-endpoint for simple tests
@app.get("/")
def read_root():
    return {"message": "API is running. Go to /docs for interactive testing."}