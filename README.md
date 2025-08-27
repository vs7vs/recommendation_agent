# Agent Playground

A minimal LangChain-based LLM agent using OpenAI GPT and custom tools.

## Setup

1. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set your OpenAI API key:
   ```bash
   export OPENAI_API_KEY=sk-...
   ```

## Usage

Run the test to see the agent in action:

```bash
pytest tests/test_agent.py
```

Or use the agent in your own code:

```python
from agent_logic.agent import run_agent
print(run_agent("Add 2 and 3."))
``` 