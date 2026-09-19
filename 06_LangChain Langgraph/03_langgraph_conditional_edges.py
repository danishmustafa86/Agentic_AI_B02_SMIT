"""
03_langgraph_conditional_edges.py
==================================
Topic: Dynamic Routing & Cycles with Conditional Edges

Key Concepts for 2026:
1. Conditional Edges: Decisions are made at runtime by examining state.
2. Router Functions: Python functions that return the name of the next node.
3. Cyclical Loops: Allowing an agent to self-correct, refine drafts, or retry.
"""

from typing import TypedDict, Literal
from langgraph.graph import StateGraph, START, END
from utils import print_section


# -------------------------------------------------------------
# 1. State Definition with Retry/Loop Tracking
# -------------------------------------------------------------
class RouterState(TypedDict):
    query: str
    category: str
    response: str
    iterations: int
    is_satisfactory: bool


# -------------------------------------------------------------
# 2. Router & Processing Nodes
# -------------------------------------------------------------
def classify_intent_node(state: RouterState) -> dict:
    """Classifies user intent based on keywords."""
    query = state["query"].lower()
    if any(term in query for term in ["add", "calculate", "multiply", "math"]):
        category = "math"
    elif any(term in query for term in ["python", "code", "bug", "function"]):
        category = "coding"
    else:
        category = "general"
    
    print(f"-> [Router] Query classified as: '{category}'")
    return {"category": category, "iterations": state.get("iterations", 0)}


def math_expert_node(state: RouterState) -> dict:
    """Specialized node for math calculations."""
    count = state.get("iterations", 0) + 1
    print(f"-> [Math Expert (Iteration {count})] Solving calculation...")
    return {
        "response": "Computed accurately: Result is 42.",
        "iterations": count
    }


def coding_expert_node(state: RouterState) -> dict:
    """Specialized node for coding queries."""
    count = state.get("iterations", 0) + 1
    print(f"-> [Coding Expert (Iteration {count})] Generating code solution...")
    return {
        "response": "def agentic_flow(): return 'LangGraph 2026 rocks!'",
        "iterations": count
    }


def general_expert_node(state: RouterState) -> dict:
    """General question answering node."""
    count = state.get("iterations", 0) + 1
    print(f"-> [General Expert (Iteration {count})] Formulating answer...")
    return {
        "response": "Agentic AI in 2026 enables autonomous reasoning graphs.",
        "iterations": count
    }


def quality_reviewer_node(state: RouterState) -> dict:
    """
    Reviewer node that checks if the response is complete.
    Simulates a self-correction loop: requires at least 2 iterations.
    """
    current_iters = state.get("iterations", 1)
    # Self-reflection logic: approve on iteration 2
    is_ok = current_iters >= 2
    status = "APPROVED" if is_ok else "NEEDS REFINEMENT"
    print(f"-> [Reviewer] Inspection status: {status} (Iterations: {current_iters})")
    return {"is_satisfactory": is_ok}


# -------------------------------------------------------------
# 3. Routing Functions (Return the next node key)
# -------------------------------------------------------------
def route_by_category(state: RouterState) -> Literal["math_node", "coding_node", "general_node"]:
    """Directs execution to the appropriate expert."""
    cat = state.get("category", "general")
    if cat == "math":
        return "math_node"
    elif cat == "coding":
        return "coding_node"
    return "general_node"


def route_review_verdict(state: RouterState) -> Literal["revise", "finish"]:
    """Determines whether to loop back or terminate."""
    if state.get("is_satisfactory", False):
        return "finish"
    return "revise"


def main():
    print_section("03: LangGraph Conditional Edges & Self-Correction Loops")

    # Construct the Graph
    workflow = StateGraph(RouterState)

    # Add Nodes
    workflow.add_node("classifier", classify_intent_node)
    workflow.add_node("math_node", math_expert_node)
    workflow.add_node("coding_node", coding_expert_node)
    workflow.add_node("general_node", general_expert_node)
    workflow.add_node("reviewer", quality_reviewer_node)

    # 1. Start with classification
    workflow.add_edge(START, "classifier")

    # 2. Dynamic Branching: Router -> Expert
    workflow.add_conditional_edges(
        "classifier",
        route_by_category,
        {
            "math_node": "math_node",
            "coding_node": "coding_node",
            "general_node": "general_node"
        }
    )

    # 3. All experts send their output to the reviewer
    workflow.add_edge("math_node", "reviewer")
    workflow.add_edge("coding_node", "reviewer")
    workflow.add_edge("general_node", "reviewer")

    # 4. Cyclical Self-Correction: Reviewer -> finish or loop back!
    workflow.add_conditional_edges(
        "reviewer",
        route_review_verdict,
        {
            "finish": END,
            "revise": "general_node"  # Loop back to refine
        }
    )

    app = workflow.compile()

    # Test with a coding query
    print("\n--- Test 1: Routing Coding Query with Quality Check Cycle ---")
    res1 = app.invoke({
        "query": "Write a python function for my agent",
        "iterations": 0,
        "is_satisfactory": False
    })
    print(f"\nFinal Verdict: Iterations={res1['iterations']} | Satisfactory={res1['is_satisfactory']}")
    print(f"Final Response: {res1['response']}")

    # Test with a math query
    print("\n--- Test 2: Routing Math Query ---")
    res2 = app.invoke({
        "query": "Please calculate 25 * 4",
        "iterations": 1,  # Set to 1 so reviewer approves immediately
        "is_satisfactory": False
    })
    print(f"\nFinal Response: {res2['response']}")

    print("\n[SUCCESS] Lesson 03 completed. You mastered dynamic routing and cycles in LangGraph!")


if __name__ == "__main__":
    main()
