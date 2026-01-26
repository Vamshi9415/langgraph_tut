from dotenv import load_dotenv

load_dotenv()

import os
from mcp.server.fastmcp import FastMCP
from tavily import TavilyClient
from typing import Dict, Any
from requests import get

mcp = FastMCP("mcp_server")

tavily_api_key = os.getenv("TAVILY_API_KEY")
tavily_client = TavilyClient(api_key=tavily_api_key) if tavily_api_key else None

# searching web
@mcp.tool()
def search_web(query: str) -> Dict[str, Any]:
    """Search the web for the information."""
    if not tavily_client:
        return {"error": "TAVILY_API_KEY is not set."}
    try:
        return tavily_client.search(query)
    except Exception as e:
        return {"error": str(e)}

# providing data to ai to use it 
@mcp.resource("github://langchain-ai/langchain-mcp-adapters/blob/main/README.md")
def github_file():
    """
    Resource for accessing langchain-ai/langchain-mcp-adapters/README.md file
    """
    url = "https://raw.githubusercontent.com/langchain-ai/langchain-mcp-adapters/main/README.md"
    try:
        resp = get(url)
        return resp.text
    except Exception as e:
        return f"Error: {str(e)}"

# prompt template
@mcp.prompt()
def prompt():
    """analyze the data from the repo with insights"""
    return """You are a helpful assistant that answers user questions about LangChain, LangGraph and LangSmith.

    You can use the following tools/resources to answer user questions:
    - search_web: Search the web for information
    - github_file: Access the langchain-ai repo files

    If the user asks a question that is not related to LangChain, LangGraph or LangSmith, you should say "I'm sorry, I can only answer questions about LangChain, LangGraph and LangSmith."

    You may try multiple tool and resource calls to answer the user's question.

    You may also ask clarifying questions to the user to better understand their question.
"""

if __name__ == "__main__":
    mcp.run(transport = "stdio")
    #here transport means how mcp server talks to ai client like stdio : standard input and htpp, sockets etc