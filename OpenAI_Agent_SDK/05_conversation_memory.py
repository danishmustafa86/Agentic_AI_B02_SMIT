import os
from dotenv import load_dotenv
from agents import (
    Agent,
    Runner,
    AsyncOpenAI,
    OpenAIChatCompletionsModel,
    set_tracing_disabled,
)

load_dotenv()

# Disable OpenAI tracing (we're using Groq, not OpenAI)
set_tracing_disabled(True)

# Same Groq setup as before
client = AsyncOpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
)
model = OpenAIChatCompletionsModel(
    model="openai/gpt-oss-120b",
    openai_client=client,
)


# 1. Create a friendly chat agent.
agent = Agent(
    name="Chat Buddy",
    instructions="You are a friendly assistant. Remember what the user tells you in this conversation.",
    model=model,
)

# 2. `conversation` is our memory. It starts empty.
#    Every time the user talks, we append their message.
#    Every time the agent replies, we append the whole updated history.
conversation: list = []

print("Chat with the agent! Type 'exit' to quit.\n")

while True:
    user_input = input("You: ")
    if user_input.strip().lower() == "exit":
        print("Goodbye!")
        break

    # 3. Add the user's new message to the history.
    conversation.append({"role": "user", "content": user_input})

    # 4. Send the FULL history each time — this is how the agent "remembers".
    result = Runner.run_sync(agent, conversation)

    # 5. Replace our conversation with the updated history from the result.
    #    to_input_list() returns everything: past messages + the new reply.
    conversation = result.to_input_list()

    print("Agent:", result.final_output, "\n")


# Try this:
#   You: My name is Sara and I love cricket.
#   You: What is my name?
#   You: Which sport do I like?
# The agent will remember because we keep sending the whole history.
