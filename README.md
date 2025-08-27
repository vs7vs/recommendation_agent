# Agent Playground

A minimal LangGraph/LangChain-based LLM agent using OpenAI GPT and custom tools.

## Setup

1. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   # or, install the package in editable mode (recommended for development)
   pip install -e .
   ```
3. Copy and fill in env vars:
   ```bash
   cp .env.example .env
   # then edit .env to add keys
   ```

## Usage

Run the CLI agent (LangGraph-powered):

```bash
futedu-agent
```

Run the tests:

```bash
pytest tests/test_agent.py
```

Or use the agent in your own code (programmatic API):

```python
from agent_logic.agent import get_agent_response
from agent_logic.system_prompt import german_system_prompt
from langchain_core.messages import SystemMessage

messages = [SystemMessage(content=german_system_prompt)]
print(get_agent_response("Addiere 2 und 3.", messages)[-1].content)
```

## Notes

- The conversation loop and routing are implemented with LangGraph.
- Tools include web search, website scraping, and link discovery; configure API keys in `.env`.