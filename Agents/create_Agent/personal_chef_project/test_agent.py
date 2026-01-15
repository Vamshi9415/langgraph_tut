from personal_chef_project import agent
from langchain.messages import HumanMessage

# Test the agent
question = HumanMessage(content="I have chicken, rice, and broccoli. What can I make?")
response = agent.invoke({"messages": [question]})

from pprint import pprint

pprint(response)