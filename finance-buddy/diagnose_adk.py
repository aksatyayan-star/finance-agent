# diagnose_adk.py
import inspect
import sys

print("--- ADK Diagnostics ---")

try:
    # 1. Attempt to import the MCPToolset, which seems to exist.
    from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
    print("✅ MCPToolset class found successfully.")

    # 2. Inspect its constructor to see what arguments it accepts.
    signature = inspect.signature(MCPToolset)
    print("\nConstructor signature for MCPToolset:")
    print(f"MCPToolset{signature}")

    # 3. List all classes in that same module.
    print("\nOther classes in google.adk.tools.mcp_tool.mcp_toolset:")
    from google.adk.tools.mcp_tool import mcp_toolset
    for name, obj in inspect.getmembers(mcp_toolset):
        if inspect.isclass(obj):
            print(f"- {name}")

except ImportError as e:
    print(f"❌ Critical Error: Failed to import a core part of ADK. {e}")
    print("Your ADK installation seems broken. Please try reinstalling it with:")
    print("uv pip install --reinstall google-adk==1.8.0")
except Exception as e:
    print(f"An unexpected error occurred: {e}")

print("\n--- Next Steps ---")
print("Use the constructor signature printed above to update your agent code.")
