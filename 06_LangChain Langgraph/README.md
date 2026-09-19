# 🚀 2026 Agentic AI Masterclass: LangChain, LangGraph, LangSmith, RAG & MCP

Welcome to the **Agentic AI 2026** course module! This repository contains a progressive, hands-on curriculum transitioning from traditional linear chains to production-grade autonomous agent graphs, memory persistence, observability, Agentic RAG, and the open standard **Model Context Protocol (MCP)**.

---

## 📦 Required Libraries (`pip install`)

To run LangChain, LangGraph, free LLM providers, and MCP in 2026, install the following:

### One-Line Install:
```bash
pip install -r requirements.txt
```

### Or install by category:

1. **Core Agentic Frameworks**:
   ```bash
   pip install langchain langchain-core langchain-community langgraph
   ```
2. **Production Observability & Tracing**:
   ```bash
   pip install langsmith
   ```
3. **Free LLM Providers (Google Gemini & Groq)**:
   ```bash
   pip install langchain-google-genai langchain-groq
   ```
4. **Model Context Protocol (MCP)**:
   ```bash
   pip install mcp langchain-mcp-adapters
   ```
5. **Config & Environment**:
   ```bash
   pip install python-dotenv pydantic
   ```

---

## 🔑 Environment & API Keys (Zero-Setup Friendly!)

You can run these scripts in two ways:

1. **With Free API Keys (Recommended for live AI responses)**:
   - Copy `.env.example` to `.env`:
     ```bash
     cp .env.example .env
     ```
   - Add your free **Google Gemini** API key ([Google AI Studio](https://aistudio.google.com/)) OR free **Groq** API key ([Groq Console](https://console.groq.com/keys)).
   - Optional: Add your free [LangSmith API Key](https://smith.langchain.com/) for visual execution traces.

2. **Zero-Setup Mock Fallback**:
   - If no API key is provided, all scripts will automatically fall back to an integrated, realistic `MockChatModel` in `utils.py`. You and your students can immediately run and study every single file without configuration friction!

---

## 📚 Curriculum Roadmap & Files

| File | Concept | What You Will Learn |
| :--- | :--- | :--- |
| **`01_langchain_basics_and_chains.py`** | **LCEL & Chains** | Prompt templates, chat models, output parsing, pipe syntax (`\|`), sequential chaining, and tool binding. |
| **`02_langgraph_nodes_and_edges.py`** | **LangGraph Primitives** | Why graphs replace linear chains, `TypedDict` state, 3 linear nodes (`cleaner -> reasoner -> formatter`), deterministic edges. |
| **`03_langgraph_conditional_edges.py`** | **Dynamic Routing & Loops** | `add_conditional_edges`, query classification router, dynamic branching, and self-reflection quality check cycles. |
| **`04_react_agent_with_tools.py`** | **ReAct Agent Loop** | The industry-standard Reasoning + Acting loop with `MessagesState`, `@tool`, `ToolNode`, and `tools_condition`. |
| **`05_agent_memory_and_persistence.py`** | **Memory & Checkpointers** | `MemorySaver`, thread isolation (`thread_id`), multi-turn memory retention, state inspection, and time travel. |
| **`06_langsmith_tracing_and_human_in_the_loop.py`** | **Observability & HITL** | LangSmith project tracing, `@traceable` decorators, `interrupt_before` breakpoints, human approval workflows. |
| **`07_rag_agent_google_or_groq.py`** | **Agentic RAG** | Vector knowledge base retriever tool, dynamic information retrieval, grounded synthesis with Gemini/Groq. |
| **`08_mcp_agent_integration.py`** | **Model Context Protocol (MCP)** | Decoupled tool architecture, MCP servers (`tools/list`, `tools/call`), and `langchain-mcp-adapters` integration. |

---

## 🏃 Quick Execution

Run any file directly with Python:

```bash
python 01_langchain_basics_and_chains.py
python 02_langgraph_nodes_and_edges.py
python 03_langgraph_conditional_edges.py
python 04_react_agent_with_tools.py
python 05_agent_memory_and_persistence.py
python 06_langsmith_tracing_and_human_in_the_loop.py
python 07_rag_agent_google_or_groq.py
python 08_mcp_agent_integration.py
```
