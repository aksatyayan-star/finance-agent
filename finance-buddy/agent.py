# File agent.py

import os
from dotenv import load_dotenv

# from google.adk.agents.llm_agent import LlmAgent
from google.adk.agents import Agent
from google.adk.tools.mcp_tool.mcp_toolset import (
    MCPToolset,
    StreamableHTTPConnectionParams,
)

# Load environment variables from .env file
load_dotenv()

# --- The Correct, Synchronous Initialization Pattern ---
# The `adk run` command expects to find a fully-formed agent object
# when it imports this file. All async operations are handled by the
# MCPToolset and the ADK runner in the background.

# 1. Get configuration from environment
url = os.getenv("MCP_SERVER_URL", "http://localhost:8080/mcp/")
# session_id = os.getenv("MCP_SESSION_ID") # Will be None if not set

# headers = {}
# if session_id:
#     headers["Mcp-Session-Id"] = session_id

# 2. Define the list of tools synchronously.
# The MCPToolset will connect to the server when the agent starts.
# You do not need to `await` its creation.
print(f"MCP_SERVER_URL={url}")
# print(f"MCP_SESSION_ID={session_id}")

tools = [
    MCPToolset(
        connection_params=StreamableHTTPConnectionParams(
            url=url,
            # session_id=session_id,
            # headers=headers
        )
    )
]

# 3. Define the agent instance directly at the module level.
# This is the object the ADK CLI will load and run.
root_agent = Agent(
    # NOTE: 'gemini-2.0-flash' is not a standard model name.
    # You likely mean 'gemini-1.5-flash-001' or a similar valid model ID.
    # model="gemini-1.5-flash-001",
    # name="assistant",
    # instruction="""Help user extract and summarize the article from wikipedia link.
    # Use the following tools to extract wikipedia article:
    # - extract_wikipedia_article

    # Once you retrieve the article, always summarize it in a few sentences for the user.
    # """,
    model='gemini-2.0-flash-001',
    name='root_agent',
    description='A helpful assistant for user questions.',
    instruction="""You are a helpful and friendly financial assistant.
    Your goal is to answer user questions using the tools you have available.
    
    When a user asks a question that requires fetching data (like 'get my net worth' or 'what are my transactions'), you MUST follow these steps:
    1. Use the appropriate tool to get the raw data from the server.
    2. After the tool returns the data (which will be in JSON format), **DO NOT show the raw JSON to the user.**
    3. Instead, **summarize the key information** from the data into a clear, concise, and easy-to-understand sentence.
    
    For example, if a tool returns a list of transactions, you should say "You had three recent transactions, including a debit of $50 at Starbucks and a credit of $1,200 from your payroll."
    """,
    tools=tools, # Pass the synchronously created toolset
)