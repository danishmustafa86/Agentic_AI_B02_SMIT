import os
import asyncio
from dotenv import load_dotenv
from openai.types.responses import ResponseTextDeltaEvent
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


# 1. A simple storyteller agent.
agent = Agent(
    name="Storyteller",
    instructions="You write short, fun bedtime stories for children (about 8-10 sentences).",
    model=model,
)


# 2. Streaming needs async, so we wrap the code in an async function.
async def main():
    # 3. Use Runner.run_streamed instead of Runner.run_sync.
    #    This gives us a live stream of the agent's output as it thinks.
    result = Runner.run_streamed(agent, "Tell me a story about a brave little cat.")

    print("Story:\n")

    # 4. Loop through each streamed event.
    #    We only care about text pieces (deltas) from the model.
    async for event in result.stream_events():
        if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
            # Print each new chunk of text WITHOUT a newline,
            # so it looks like the story is being typed live.
            print(event.data.delta, end="", flush=True)

    print("\n\n--- Story complete ---")


# 5. Run the async main function.
asyncio.run(main())
