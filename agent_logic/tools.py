from pydantic import BaseModel, Field
import requests

from langchain_community.document_loaders import WebBaseLoader
from langchain_core.tools import tool
from urllib.parse import quote

from bs4 import BeautifulSoup, Tag
from urllib.parse import urljoin, urlparse
from langchain_tavily import TavilySearch


class AddNumbersInput(BaseModel):
    a: int
    b: int

class WebSearchInput(BaseModel):
    query: str

def add_numbers(a: int, b: int) -> int:
    """Add two numbers and return the result."""
    return a + b

# Define the new, powerful search tool
web_search_tool = TavilySearch(max_results=3)
web_search_tool.name = "web_search_tool"
web_search_tool.description = "A powerful search engine. Use this to find information on the internet. It returns a summarized answer and a list of sources." 


class ScrapeWebsiteInput(BaseModel):
    url: str = Field(description="The URL of the webpage you want to scrape.")

@tool(args_schema=ScrapeWebsiteInput)
def scrape_website_tool(url: str) -> str:
    """
    Scrapes the text content of a single webpage.
    The agent should use this tool when a user provides a specific URL
    and asks a question about its content, like 'Summarize this page'.
    """
    try:
        print(f"--- Loading content from {url} ---")
        loader = WebBaseLoader(web_path=url)
        docs = loader.load() # Use .load() for synchronous execution

        # Combine the content of all loaded documents (usually just one for a single URL)
        content = " ".join([doc.page_content for doc in docs])
        
        # Clean up excessive newlines and whitespace
        cleaned_content = " ".join(content.split())

        if len(cleaned_content) > 5000:
             return f"Successfully scraped the website. The content is very long, here is the beginning: {cleaned_content[:5000]}"

        if not cleaned_content:
            return "Could not find any text content on the page."
        
        return cleaned_content
    
    except Exception as e:
        return f"An error occurred while trying to scrape the website: {e}"

class FindLinksInput(BaseModel):
    url: str = Field(description="The URL of the webpage to find links on.")

@tool(args_schema=FindLinksInput)
def find_links_tool(url: str) -> str:
    """
    Finds all the navigable links on a given webpage URL and returns them as a list.
    Use this to explore a website and decide where to go next.
    """
    try:
        print(f"--- Finding links on {url} ---")
        response = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")
        
        links = []
        for a_tag in soup.find_all("a", href=True):
            if isinstance(a_tag, Tag):
                href = a_tag.get("href")
                if href is None:
                    continue
                absolute_url = urljoin(url, str(href))
                # Basic filtering to ignore irrelevant links
                parsed_url = urlparse(absolute_url)
                if parsed_url.scheme in ['http', 'https'] and '#' not in absolute_url:
                    if absolute_url not in links:
                        links.append(absolute_url)

        if not links:
            return "No links found on this page."
            
        # Return a formatted string for the LLM to easily parse
        return "Found the following links:\n" + "\n".join(f"- {link}" for link in links[:100]) # Return max 30 links to not overwhelm the LLM

    except requests.RequestException as e:
        return f"Error fetching the URL: {e}"
    except Exception as e:
        return f"An error occurred while finding links: {e}"
