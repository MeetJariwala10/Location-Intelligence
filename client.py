# Create server parameters for stdio connection
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.streamable_http import streamablehttp_client
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import InMemorySaver
import asyncio
from dotenv import load_dotenv
import json

load_dotenv()

model = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
# checkpointer = InMemorySaver()

# NOTE: using stdio 

# server_params = StdioServerParameters(
#     command="python",
#     # Make sure to update to the full absolute path to your math_server.py file
#     args=["server.py"],
    
# )

# # async def run_agent():
# #     async with stdio_client(server_params) as (read, write):
# #         async with ClientSession(read, write) as session:
# #             # Initialize the connection
# #             await session.initialize()

# #             # Get tools
# #             tools = await load_mcp_tools(session)

# #             # Create and run the agent
# #             agent = create_react_agent(model, tools)
# #             # agent_response = await agent.ainvoke({"messages": "what's (3 + 5) x 12?"})
# #             agent_response = await agent.ainvoke({"messages": "What is 5 * 2 and then add it to 10"})
# #             return agent_response


# NOTE: using streamable-http

async def run_agent():
    async with streamablehttp_client("http://localhost:8000/mcp") as (
        read_stream, 
        write_stream,
        _
    ):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            tools = await load_mcp_tools(session)

            # Create and run the agent
            agent = create_react_agent(model, tools)

            agent_response = await agent.ainvoke({"messages": "give me analysis of surroundings of Sarvajanik College of engineering and technology (public transportation facilities, restaurants, playgrounds, hospitals etc) along with location, including the Air quality, temperature. List down the names also and give in points."})
            # agent_response = await agent.ainvoke({"messages": "where is Sarvajanik college of engineering and technology. give its coords and its AQI"})
            return agent_response




# Run the async function
if __name__ == "__main__":
    result = asyncio.run(run_agent())
    
    # Extract the final answer from the last message
    messages = result['messages']
    if messages and len(messages) > 0:
        last_message = messages[-1]
        if hasattr(last_message, 'content') and last_message.content:
            print(f"\nAnswer: {last_message.content}")
        else:
            print("\nNo final answer found.")
    else:
        print("\nNo messages received.")




