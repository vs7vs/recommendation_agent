import re
from langchain_core.messages import AIMessage

def german_addition_handler(user_input: str):
    """
    Detects simple German addition requests and returns the result
    without calling an LLM. Returns None if no match.
    """
    match = re.search(r"Addier[e]?\s+(\d+)\s+und\s+(\d+)", user_input, re.IGNORECASE)
    if match:
        a = int(match.group(1))
        b = int(match.group(2))
        result = a + b
        return AIMessage(content=str(result))
    return None

def test_addition_handler_with_match():
    """Tests that the handler correctly calculates addition."""
    response = german_addition_handler("Addiere 5 und 10")
    assert response is not None
    assert response.content == "15"

def test_addition_handler_no_match():
    """Tests that the handler returns None for unrelated input."""
    response = german_addition_handler("What is the capital of Germany?")
    assert response is None