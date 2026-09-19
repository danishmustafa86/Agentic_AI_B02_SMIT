"""
Utility module for the 2026 Agentic AI Course.
Provides model initialization for Google Gemini, Groq, or a zero-setup Mock LLM.
"""

import os
from typing import Any, List, Optional
from dotenv import load_dotenv
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage
from langchain_core.outputs import ChatGeneration, ChatResult

# Load environment variables from .env if present
load_dotenv()


class MockChatModel(BaseChatModel):
    """
    A lightweight, realistic Mock Chat Model.
    Allows all student examples to execute smoothly even without API keys!
    """

    model_name: str = "mock-llm-2026"

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Any = None,
        **kwargs: Any,
    ) -> ChatResult:
        last_msg = messages[-1] if messages else None
        last_msg_content = str(last_msg.content if last_msg else "").lower()

        # If the last message was a Tool execution result, synthesize the final answer!
        if last_msg and type(last_msg).__name__ == "ToolMessage":
            content = (
                f"[Mock LLM Final Synthesis] Based on the tool result: '{last_msg.content}', "
                "the agentic operation was successfully executed and verified."
            )
            return ChatResult(generations=[ChatGeneration(message=AIMessage(content=content, tool_calls=[]))])

        # Otherwise, inspect user input to decide if a tool should be triggered:
        tool_calls = []
        if "calculate" in last_msg_content or "25 * 4" in last_msg_content:
            tool_calls = [{
                "name": "calculator",
                "args": {"expression": "25 * 4"},
                "id": "call_calc_001",
                "type": "tool_call"
            }]
            content = "I will calculate 25 * 4 using the calculator tool."
        elif "weather" in last_msg_content:
            tool_calls = [{
                "name": "get_weather",
                "args": {"city": "San Francisco"},
                "id": "call_weather_001",
                "type": "tool_call"
            }]
            content = "Checking weather for San Francisco."
        elif "proprietary" in last_msg_content or "search" in last_msg_content or "rag" in last_msg_content or "architecture" in last_msg_content:
            tool_calls = [{
                "name": "search_knowledge_base",
                "args": {"query": "Agentic AI 2026 Architecture"},
                "id": "call_kb_001",
                "type": "tool_call"
            }]
            content = "Searching the proprietary knowledge base."
        elif "database" in last_msg_content or "query" in last_msg_content:
            tool_calls = [{
                "name": "query_database",
                "args": {"sql_query": "SELECT * FROM users LIMIT 3;"},
                "id": "call_mcp_001",
                "type": "tool_call"
            }]
            content = "Dispatching query to the MCP database server."
        else:
            content = (
                f"[Mock LLM Response] Processed your query: '{last_msg_content}'. "
                "In 2026, Agentic AI coordinates autonomous workflows via state graphs and tool calling."
            )

        ai_msg = AIMessage(content=content, tool_calls=tool_calls)
        return ChatResult(generations=[ChatGeneration(message=ai_msg)])

    @property
    def _llm_type(self) -> str:
        return "mock-chat-model"

    def bind_tools(self, tools: Any, **kwargs: Any) -> "MockChatModel":
        """Accepts tool bindings like real LangChain models."""
        return self


def get_chat_model(temperature: float = 0.0):
    """
    Returns a modern chat model based on available environment variables.
    Priority:
    1. Google Gemini (GOOGLE_API_KEY)
    2. Groq (GROQ_API_KEY)
    3. MockChatModel (Zero setup fallback)
    """
    google_key = os.getenv("GOOGLE_API_KEY")
    groq_key = os.getenv("GROQ_API_KEY")

    if google_key and not google_key.startswith("your_"):
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            print("[INFO] Using Google Gemini LLM (gemini-2.5-flash-lite)")
            return ChatGoogleGenerativeAI(
                model="gemini-2.5-flash-lite",
                temperature=temperature,
                google_api_key=google_key,
            )
        except Exception as e:
            print(f"[WARN] Failed to load Google Gemini: {e}")

    if groq_key and not groq_key.startswith("your_"):
        try:
            from langchain_groq import ChatGroq
            print("[INFO] Using Groq LLM (openai/gpt-oss-120b)")
            return ChatGroq(
                model="openai/gpt-oss-120b",
                temperature=temperature,
                groq_api_key=groq_key,
            )
        except Exception as e:
            print(f"[WARN] Failed to load Groq: {e}")

    print("[INFO] No active API key found in .env. Using built-in Mock LLM for simulation.")
    return MockChatModel()


def print_section(title: str):
    """Utility for clean console output."""
    print("\n" + "=" * 60)
    print(f"  {title.upper()}")
    print("=" * 60)
