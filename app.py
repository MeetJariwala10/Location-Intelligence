import asyncio
import os
from typing import Optional

import streamlit as st
from dotenv import load_dotenv
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
from langchain_google_genai import ChatGoogleGenerativeAI


load_dotenv()


def get_model() -> ChatGoogleGenerativeAI:
    # Requires GOOGLE_API_KEY env var. You can set it in a .env file.
    return ChatGoogleGenerativeAI(model="gemini-2.0-flash")


async def run_agent_with_query(query: str, mcp_url: str) -> Optional[str]:
    async with streamablehttp_client(mcp_url) as (
        read_stream,
        write_stream,
        _,
    ):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            tools = await load_mcp_tools(session)
            model = get_model()
            agent = create_react_agent(model, tools)

            result = await agent.ainvoke({"messages": query})

            messages = result.get("messages", [])
            if messages:
                last_message = messages[-1]
                content = getattr(last_message, "content", None)
                if content:
                    return str(content)
            return None


def main():
    st.set_page_config(page_title="Conversational AI for GeoSpatial Data analysis", page_icon="🗺️", layout="centered")
    st.title("Location Intelligence")
    st.caption("Ask your question related to any location, its surroundings, infrastructure facilities and much more... ")
    st.caption("Uses MCP server + ReAct agent + Web search to give you accurate, real-time results")

    default_query = (
        "give me analysis of surroundings of Sarvajanik College of engineering and technology "
        "(public transportation facilities, restaurants, playgrounds, hospitals etc) along with "
        "location, including the Air quality, temperature. List down the names also and give in points."
    )

    query = st.text_area("Your query", value=default_query, height=140)
    mcp_url = st.text_input("MCP server URL", value="http://localhost:8000/mcp")

    col1, col2 = st.columns(2)
    with col1:
        run_btn = st.button("Run Query", type="primary")
    with col2:
        clear_btn = st.button("Clear Output")

    if clear_btn:
        st.session_state.pop("last_output", None)

    if run_btn:
        if not query.strip():
            st.warning("Please enter a query.")
        else:
            with st.spinner("Running agent and calling MCP tools…"):
                try:
                    output = asyncio.run(run_agent_with_query(query.strip(), mcp_url.strip()))
                    st.session_state["last_output"] = output
                except Exception as e:
                    st.error(f"Error running agent: {e}")

    if st.session_state.get("last_output"):
        st.subheader("Response")
        st.write(st.session_state["last_output"])


if __name__ == "__main__":
    main()


