import json
import re
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional

from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, BaseMessage, ToolMessage
from agent.graph import create_agent_graph
from agent.system_prompt import german_system_prompt

# Create the agent
try:
    agent = create_agent_graph()
except Exception as e:
    print(f"Error creating agent: {e}")
    agent = None

app = FastAPI(title="Futedu Agent API", version="1.0.0")

# --- CORS Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
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
async def chat_with_agent(request: ChatRequest):
    try:
        if agent is None:
            raise HTTPException(status_code=500, detail="Agent not initialized")
        
        messages: List[BaseMessage] = [SystemMessage(content=german_system_prompt)]
        
        # Process chat history
        for item in request.chat_history:
            if item.type == "human":
                messages.append(HumanMessage(content=item.content))
            elif item.type == "ai":
                try:
                    json.loads(item.content)
                    messages.append(AIMessage(content=item.content))
                except (json.JSONDecodeError, TypeError):
                    messages.append(AIMessage(content=item.content))
        
        # Add current user input
        if request.tool_call_id:
            messages.append(ToolMessage(content=request.user_input, tool_call_id=request.tool_call_id))
        else:
            messages.append(HumanMessage(content=request.user_input))

        # Process with agent - use a more robust approach
        try:
            # Use invoke instead of stream for simpler handling
            result = agent.invoke({"messages": messages})
            print(f"DEBUG: Agent result type: {type(result)}")
            print(f"DEBUG: Agent result keys: {list(result.keys()) if isinstance(result, dict) else 'not dict'}")
            
            # Extract messages from the result
            if isinstance(result, dict) and "messages" in result:
                messages_list = result["messages"]
            else:
                # Fallback: try to find messages in the result
                messages_list = None
                if isinstance(result, dict):
                    for key, value in result.items():
                        if isinstance(value, list) and len(value) > 0 and hasattr(value[0], 'content'):
                            messages_list = value
                            break
                
                if messages_list is None:
                    raise HTTPException(status_code=500, detail="Could not extract messages from agent response")
            
            # Get the last message
            if not messages_list:
                raise HTTPException(status_code=500, detail="No messages in agent response")
            
            last_message = messages_list[-1]
            print(f"DEBUG: Last message type: {type(last_message)}")
            print(f"DEBUG: Last message content: {getattr(last_message, 'content', 'NO CONTENT')}")
            
        except Exception as e:
            print(f"Agent processing error: {e}")
            raise HTTPException(status_code=500, detail=f"Agent processing error: {str(e)}")

        final_response_str = getattr(last_message, 'content', '')

        # Handle tool calls
        if not final_response_str and hasattr(last_message, "tool_calls") and last_message.tool_calls:
            tool_call = last_message.tool_calls[0]
            if tool_call['name'] == 'human_feedback_tool':
                question = tool_call['args'].get('question', 'I have a question.')
                return {"response": question, "tool_call_id": tool_call['id']}

        # Handle JSON responses
        if final_response_str:
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
        
        # Fallback response
        return {"response": "I'm processing your request. Please wait a moment."}

    except HTTPException:
        raise
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/")
def read_root():
    return {"message": "API is running."}

@app.get("/health")
def health_check():
    return {"status": "healthy", "message": "API is running"}

@app.get("/test-agent")
async def test_agent():
    """Test endpoint to check if the agent is working properly."""
    try:
        if agent is None:
            return {"error": "Agent not initialized"}
        
        # Test with a simple message
        messages = [SystemMessage(content=german_system_prompt)]
        messages.append(HumanMessage(content="Test message"))
        
        result = agent.invoke({"messages": messages})
        
        return {
            "status": "success",
            "result_type": str(type(result)),
            "result_keys": list(result.keys()) if isinstance(result, dict) else "not dict",
            "has_messages": "messages" in result if isinstance(result, dict) else False
        }
    except Exception as e:
        return {"error": str(e), "type": str(type(e))}

@app.options("/chat")
async def options_chat():
    return {"message": "OK"}

@app.options("/")
async def options_root():
    return {"message": "OK"}

