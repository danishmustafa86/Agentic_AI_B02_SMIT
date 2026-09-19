"""
07_rag_agent_google_or_groq.py
================================
Topic: Agentic RAG (Retrieval-Augmented Generation) with Google Gemini / Groq

Key Concepts for 2026:
1. Traditional RAG vs. Agentic RAG:
   - Traditional: Blindly retrieves chunks and stuffs them into the prompt.
   - Agentic RAG: The agent dynamically decides *when* to search, *what* query to run,
     and can search multiple times if initial results are insufficient.
2. Knowledge Base Tool: Wrapping knowledge retrieval inside an agent `@tool`.
3. Model Integration: Powered by Google Gemini (`ChatGoogleGenerativeAI`) or Groq (`ChatGroq`).
"""

from typing import List
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.prebuilt import ToolNode, tools_condition
from utils import get_chat_model, print_section


# -------------------------------------------------------------
# 1. Private Domain Knowledge Base (2026 AI Specs)
# -------------------------------------------------------------
KNOWLEDGE_BASE = [
    {
        "topic": "Agentic AI 2026 Architecture",
        "content": "In 2026, leading Agentic AI systems shifted from monolithic prompts to modular LangGraph state machines with standardized MCP (Model Context Protocol) tool interfaces."
    },
    {
        "topic": "LangGraph Checkpointers",
        "content": "LangGraph checkpointers support time-travel debugging and multi-tenant session persistence using distributed stores like PostgresSaver or DynamoDBSaver."
    },
    {
        "topic": "Cognitive Memory in Agents",
        "content": "Modern agents combine episodic memory (conversation threads), semantic memory (vector stores), and procedural memory (executable graph workflows)."
    }
]


# -------------------------------------------------------------
# 2. Defining the Retriever Tool
# -------------------------------------------------------------
@tool
def search_knowledge_base(query: str) -> str:
    """Searches the proprietary 2026 AI knowledge base for facts matching the query."""
    print(f"   [KNOWLEDGE BASE SEARCH] Querying database for: '{query}'")
    query_lower = query.lower()
    matches: List[str] = []

    for doc in KNOWLEDGE_BASE:
        if any(word in doc["topic"].lower() or word in doc["content"].lower() for word in query_lower.split()):
            matches.append(f"[{doc['topic']}]: {doc['content']}")

    if matches:
        return "\n\n".join(matches)
    return "No matching documents found in the proprietary knowledge base."


tools = [search_knowledge_base]


# -------------------------------------------------------------
# 3. Agent Reasoning Node
# -------------------------------------------------------------
def rag_agent_node(state: MessagesState) -> dict:
    """Invokes LLM with access to the knowledge base retriever tool."""
    model = get_chat_model(temperature=0.0)
    model_with_tools = model.bind_tools(tools)
    response = model_with_tools.invoke(state["messages"])
    return {"messages": [response]}


def main():
    print_section("07: Agentic RAG with Google Gemini / Groq")

    # Construct the RAG Agent Graph
    builder = StateGraph(MessagesState)
    builder.add_node("agent", rag_agent_node)
    builder.add_node("tools", ToolNode(tools))

    builder.add_edge(START, "agent")
    builder.add_conditional_edges(
        "agent",
        tools_condition,
        {"tools": "tools", END: END}
    )
    builder.add_edge("tools", "agent")

    rag_app = builder.compile()

    # Query requiring knowledge from the proprietary database
    user_query = "What architecture do 2026 Agentic AI systems use according to our proprietary docs?"
    print(f"\nUser Query: '{user_query}'\n")

    input_messages = [
        SystemMessage(
            content="You are an enterprise research agent. Use the search_knowledge_base tool to verify facts before answering."
        ),
        HumanMessage(content=user_query)
    ]

    result = rag_app.invoke({"messages": input_messages})

    print("\n--- Agentic RAG Trace & Synthesis ---")
    for msg in result["messages"]:
        sender = type(msg).__name__
        if hasattr(msg, "tool_calls") and msg.tool_calls:
            print(f"[{sender}] Decided to Retrieve: {msg.tool_calls}")
        elif sender == "ToolMessage":
            print(f"[{sender}] Retrieved Chunks:\n{msg.content}")
        elif sender == "AIMessage":
            print(f"\n[Final Grounded Answer]:\n{msg.content}")

    print("\n[SUCCESS] Lesson 07 completed. You built an Agentic RAG workflow with dynamic retrieval!")


if __name__ == "__main__":
    main()
