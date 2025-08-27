from agent_logic.agent import get_agent_response
from agent_logic.system_prompt import german_system_prompt
from langchain_core.messages import SystemMessage

def test_add_numbers():
    # 1. Start with the system prompt, just like a real conversation
    messages = [SystemMessage(content=german_system_prompt)]

    # 2. Call the testable function with the user's request
    result_messages = get_agent_response("Addiere 2 und 3.", messages)

    # 3. Get the last message from the result
    final_response = result_messages[-1].content

    # 4. Assert that the answer is in the final response
    print(f"Agent response: {final_response}") # Helpful for debugging tests
    assert "5" in final_response
