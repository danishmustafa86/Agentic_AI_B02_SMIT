"""
01_langchain_basics_and_chains.py
==================================
Topic: LangChain Fundamentals & LCEL (LangChain Expression Language)

Key Concepts for 2026:
1. Prompts: ChatPromptTemplate for structured inputs.
2. LCEL Composition: Using the pipe operator `|` to link components.
3. Output Parsers: Converting raw AIMessage to clean strings or schemas.
4. Sequential Chaining: Connecting multiple steps deterministically.
5. Tool Binding: Introducing `bind_tools` to prepare an LLM for agentic tasks.
"""

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.tools import tool
from utils import get_chat_model, print_section


# -------------------------------------------------------------
# 1. Defining a Tool (Used in modern Agentic AI)
# -------------------------------------------------------------
@tool
def get_stock_price(ticker: str) -> str:
    """Returns the current mock stock price for a given ticker symbol."""
    mock_prices = {"AAPL": "$230.50", "GOOGL": "$180.25", "NVDA": "$125.00"}
    return mock_prices.get(ticker.upper(), "$100.00")


def main():
    print_section("01: LangChain Basics & LCEL Chaining")

    # Step 1: Initialize the Model (Google Gemini, Groq, or Mock fallback)
    model = get_chat_model(temperature=0.3)

    # ---------------------------------------------------------
    # Part A: Simple Prompt + Model + Output Parser Chain
    # ---------------------------------------------------------
    print("\n--- Part A: Basic LCEL Pipe (Prompt | Model | StrOutputParser) ---")

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an AI tech analyst specializing in 2026 Agentic AI developments."),
        ("human", "Explain the significance of '{concept}' in 2 concise sentences.")
    ])

    # In modern LangChain, components are piped together using `|`
    chain = prompt | model | StrOutputParser()

    result = chain.invoke({"concept": "autonomous agent workflows"})
    print(f"\nResult:\n{result}")

    # ---------------------------------------------------------
    # Part B: Sequential Chaining (Step 1 -> Step 2)
    # ---------------------------------------------------------
    print("\n--- Part B: Sequential Chaining (Idea -> Pitch) ---")

    # Step 1: Generate product idea
    idea_prompt = ChatPromptTemplate.from_template(
        "Generate a 1-sentence product concept for an AI agent in the {industry} industry."
    )
    idea_chain = idea_prompt | model | StrOutputParser()

    # Step 2: Create elevator pitch from the idea
    pitch_prompt = ChatPromptTemplate.from_template(
        "Create an exciting 2-sentence elevator pitch for this product:\n{idea}"
    )
    pitch_chain = pitch_prompt | model | StrOutputParser()

    # Run sequentially:
    product_idea = idea_chain.invoke({"industry": "Education"})
    print(f"Step 1 (Idea): {product_idea}")

    elevator_pitch = pitch_chain.invoke({"idea": product_idea})
    print(f"Step 2 (Pitch): {elevator_pitch}")

    # ---------------------------------------------------------
    # Part C: Tool Binding (The Bridge to Agents)
    # ---------------------------------------------------------
    print("\n--- Part C: Tool Binding with model.bind_tools() ---")

    # In 2026, models don't just chat; they are bound to tools!
    model_with_tools = model.bind_tools([get_stock_price])

    # Call with a query requiring the tool
    response = model_with_tools.invoke("What is the current stock price for AAPL?")
    print(f"Model Response Type: {type(response).__name__}")
    if response.tool_calls:
        print(f"Detected Tool Calls: {response.tool_calls}")
    else:
        print(f"Response Content: {response.content}")

    print("\n[SUCCESS] Lesson 01 completed. Moving from static chains to graph-based agents!")


if __name__ == "__main__":
    main()
