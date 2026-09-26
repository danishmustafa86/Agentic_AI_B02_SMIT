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


# -------------------------------------------------------------
# 1. LangSmith Configuration Overview
# -------------------------------------------------------------
def configure_langsmith_observability():
    """Configures LangSmith environment if keys are set."""
    if os.getenv("LANGCHAIN_TRACING_V2") == "true" and os.getenv("LANGCHAIN_API_KEY"):
        os.environ.setdefault("LANGCHAIN_PROJECT", "default")


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
    auto_allowed = verify_compliance_rules(state["amount"], state["recipient"])
    if auto_allowed:
        return {"is_approved": True, "status": "AUTO_APPROVED"}
    else:
        return {"is_approved": False, "status": "PENDING_HUMAN_APPROVAL"}


def execute_payment_node(state: PaymentState) -> dict:
    """Node 2 (High Stakes): Executes the actual wire transfer."""
    if state.get("is_approved", False):
        print(f"\nPayment Executed: Wire transferred ${state['amount']:,.2f} to '{state['recipient']}'.")
        return {"status": "FUNDS_DISPATCHED_SUCCESSFULLY"}
    else:
        print(f"\nPayment Rejected: Wire transfer cancelled.")
        return {"status": "TRANSACTION_REJECTED"}


def main():
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

    checkpointer = MemorySaver()
    app = builder.compile(
        checkpointer=checkpointer,
        interrupt_before=["execute_payment"]  # Breakpoint before sensitive execution
    )

    # ---------------------------------------------------------
    # 4. Initiate Transaction & Draft Payment
    # ---------------------------------------------------------
    thread_config = {"configurable": {"thread_id": "tx-bank-99901"}}
    initial_payment = {
        "recipient": "Enterprise Cloud Hosting LLC",
        "amount": 5400.00,
        "is_approved": False,
        "status": "INITIATED"
    }

    # Runs until the breakpoint right after drafting
    app.invoke(initial_payment, config=thread_config)

    # ---------------------------------------------------------
    # 5. Show Draft in Terminal for Human-in-the-Loop Review
    # ---------------------------------------------------------
    state_snapshot = app.get_state(thread_config)
    draft = state_snapshot.values

    print("=== Payment Draft ===")
    print(f"Recipient: {draft['recipient']}")
    print(f"Amount   : ${draft['amount']:,.2f}")
    print(f"Status   : {draft['status']}")
    print("=====================")

    # ---------------------------------------------------------
    # 6. Interactive Terminal Prompt: Approve or Reject
    # ---------------------------------------------------------
    while True:
        decision = input("\nApprove and execute payment? (yes/no): ").strip().lower()
        if decision in ["yes", "y"]:
            app.update_state(
                thread_config,
                {"is_approved": True, "status": "APPROVED_BY_USER"}
            )
            break
        elif decision in ["no", "n"]:
            app.update_state(
                thread_config,
                {"is_approved": False, "status": "REJECTED_BY_USER"}
            )
            break
        print("Invalid input. Please enter 'yes' or 'no'.")

    # Resume graph to call execute_payment_node
    app.invoke(None, config=thread_config)


if __name__ == "__main__":
    main()
