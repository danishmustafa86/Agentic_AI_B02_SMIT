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

# Same Groq setup as hello.py
client = AsyncOpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
)
model = OpenAIChatCompletionsModel(
    model="openai/gpt-oss-120b",
    openai_client=client,
)


# 1. Two specialist agents — each one only knows how to do its own job
urdu_agent = Agent(
    name="Urdu Agent",
    instructions="You only reply in Urdu.",
    model=model,
)

english_agent = Agent(
    name="English Agent",
    instructions="You only reply in English.",
    model=model,
)

# 2. A router agent that picks the right specialist via handoffs.
#    The 'handoffs' list is the set of agents this one can delegate to.
router = Agent(
    name="Router",
    instructions=(
        "Detect the language of the user. "
        "Hand off to Urdu Agent for Urdu, English Agent for English."
    ),
    model=model,
    handoffs=[urdu_agent, english_agent],
)

# 3. Run the router. It will hand off automatically to the right specialist.
result = Runner.run_sync(router, "Assalam-o-Alaikum, aap kaise hain?")

# 4. The final answer comes from whichever agent finished the job.
print(result.final_output)
