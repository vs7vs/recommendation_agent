import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")


if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable not set.") 

if not TAVILY_API_KEY:
    raise ValueError("TAVILY_API_KEY environment variable not set.") 