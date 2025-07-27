import os
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset

# ──────────────────────────────────────────
# Build an MCPToolset from environment vars
# ──────────────────────────────────────────
def _make_mcp_toolset() -> MCPToolset:
    """Return an MCPToolset wired to the Google Maps MCP server."""
    endpoint   = os.getenv("MCP_SERVER_URL", "http://localhost:8080/mcp")

    # ADK 1.8 ctor:  MCPToolset(endpoint, *, session_id=None, ...)
    return MCPToolset(endpoint)