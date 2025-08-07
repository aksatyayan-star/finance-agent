# File agent.py

import os
from dotenv import load_dotenv

# from google.adk.agents.llm_agent import LlmAgent
from google.adk.agents import Agent
from google.adk.tools.mcp_tool.mcp_toolset import (
    MCPToolset,
    StreamableHTTPConnectionParams,
)
from src.finance_buddy.knowledge_base.retriever import answer_conceptual_question

# Load environment variables from .env file
load_dotenv()

# --- The Correct, Synchronous Initialization Pattern ---
# The `adk run` command expects to find a fully-formed agent object
# when it imports this file. All async operations are handled by the
# MCPToolset and the ADK runner in the background.

# 1. Get configuration from environment
url = os.getenv("MCP_SERVER_URL", "http://localhost:8080/mcp/")

# 2. Define the list of tools synchronously.
print(f"MCP_SERVER_URL={url}")

tools = [
    MCPToolset(
        connection_params=StreamableHTTPConnectionParams(
            url=url,
        )
    ),
    answer_conceptual_question,
]

# 3. Define the agent instance directly at the module level.
# This is the object the ADK CLI will load and run.
root_agent = Agent(
    model='gemini-2.0-flash-001',
    name='root_agent',
    description='A helpful financial expert that can provide market data, portfolio analysis, and answer financial questions.',
    instruction="""You are a helpful and friendly financial assistant.
    Your goal is to answer user questions using the tools you have available.

    When a user asks a question that requires fetching data from their accounts (like 'get my net worth' or 'what are my transactions'), you MUST use the MCP tools. After the tool returns the data (which will be in JSON format), **DO NOT show the raw JSON to the user.** Instead, **summarize the key information** from the data into a clear, concise, and easy-to-understand sentence.

    **For conceptual or educational questions** (e.g., "What is a P/E ratio?", "Explain dollar-cost averaging"), you MUST use the `answer_conceptual_question` tool. This tool will provide you with expert knowledge from a financial knowledge base.

    When using `answer_conceptual_question`, follow these steps:
    1. Call the tool with the user's query.
    2. The tool will return a list of relevant text chunks.
    3. Synthesize the information from these chunks into a comprehensive and clear answer for the user.
    4. Cite the source URLs provided in the tool's output at the end of your answer.
    """,
    tools=tools,
)