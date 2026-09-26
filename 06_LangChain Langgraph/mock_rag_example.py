"""
mock_rag_example.py
===================
Offline Mock Testing Suite for Agentic RAG (Zero API Key Requirement).

Purpose for Students & Instructors:
- Validates the complete RAG lifecycle offline without external network or API keys.
- Step 1: Ingestion -> Loads mock domain documents.
- Step 2: Chunking  -> Splits text using RecursiveCharacterTextSplitter.
- Step 3: Indexing  -> Builds an InMemoryVectorStore with deterministic embeddings.
- Step 4: Retrieval -> Validates vector similarity search scoring.
- Step 5: Agentic   -> Runs a LangGraph ReAct agent with MockChatModel to verify tool calling.
"""

import math
import hashlib
from typing import List, Optional
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.prebuilt import ToolNode, tools_condition
from utils import MockChatModel, print_section


# -------------------------------------------------------------
# 1. Zero-Setup Teaching Embeddings
# -------------------------------------------------------------
class MockTeachingEmbeddings(Embeddings):
    """Deterministic hash-based semantic embedding for offline testing."""

    def __init__(self, dims: int = 256):
        self.dims = dims

    def _hash(self, token: str) -> int:
        return int(hashlib.md5(token.encode("utf-8")).hexdigest(), 16) % self.dims

    def _embed(self, text: str) -> List[float]:
        vec = [0.0] * self.dims
        words = text.lower().replace(".", " ").replace(",", " ").replace("?", " ").split()
        for w in words:
            vec[self._hash(w)] += 2.0
            for i in range(max(1, len(w) - 2)):
                vec[self._hash(w[i : i + 3])] += 1.0

        mag = math.sqrt(sum(x * x for x in vec))
        return [x / mag for x in vec] if mag > 0 else vec

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [self._embed(t) for t in texts]

    def embed_query(self, text: str) -> List[float]:
        return self._embed(text)


# -------------------------------------------------------------
# 2. Step 1: Ingestion (Source Knowledge)
# -------------------------------------------------------------
def get_mock_documents() -> List[Document]:
    """Provides private domain documents for testing."""
    return [
        Document(
            page_content="Agentic AI systems in 2026 use modular LangGraph state machines and MCP tool interfaces.",
            metadata={"source": "doc_arch_01.txt", "topic": "architecture"}
        ),
        Document(
            page_content="Agents maintain episodic, semantic, and procedural memory to preserve context across turns.",
            metadata={"source": "doc_memory_02.txt", "topic": "memory"}
        ),
        Document(
            page_content="LangGraph checkpointers like PostgresSaver provide time-travel debugging and session persistence.",
            metadata={"source": "doc_safety_03.txt", "topic": "checkpoints"}
        )
    ]


# Global vector store for the mock tool
_mock_vector_store: Optional[InMemoryVectorStore] = None


# -------------------------------------------------------------
# 3. Step 4: Retrieval Tool
# -------------------------------------------------------------
@tool
def search_knowledge_base(query: str) -> str:
    """Searches the proprietary 2026 knowledge base for facts matching the query."""
    global _mock_vector_store
    if _mock_vector_store is None:
        return "Vector store uninitialized."

    docs = _mock_vector_store.similarity_search(query, k=1)
    if docs:
        return f"[Retrieved Chunk from {docs[0].metadata['source']}]: {docs[0].page_content}"
    return "No relevant documents found."


# -------------------------------------------------------------
# 4. Step 5: Mock Agentic Graph
# -------------------------------------------------------------
def run_mock_rag_pipeline():
    print_section("MOCK RAG TESTING SUITE (100% Offline)")

    # Phase 1: Ingestion
    print("\n[Test 1: Ingestion]")
    docs = get_mock_documents()
    print(f"-> Ingested {len(docs)} documents.")
    assert len(docs) == 3, "Expected 3 documents"

    # Phase 2: Chunking
    print("\n[Test 2: Chunking]")
    splitter = RecursiveCharacterTextSplitter(chunk_size=70, chunk_overlap=15)
    chunks = splitter.split_documents(docs)
    print(f"-> Split into {len(chunks)} chunks.")
    assert len(chunks) >= 3, "Expected at least 3 chunks"

    # Phase 3: Indexing
    print("\n[Test 3: Vector Store Indexing]")
    embeddings = MockTeachingEmbeddings()
    global _mock_vector_store
    _mock_vector_store = InMemoryVectorStore(embeddings)
    _mock_vector_store.add_documents(chunks)
    print(f"-> Successfully indexed {len(chunks)} chunks into InMemoryVectorStore.")

    # Phase 4: Direct Vector Search Verification
    print("\n[Test 4: Vector Similarity Search Verification]")
    query = "What architecture do 2026 agents use?"
    results = _mock_vector_store.similarity_search(query, k=1)
    print(f"-> Query: '{query}'")
    print(f"-> Top Result: {results[0].page_content}")
    assert "architecture" in results[0].page_content.lower() or "langgraph" in results[0].page_content.lower(), "Retrieved content did not match target topic"

    # Phase 5: End-to-End Agentic RAG Graph with MockChatModel
    print("\n[Test 5: LangGraph Agentic RAG Execution]")
    mock_llm = MockChatModel().bind_tools([search_knowledge_base])

    def mock_agent_node(state: MessagesState):
        return {"messages": [mock_llm.invoke(state["messages"])]}

    builder = StateGraph(MessagesState)
    builder.add_node("agent", mock_agent_node)
    builder.add_node("tools", ToolNode([search_knowledge_base]))

    builder.add_edge(START, "agent")
    builder.add_conditional_edges("agent", tools_condition, {"tools": "tools", END: END})
    builder.add_edge("tools", "agent")
    rag_app = builder.compile()

    test_input = [HumanMessage(content="What architecture do 2026 agents use? search knowledge base")]
    output = rag_app.invoke({"messages": test_input})

    # Verify message trace
    has_tool_call = any(hasattr(m, "tool_calls") and m.tool_calls for m in output["messages"])
    has_tool_result = any(type(m).__name__ == "ToolMessage" for m in output["messages"])
    final_message = output["messages"][-1]

    print(f"-> Tool Call Verified: {has_tool_call}")
    print(f"-> Tool Execution Verified: {has_tool_result}")
    print(f"-> Final LLM Output: {final_message.content}")

    assert has_tool_call, "Agent should have triggered a tool call"
    assert has_tool_result, "Agent should have received a ToolMessage"
    assert final_message.content, "Final message should not be empty"

    print("\n" + "=" * 60)
    print("  ALL MOCK RAG TESTS PASSED! (Zero API Keys Required)")
    print("=" * 60)


if __name__ == "__main__":
    run_mock_rag_pipeline()
