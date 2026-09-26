"""
07_rag_agent_google_or_groq.py
================================
Topic: Complete Agentic RAG (Retrieval-Augmented Generation) with Google Gemini / Groq

Pedagogical Order of RAG (2026 Standards):
1. Ingestion: Load raw proprietary documents into structured Document objects.
2. Chunking: Split documents into semantically coherent chunks using RecursiveCharacterTextSplitter.
3. Indexing: Convert chunks into vector embeddings and index them in an InMemoryVectorStore.
   - Works with Free Google Gemini API key (models/gemini-embedding-001)
   - Works with Groq API key or Offline (via built-in zero-setup TeachingEmbeddings)
4. Retrieval Tool: Wrap vector store similarity search inside a LangChain @tool.
5. Agentic Graph: Build a LangGraph state machine where the agent dynamically decides
   when, what, and how to search the vector index.
6. Synthesis: Synthesize grounded answers backed by retrieved evidence.
"""

import os
import sys
import math
import hashlib
from typing import List, Optional
from dotenv import load_dotenv

# Ensure proper utf-8 encoding on Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.prebuilt import ToolNode, tools_condition
from utils import get_chat_model, MockChatModel, print_section

load_dotenv()


# -------------------------------------------------------------
# 1. Zero-Setup Embeddings (Groq & Offline Fallback)
# -------------------------------------------------------------
class TeachingEmbeddings(Embeddings):
    """
    Deterministic semantic vector generator for zero-setup learning and Groq users.
    Groq provides ultra-fast LLM inference but does not host an embedding endpoint.
    This class ensures vector indexing and cosine similarity search work 100% reliably
    even without paid vector databases or third-party embedding subscriptions!
    """

    def __init__(self, dims: int = 512):
        self.dims = dims

    def _hash(self, token: str) -> int:
        return int(hashlib.md5(token.encode("utf-8")).hexdigest(), 16) % self.dims

    def _embed(self, text: str) -> List[float]:
        vec = [0.0] * self.dims
        words = text.lower().replace(".", " ").replace(",", " ").replace("?", " ").replace("!", " ").split()
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


def get_embeddings() -> Embeddings:
    """
    Selects the best available embedding model:
    1. Google Gemini Embeddings (free tier) if GOOGLE_API_KEY is configured.
    2. TeachingEmbeddings if using Groq (which has no embedding API) or testing offline.
    """
    google_key = os.getenv("GOOGLE_API_KEY")
    if google_key and not google_key.startswith("your_"):
        try:
            from langchain_google_genai import GoogleGenerativeAIEmbeddings
            print("[INFO] Embedding Provider: Google Gemini (models/gemini-embedding-001)")
            return GoogleGenerativeAIEmbeddings(
                model="models/gemini-embedding-001",
                google_api_key=google_key,
            )
        except Exception as e:
            print(f"[WARN] Failed to load Google Gemini Embeddings ({e}). Falling back to TeachingEmbeddings.")

    print("[INFO] Embedding Provider: Zero-setup TeachingEmbeddings (Groq/Offline compatible).")
    return TeachingEmbeddings()


# -------------------------------------------------------------
# 2. Step 1: Raw Knowledge Ingestion (Source Documents)
# -------------------------------------------------------------
def load_proprietary_knowledge() -> List[Document]:
    """
    Simulates loading private enterprise/course knowledge.
    LLMs cannot know this information without RAG!
    """
    return [
        Document(
            page_content=(
                "In 2026, leading Agentic AI systems shifted from monolithic prompt engineering to modular "
                "LangGraph state machines. These architectures use standardized MCP (Model Context Protocol) "
                "interfaces for tool integration and run deterministic graph cycles with Human-in-the-Loop checkpoints."
            ),
            metadata={"source": "spec_2026_architecture.md", "topic": "Agentic Architecture 2026"}
        ),
        Document(
            page_content=(
                "Cognitive Memory in 2026 AI Agents is partitioned into three distinct layers: "
                "1. Episodic Memory (retains conversation threads and short-term dialogue state), "
                "2. Semantic Memory (indexes long-term knowledge via vector stores and RAG), and "
                "3. Procedural Memory (encodes executable workflows and LangGraph transitions)."
            ),
            metadata={"source": "spec_2026_memory.md", "topic": "Agentic Memory Hierarchy"}
        ),
        Document(
            page_content=(
                "LangGraph checkpointers support time-travel debugging and distributed session persistence. "
                "Enterprise systems deploy PostgresSaver or DynamoDBSaver checkpointers to ensure failover resilience "
                "and allow humans to inspect, approve, or roll back agent decisions before sensitive operations."
            ),
            metadata={"source": "spec_2026_persistence.md", "topic": "Persistence & Safety"}
        )
    ]


# -------------------------------------------------------------
# 3. Step 2 & 3: Chunking & Vector Store Indexing
# -------------------------------------------------------------
def build_vector_store_index() -> InMemoryVectorStore:
    """
    Executes the classic RAG Indexing Pipeline:
    1. Ingestion: Load raw documents.
    2. Chunking: Split documents using RecursiveCharacterTextSplitter.
    3. Indexing: Embed and store chunks in an InMemoryVectorStore.
    """
    raw_docs = load_proprietary_knowledge()
    print(f"\n[Step 1: Ingestion] Loaded {len(raw_docs)} proprietary knowledge documents.")

    # Chunking: Recursive splitting ensures coherent paragraphs and token limits
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=180,  # Demonstrating overlap windows: [0..180], [150..330], [300..480], [450..630]
        chunk_overlap=30,
        separators=["\n\n", "\n", ". ", " "]
    )
    chunks = splitter.split_documents(raw_docs)
    print(f"[Step 2: Chunking] Split into {len(chunks)} semantic chunks (chunk_size=180, overlap=30).")

    # Indexing: Embed chunks into vector store
    embedding_model = get_embeddings()
    vector_store = InMemoryVectorStore(embedding_model)
    vector_store.add_documents(chunks)
    print(f"[Step 3: Indexing] Indexed {len(chunks)} chunks into InMemoryVectorStore successfully.")

    return vector_store


# Global reference for the retrieval tool
_vector_store: Optional[InMemoryVectorStore] = None


# -------------------------------------------------------------
# 4. Step 4: Exposing Vector Store as an Agentic Tool
# -------------------------------------------------------------
@tool
def search_knowledge_base(query: str) -> str:
    """
    Searches the proprietary 2026 Agentic AI knowledge base using vector similarity search.
    Input should be a specific search query, e.g. '2026 agent memory architecture'.
    """
    global _vector_store
    if _vector_store is None:
        return "Error: Vector store has not been initialized."

    print(f"   -> [Tool Execution: search_knowledge_base] Querying vector index for: '{query}'")
    retrieved_docs = _vector_store.similarity_search(query, k=2)

    if not retrieved_docs:
        return "No matching documents found in the proprietary knowledge base."

    formatted_results = []
    for i, doc in enumerate(retrieved_docs, start=1):
        source = doc.metadata.get("source", "unknown")
        topic = doc.metadata.get("topic", "general")
        formatted_results.append(
            f"--- Chunk {i} [{source} | {topic}] ---\n{doc.page_content}"
        )

    return "\n\n".join(formatted_results)


tools = [search_knowledge_base]


# -------------------------------------------------------------
# 5. Step 5: Agent Reasoning Node & StateGraph
# -------------------------------------------------------------
def rag_agent_node(state: MessagesState) -> dict:
    """
    Agentic Reasoning Node:
    The LLM inspects conversation history and decides whether to query
    the vector database or synthesize an answer.
    Includes graceful automatic fallback to Groq or Mock LLM if Gemini rate limits are hit.
    """
    # Check if student explicitly requested Groq via environment
    if os.getenv("LLM_PROVIDER", "").lower() == "groq" and os.getenv("GROQ_API_KEY"):
        from langchain_groq import ChatGroq
        groq_model = ChatGroq(
            model="openai/gpt-oss-120b",
            temperature=0.0,
            groq_api_key=os.getenv("GROQ_API_KEY"),
        )
        response = groq_model.bind_tools(tools).invoke(state["messages"])
        return {"messages": [response]}

    model = get_chat_model(temperature=0.0)
    try:
        model_with_tools = model.bind_tools(tools)
        response = model_with_tools.invoke(state["messages"])
        return {"messages": [response]}
    except Exception as e:
        err_str = str(e)
        # Automatic resilience against Gemini 429 quota exhaustion on free tiers
        if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str or "quota" in err_str.lower():
            print("\n[WARN] Gemini quota limit reached (429). Seamlessly falling back to Groq LLM...")
            groq_key = os.getenv("GROQ_API_KEY")
            if groq_key and not groq_key.startswith("your_"):
                from langchain_groq import ChatGroq
                groq_model = ChatGroq(
                    model="openai/gpt-oss-120b",
                    temperature=0.0,
                    groq_api_key=groq_key,
                )
                response = groq_model.bind_tools(tools).invoke(state["messages"])
                return {"messages": [response]}
            else:
                print("[WARN] Groq key unavailable. Falling back to MockChatModel...")
                mock_model = MockChatModel().bind_tools(tools)
                response = mock_model.invoke(state["messages"])
                return {"messages": [response]}
        raise e


def build_rag_graph():
    """Builds the LangGraph Agentic RAG workflow with tool-calling loop."""
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
    return builder.compile()


# -------------------------------------------------------------
# 6. Step 6: End-to-End Execution
# -------------------------------------------------------------
def main():
    print_section("07: Complete Agentic RAG (Gemini / Groq / Mock)")

    # 1. Build Indexing (Ingest -> Chunk -> Embed -> Index)
    global _vector_store
    _vector_store = build_vector_store_index()

    # 2. Compile LangGraph Agent
    rag_app = build_rag_graph()

    # 3. User query requiring private knowledge
    user_query = "What memory layers do modern 2026 AI agents combine, and what architecture do they run on?"
    print(f"\n[User Query]: '{user_query}'\n")

    input_messages = [
        SystemMessage(
            content=(
                "You are an enterprise AI assistant. Answer the user's questions accurately. "
                "Use the search_knowledge_base tool to look up facts from the proprietary documentation."
            )
        ),
        HumanMessage(content=user_query)
    ]

    # 4. Execute Agentic RAG
    print("--- Executing Agentic RAG Workflow ---")
    result = rag_app.invoke({"messages": input_messages})

    # 5. Display Tracing & Grounded Synthesis
    print("\n--- Agentic RAG Execution Trace ---")
    for msg in result["messages"]:
        sender = type(msg).__name__
        if hasattr(msg, "tool_calls") and msg.tool_calls:
            print(f"\n[{sender}] Decided to Retrieve from Vector Store:")
            for call in msg.tool_calls:
                print(f"   Query: '{call['args'].get('query', '')}'")
        elif sender == "ToolMessage":
            print(f"\n[{sender}] Retrieved Vector Chunks:\n{msg.content}")
        elif sender == "AIMessage" and msg.content:
            print(f"\n[Final Grounded Answer]:\n{msg.content}")

    print("\n[SUCCESS] Lesson 07 completed! You mastered the complete RAG lifecycle: Ingestion -> Chunking -> Indexing -> Agentic Retrieval -> Grounded Generation.")


if __name__ == "__main__":
    main()
