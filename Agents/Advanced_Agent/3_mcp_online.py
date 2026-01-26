from dotenv import load_dotenv
import sys
load_dotenv()
import asyncio
#online mcp server
from langchain_mcp_adapters.client import MultiServerMCPClient
async def main():
    client = MultiServerMCPClient(
    {
        "time": {
            "transport": "stdio",
            "command": sys.executable,
            "args": [
                "-m",
                "mcp_server_time",
                "--local-timezone=Europe/Warsaw"
            ]
        }
    }
)

    tools = await client.get_tools()

    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain.agents import create_agent
    
    model = ChatGoogleGenerativeAI(model = "gemini-2.5-flash")
    
    agent = create_agent(
        model = model,
        tools = tools
    )
    
    from langchain.messages import HumanMessage
    
    question = HumanMessage("what time is it ?")
    
    response = await agent.ainvoke(
        {
            "messages" : [question]
        }
    )
    
    from pprint import pprint
    pprint(response)

if __name__ == "__main__":
    asyncio.run(main())
