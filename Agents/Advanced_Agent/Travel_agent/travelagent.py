from dotenv import load_dotenv

load_dotenv()

from langchain_mcp_adapters.client import MultiServerMCPClient

def build_client() -> MultiServerMCPClient :
    return MultiServerMCPClient(
        {
        "travel_server": {
                "transport": "streamable_http",
                "url": "https://mcp.kiwi.com"
            }
    }
    )

#get the tools

async def fetch_mcp_context(client : MultiServerMCPClient):
    print("Getting Tools")
    tools = await client.get_tools()
    print("Tools ",tools)
    
    return tools


from langchain.agents import create_agent

from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import InMemorySaver

# 1. Updated Import

from langchain.agents import create_agent

def build_agent(tools):
    model = ChatGoogleGenerativeAI(model='gemini-2.5-flash')

    agent = create_agent(
        model=model,
        tools=tools,
        system_prompt="You are a travel agent. Today is Friday, Feb 6, 2026. Use the tools to get the perfect plan."
    )
    return agent


def config():
    return {
        "configurable" : {
            "thread_id" : "1"
        }
    }
from langchain.messages import HumanMessage

async def run_Agent(agent,config):
    query = HumanMessage(content = " Get me a direct flight from Hyderabad to Chennai on March 31st")
    response = await agent.ainvoke(
        {
        'messages' : [query],
        },config
        )# needs Human Message,config
    
    return response

async def main():
    client = build_client()
    tools = await fetch_mcp_context(client=client)
    agent = build_agent(tools)
    my_config = config() 
    response = await run_Agent(agent, my_config)
    
    from pprint import pprint
    print(response)

import asyncio
if __name__ == "__main__":
    asyncio.run(main())