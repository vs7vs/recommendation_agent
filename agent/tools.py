from pydantic import BaseModel, Field
import requests
from bs4 import BeautifulSoup, Tag
from urllib.parse import urljoin, urlparse

from langchain_community.document_loaders import WebBaseLoader
from langchain_core.tools import tool
from langchain_tavily import TavilySearch

# --- Tool 1: Web Search ---
def create_web_search_tool():
    """Create the web search tool after environment variables are loaded."""
    tool = TavilySearch(max_results=3)
    tool.name = "web_search" # Use a simple name for the agent
    tool.description = "A powerful search engine. Use this to find information on the internet. It returns a summarized answer and a list of sources."
    return tool

# --- Tool 2: Scrape Website ---
class ScrapeWebsiteInput(BaseModel):
    url: str = Field(description="The URL of the webpage you want to scrape.")

@tool(args_schema=ScrapeWebsiteInput)
def scrape_website_tool(url: str) -> str:
    """
    Scrapes the text content of a single webpage.
    Use this when a user provides a specific URL and asks a question about its content.
    """
    try:
        loader = WebBaseLoader(web_path=url)
        docs = loader.load()
        content = " ".join([doc.page_content for doc in docs])
        cleaned_content = " ".join(content.split())

        if not cleaned_content:
            return "Could not find any text content on the page."
        
        # Return a preview if the content is too long
        return cleaned_content[:5000]
    
    except Exception as e:
        return f"An error occurred while trying to scrape the website: {e}"

# --- Tool 3: Find Links ---
class FindLinksInput(BaseModel):
    url: str = Field(description="The URL of the webpage to find links on.")

@tool(args_schema=FindLinksInput)
def find_links_tool(url: str) -> str:
    """
    Finds all the navigable links on a given webpage URL and returns them as a list.
    Use this to explore a website.
    """
    try:
        response = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        
        links = []
        for a_tag in soup.find_all("a", href=True):
            href = a_tag.get("href")
            if not href:
                continue
            
            absolute_url = urljoin(url, href)
            parsed_url = urlparse(absolute_url)
            if parsed_url.scheme in ['http', 'https'] and '#' not in absolute_url:
                if absolute_url not in links:
                    links.append(absolute_url)

        if not links:
            return "No links found on this page."
            
        return "Found the following links:\n" + "\n".join(f"- {link}" for link in links[:30])

    except Exception as e:
        return f"An error occurred while finding links: {e}"

@tool
def human_feedback_tool(question: str) -> str:
    """
    Use this tool when you need to ask the user a clarifying question,
    get their feedback on a suggestion, or ask for more information.
    The input to this tool is the exact question you want to ask the human.
    """
    # This tool is a signal. The function body doesn't need to do anything.
    # The graph will interrupt when this tool is called.
    return ""

# --- Assemble the Final Tools List ---
# Add the new tool to your list of tools
tools = [
    create_web_search_tool(),
    scrape_website_tool,
    find_links_tool,
    human_feedback_tool 
]
