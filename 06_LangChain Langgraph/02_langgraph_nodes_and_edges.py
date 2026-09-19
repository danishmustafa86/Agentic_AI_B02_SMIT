"""
02_langgraph_nodes_and_edges.py
================================
Topic: LangGraph Core Architecture: State, Nodes, and Edges

Why LangGraph in 2026?
Standard chains are linear and one-way. Real agentic systems require:
1. Shared, mutable State that travels across steps.
2. Nodes: Specialized units of computation (functions).
3. Edges: Connectors that define execution flow (deterministic or conditional).
4. Loops & Cycles: Essential for self-reflection and retry logic.

In this file, we build a clean 3-node linear graph:
[START] -> [input_cleaner] -> [llm_reasoner] -> [formatter] -> [END]
"""

from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from utils import get_chat_model, print_section


# -------------------------------------------------------------
# 1. Defining the State
# In LangGraph, State is the single source of truth across all nodes.
# -------------------------------------------------------------
class AgentState(TypedDict):
    raw_input: str
    cleaned_input: str
    analysis: str
    final_output: str


# -------------------------------------------------------------
# 2. Defining the Nodes (Functions)
# Each node takes the current state and returns a dictionary with updates.
# -------------------------------------------------------------
def input_cleaner_node(state: AgentState) -> dict:
    """Node 1: Sanitizes and prepares the raw input."""
    raw = state.get("raw_input", "")
    cleaned = raw.strip().capitalize()
    print(f"-> [Node 1: Cleaner] Cleaned input: '{cleaned}'")
    return {"cleaned_input": cleaned}


def llm_reasoner_node(state: AgentState) -> dict:
    """Node 2: Generates reasoning using the chat model."""
    cleaned = state.get("cleaned_input", "")
    model = get_chat_model()
    
    prompt = f"Analyze the following user goal in one brief bullet point: '{cleaned}'"
    response = model.invoke(prompt)
    
    analysis_text = getattr(response, "content", str(response))
    print(f"-> [Node 2: Reasoner] Generated analysis: '{analysis_text}'")
    return {"analysis": analysis_text}


def formatter_node(state: AgentState) -> dict:
    """Node 3: Formats the final response for the user."""
    analysis = state.get("analysis", "")
    formatted = (
        "==============================\n"
        "   AGENT EXECUTION SUMMARY    \n"
        "==============================\n"
        f"Goal: {state.get('cleaned_input')}\n"
        f"Result: {analysis}\n"
        "Status: COMPLETED SUCCESSFULLY"
    )
    print("-> [Node 3: Formatter] Applied final presentation template.")
    return {"final_output": formatted}


def main():
    print_section("02: LangGraph Nodes & Edges (3-Node Linear Graph)")

    # ---------------------------------------------------------
    # 3. Constructing the StateGraph
    # ---------------------------------------------------------
    builder = StateGraph(AgentState)

    # Add the 3 nodes
    builder.add_node("cleaner", input_cleaner_node)
    builder.add_node("reasoner", llm_reasoner_node)
    builder.add_node("formatter", formatter_node)

    # Define the execution flow with deterministic edges
    builder.add_edge(START, "cleaner")
    builder.add_edge("cleaner", "reasoner")
    builder.add_edge("reasoner", "formatter")
    builder.add_edge("formatter", END)

    # ---------------------------------------------------------
    # 4. Compile the Graph
    # Compiling transforms the definition into an executable Runnable!
    # ---------------------------------------------------------
    app = builder.compile()

    # ---------------------------------------------------------
    # 5. Execute the Graph
    # ---------------------------------------------------------
    initial_input = {"raw_input": "   automate invoice reconciliation using agents in 2026   "}
    print(f"\nInitial State: {initial_input}\n")

    final_state = app.invoke(initial_input)

    print("\n--- Final Graph State ---")
    print(final_state["final_output"])
    print("\n[SUCCESS] Lesson 02 completed. You now know how to build and link LangGraph nodes!")


if __name__ == "__main__":
    main()
