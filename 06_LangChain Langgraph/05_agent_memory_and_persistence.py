"""
05_agent_memory_and_persistence.py
===================================
Topic: Agent Memory, Persistence, and State Checkpointing

Key Concepts for 2026:
1. Checkpointers: Saving state snapshots at every step using `MemorySaver`.
2. Threads: Unique conversation sessions (`thread_id`) allowing multi-turn memory.
3. State Inspection: Accessing the snapshot history with `app.get_state()`.
4. State Modification: Injecting or overriding state with `app.update_state()`.
"""

from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage, AIMessage
from utils import get_chat_model, print_section


def conversational_agent_node(state: MessagesState) -> dict:
    """Agent node that answers queries while having full access to conversation memory."""
    model = get_chat_model()
    # Model receives full accumulated message history for this thread
    response = model.invoke(state["messages"])
    return {"messages": [response]}


def main():
    print_section("05: Agent Memory & State Persistence with Checkpointers")

    # 1. Initialize an In-Memory Checkpointer
    # In production (2026), you might use PostgresSaver or MongoDBSaver
    checkpointer = MemorySaver()

    # 2. Build the graph with MessagesState
    builder = StateGraph(MessagesState)
    builder.add_node("agent", conversational_agent_node)
    builder.add_edge(START, "agent")
    builder.add_edge("agent", END)

    # Compile the graph WITH the checkpointer enabled
    app = builder.compile(checkpointer=checkpointer)

    # ---------------------------------------------------------
    # Multi-Turn Conversation using Thread ID
    # ---------------------------------------------------------
    # Thread 1: User "Alex"
    config_thread_1 = {"configurable": {"thread_id": "session-user-alex-101"}}

    print("\n--- Turn 1: Storing Information in Memory ---")
    turn1_input = {"messages": [HumanMessage(content="Hi! My name is Alex, and I am building an AI agent in 2026.")]}
    response1 = app.invoke(turn1_input, config=config_thread_1)
    print(f"User: {turn1_input['messages'][0].content}")
    print(f"Agent: {response1['messages'][-1].content}")

    print("\n--- Turn 2: Querying Memory (Separate Invoke Call) ---")
    # Notice we ONLY send the new question, not the previous messages!
    turn2_input = {"messages": [HumanMessage(content="Do you remember what my name is and what I am building?")]}
    response2 = app.invoke(turn2_input, config=config_thread_1)
    print(f"User: {turn2_input['messages'][0].content}")
    print(f"Agent: {response2['messages'][-1].content}")

    # ---------------------------------------------------------
    # Thread Isolation Demonstration
    # ---------------------------------------------------------
    print("\n--- Thread Isolation Test (Thread 2: User Sarah) ---")
    config_thread_2 = {"configurable": {"thread_id": "session-user-sarah-202"}}
    sarah_input = {"messages": [HumanMessage(content="What is my name?")]}
    response_sarah = app.invoke(sarah_input, config=config_thread_2)
    print(f"User (Sarah): {sarah_input['messages'][0].content}")
    print(f"Agent response to Sarah: {response_sarah['messages'][-1].content}")

    # ---------------------------------------------------------
    # State Inspection & Time Travel
    # ---------------------------------------------------------
    print("\n--- State Inspection (app.get_state) ---")
    current_state = app.get_state(config_thread_1)
    print(f"Thread 1 Message Count in Checkpoint: {len(current_state.values['messages'])}")
    print(f"Next Node to execute: {current_state.next} (empty tuple means execution finished)")

    print("\n--- State Modification (app.update_state) ---")
    # In 2026, engineers can inject human feedback or corrections directly into checkpoint state:
    app.update_state(
        config_thread_1,
        {"messages": [AIMessage(content="System Note: Alex has admin-level clearance.")]}
    )
    updated_state = app.get_state(config_thread_1)
    print(f"Updated Message Count after injection: {len(updated_state.values['messages'])}")
    print(f"Latest injected message: {updated_state.values['messages'][-1].content}")

    print("\n[SUCCESS] Lesson 05 completed. You mastered session memory and state checkpointers!")


if __name__ == "__main__":
    main()
