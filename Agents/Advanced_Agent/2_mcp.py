import asyncio
import sys
from pathlib import Path
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient

load_dotenv()

# Windows async fix (script context)
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

BASE_DIR = Path(__file__).resolve().parent
SERVER_PATH = BASE_DIR / "Resources" / "2.1_mcp_server.py"

def build_client() -> MultiServerMCPClient :
    return MultiServerMCPClient(
        {
            "local_server": {
                "transport": "stdio",
                "command": sys.executable,
                "args": [str(SERVER_PATH)],
            }
        }
    )

async def fetch_mcp_context(client: MultiServerMCPClient):
    print("Getting Tools ..")
    tools = await client.get_tools()
    print(tools)
    
    print("Getting Resoures ..")
    resources = await client.get_resources("local_server")
    print(resources)
    
    print("Getting Prompt")
    prompt = await client.get_prompt("local_server","prompt")
    print(prompt)
    
    return tools,prompt
 
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI

def build_agent(tools,prompt):
    model = ChatGoogleGenerativeAI(model = "gemini-2.5-flash")
    agent = create_agent(
        model = model,
        tools = tools,
        system_prompt = str(prompt)
    )
    return agent 
from langchain.messages import HumanMessage

async def run_agent(agent):
    config = {
        "configurable" : {
            "thread_id" : "1"
        }
    }
    response = await agent.ainvoke(
        {
            "messages" : [
                HumanMessage("tell me about the langchain-mcp adapters")
            ]
        },config = config
    )
    
    return response 

    
    
async def main():
    
    client = build_client()
    tools, prompt = await fetch_mcp_context(client)
    agent = build_agent(tools,prompt)
    
    response = await run_agent(agent=agent)
    from pprint import pprint
    
    pprint(response)

if __name__ == "__main__":
    asyncio.run(main())