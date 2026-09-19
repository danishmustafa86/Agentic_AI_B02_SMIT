"""
08_mcp_agent_integration.py
============================
Topic: Model Context Protocol (MCP) Integration with LangChain & LangGraph

Key Concepts for 2026:
1. What is MCP?
   - The universal open standard (introduced by Anthropic) for connecting AI models to
     external tools, databases, and enterprise data sources safely.
   - Decouples tool implementation from the LLM framework: write an MCP server once,
     and any agent (LangGraph, Claude Desktop, Cursor, Gemini) can use it.
2. The MCP Architecture:
   - MCP Server: Exposes tools, prompts, and resources over JSON-RPC (stdio or SSE).
   - MCP Client / Host: The agent framework (LangChain/LangGraph) discovering and calling tools.
3. LangChain MCP Adapters:
   - Converting standard MCP tool specifications into LangChain `BaseTool` objects.
"""

from typing import Any, Dict
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.prebuilt import ToolNode, tools_condition
from utils import get_chat_model, print_section


# -------------------------------------------------------------
# 1. Simulating an MCP Server's Tool Endpoint
# -------------------------------------------------------------
# In a real MCP setup, this runs as a separate process or microservice.
# The server declares its capabilities via JSON-RPC.

class MockEnterpriseMCPServer:
    """Simulates an external enterprise MCP Server exposing a database tool."""

    @staticmethod
    def get_tool_metadata() -> Dict[str, Any]:
        """Equivalent to MCP `tools/list` response."""
        return {
            "name": "query_database",
            "description": "Executes read-only SQL queries against the enterprise user database.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "sql_query": {
                        "type": "string",
                        "description": "The SQL query to run, e.g. SELECT * FROM users LIMIT 3;"
                    }
                },
                "required": ["sql_query"]
            }
        }

    @staticmethod
    def call_tool(arguments: Dict[str, Any]) -> str:
        """Equivalent to MCP `tools/call` execution."""
        query = arguments.get("sql_query", "")
        print(f"   [MCP SERVER RPC] Received JSON-RPC request for 'query_database': '{query}'")
        # Simulated database return
        return (
            "| user_id | username | role        | status |\n"
            "|---------|----------|-------------|--------|\n"
            "| 101     | Alice    | Lead Dev    | Active |\n"
            "| 102     | Bob      | QA Engineer | Active |\n"
            "| 103     | Charlie  | DevOps      | Active |"
        )


# -------------------------------------------------------------
# 2. MCP Adapter: Bridging MCP Tool to LangChain BaseTool
# -------------------------------------------------------------
# LangChain's `langchain-mcp-adapters` converts MCP tools into standard LangChain tools:

@tool
def query_database(sql_query: str) -> str:
    """Executes read-only SQL queries against the enterprise user database via MCP."""
    # Dispatches the call across the MCP protocol bridge
    return MockEnterpriseMCPServer.call_tool({"sql_query": sql_query})


mcp_tools = [query_database]


# -------------------------------------------------------------
# 3. LangGraph Agent Powered by MCP Tools
# -------------------------------------------------------------
def mcp_agent_node(state: MessagesState) -> dict:
    """Agent node that reasons and triggers MCP-provided tools."""
    model = get_chat_model()
    # The agent binds the MCP tools just like native tools!
    model_with_mcp = model.bind_tools(mcp_tools)
    response = model_with_mcp.invoke(state["messages"])
    return {"messages": [response]}


def main():
    print_section("08: Model Context Protocol (MCP) in Agentic AI")

    print("\n--- MCP Architecture Overview ---")
    meta = MockEnterpriseMCPServer.get_tool_metadata()
    print(f"Discovered MCP Tool: {meta['name']}")
    print(f"Description: {meta['description']}")
    print(f"Schema: {meta['input_schema']}")

    # ---------------------------------------------------------
    # 4. Construct the Graph with MCP ToolNode
    # ---------------------------------------------------------
    builder = StateGraph(MessagesState)
    builder.add_node("agent", mcp_agent_node)
    builder.add_node("mcp_tools", ToolNode(mcp_tools))

    builder.add_edge(START, "agent")
    builder.add_conditional_edges(
        "agent",
        tools_condition,
        {"tools": "mcp_tools", END: END}
    )
    builder.add_edge("mcp_tools", "agent")

    app = builder.compile()

    # ---------------------------------------------------------
    # 5. Run the Agent Querying the MCP Server
    # ---------------------------------------------------------
    user_query = "Please query the database for the first 3 active users."
    print(f"\nUser Request: '{user_query}'\n")

    input_messages = [
        SystemMessage(content="You are an enterprise AI coordinator with access to MCP database tools."),
        HumanMessage(content=user_query)
    ]

    result = app.invoke({"messages": input_messages})

    print("\n--- Execution & MCP Response Trace ---")
    for msg in result["messages"]:
        sender = type(msg).__name__
        if hasattr(msg, "tool_calls") and msg.tool_calls:
            print(f"[{sender}] Dispatched MCP Tool Call: {msg.tool_calls}")
        elif sender == "ToolMessage":
            print(f"[{sender}] Data Returned from MCP Server:\n{msg.content}")
        elif sender == "AIMessage":
            print(f"\n[Agent Final Summary]:\n{msg.content}")

    print("\n[SUCCESS] Lesson 08 completed. You mastered the Model Context Protocol (MCP) in 2026!")


if __name__ == "__main__":
    main()
