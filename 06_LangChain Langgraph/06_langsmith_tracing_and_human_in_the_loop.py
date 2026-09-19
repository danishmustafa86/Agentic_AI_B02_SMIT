"""
06_langsmith_tracing_and_human_in_the_loop.py
==============================================
Topic: Production Agentic AI: LangSmith Tracing & Human-in-the-Loop (HITL)

Key Concepts for 2026:
1. LangSmith Observability:
   - Tracing LLM calls, latency, and tool invocations.
   - Custom tracing using `@traceable`.
2. Human-in-the-Loop (HITL):
   - Pausing execution before high-stakes actions (e.g. wire transfer, DB update).
   - `interrupt_before` breakpoints.
   - Inspecting pending action, approving/editing, and resuming execution.
"""

import os
from typing import TypedDict
from langsmith import traceable
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from utils import print_section


# -------------------------------------------------------------
# 1. LangSmith Configuration Overview
# -------------------------------------------------------------
def configure_langsmith_observability():
    """Explains and configures LangSmith environment variables."""
    # When enabled, all LangChain & LangGraph calls automatically stream traces to LangSmith!
    if os.getenv("LANGCHAIN_TRACING_V2") == "true" and os.getenv("LANGCHAIN_API_KEY"):
        print("[LangSmith] Live tracing is ACTIVE -> Project: " + os.getenv("LANGCHAIN_PROJECT", "default"))
    else:
        print("[LangSmith] Tracing is inactive (no API key set). Set keys in .env to view web UI traces.")


# Custom function traced with LangSmith
@traceable(name="verify_compliance_rules", tags=["security", "compliance"])
def verify_compliance_rules(amount: float, recipient: str) -> bool:
    """A business logic rule traced by LangSmith."""
    # Flag amounts >= $1,000 for human approval
    return amount < 1000.0


# -------------------------------------------------------------
# 2. State & Nodes for Sensitive Transaction
# -------------------------------------------------------------
class PaymentState(TypedDict):
    recipient: str
    amount: float
    is_approved: bool
    status: str


def draft_transaction_node(state: PaymentState) -> dict:
    """Node 1: Drafts the transaction and checks compliance."""
    print(f"-> [Node 1: Drafter] Drafting payment of ${state['amount']} to '{state['recipient']}'")
    auto_allowed = verify_compliance_rules(state["amount"], state["recipient"])
    if auto_allowed:
        return {"is_approved": True, "status": "AUTO_APPROVED"}
    else:
        print("   [ALERT] Amount exceeds $1,000 threshold. Escalating for Human Review!")
        return {"is_approved": False, "status": "PENDING_HUMAN_APPROVAL"}


def execute_payment_node(state: PaymentState) -> dict:
    """Node 2 (High Stakes): Executes the actual wire transfer."""
    if state.get("is_approved", False):
        print(f"-> [Node 2: High-Stakes Action] WIRE TRANSFERRED ${state['amount']} to '{state['recipient']}'!")
        return {"status": "FUNDS_DISPATCHED_SUCCESSFULLY"}
    else:
        print("-> [Node 2: High-Stakes Action] TRANSACTION CANCELLED: Human rejected approval.")
        return {"status": "TRANSACTION_REJECTED"}


def main():
    print_section("06: LangSmith Tracing & Human-in-the-Loop (HITL)")
    configure_langsmith_observability()

    # ---------------------------------------------------------
    # 3. Construct Graph with Breakpoint (HITL)
    # ---------------------------------------------------------
    builder = StateGraph(PaymentState)
    builder.add_node("draft_transaction", draft_transaction_node)
    builder.add_node("execute_payment", execute_payment_node)

    builder.add_edge(START, "draft_transaction")
    builder.add_edge("draft_transaction", "execute_payment")
    builder.add_edge("execute_payment", END)

    # In LangGraph 2026, HITL requires a checkpointer to preserve state during pause
    checkpointer = MemorySaver()

    # Interrupt execution before the high-stakes payment node!
    app = builder.compile(
        checkpointer=checkpointer,
        interrupt_before=["execute_payment"]  # Human breakpoint!
    )

    # ---------------------------------------------------------
    # 4. Initiate Sensitive Action
    # ---------------------------------------------------------
    thread_config = {"configurable": {"thread_id": "tx-bank-99901"}}
    initial_payment = {
        "recipient": "Enterprise Cloud Hosting LLC",
        "amount": 5400.00,  # High amount triggers review
        "is_approved": False,
        "status": "INITIATED"
    }

    print("\n--- Step 1: Agent Runs Until Breakpoint ---")
    app.invoke(initial_payment, config=thread_config)

    # ---------------------------------------------------------
    # 5. Inspect Suspended State (Human Dashboard)
    # ---------------------------------------------------------
    state_snapshot = app.get_state(thread_config)
    print("\n--- Step 2: System Paused for Human Approval ---")
    print(f"Graph Status: Interrupted before node '{state_snapshot.next}'")
    print(f"Pending Transaction: Recipient='{state_snapshot.values['recipient']}', Amount=${state_snapshot.values['amount']}")
    print(f"Current State Status: {state_snapshot.values['status']}")

    # ---------------------------------------------------------
    # 6. Human Decision & Resume
    # ---------------------------------------------------------
    print("\n--- Step 3: Human Approves the Transaction ---")
    print("Simulated Human Operator: 'Transfer verified and approved.'")

    # The human updates the state to mark approved
    app.update_state(
        thread_config,
        {"is_approved": True, "status": "APPROVED_BY_ADMIN"}
    )

    # Resume graph by passing None as input!
    print("\n--- Step 4: Resuming Execution from Checkpoint ---")
    final_state = app.invoke(None, config=thread_config)

    print("\n--- Final Status ---")
    print(f"Final State: {final_state['status']}")
    print("\n[SUCCESS] Lesson 06 completed. You mastered LangSmith concepts and Human-in-the-Loop workflows!")


if __name__ == "__main__":
    main()
