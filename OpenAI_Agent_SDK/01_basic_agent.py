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
# 1. Disable OpenAI tracing because we don't have an OpenAI API key
set_tracing_disabled(True)

# 2. Create an OpenAI-compatible client pointing to Groq
client = AsyncOpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
)

# 3. Tell the Agents SDK which model to use
model = OpenAIChatCompletionsModel(
    model="openai/gpt-oss-120b",
    openai_client=client,
)

# 4. Create the agent
agent = Agent(
    name="Hello Agent",
    instructions="You are a helpful hotel booking assistant. Don't respond to anything that is out of topic.",
    model=model,
)

# 5. Run the agent
result = Runner.run_sync(
    agent,
    "How Can I book a hotel in Faisalabad? Which famous hotels are available in Faisalabad?"
)

# 6. Display the final answer
print(result.final_output)














# from agents import Agent, Runner

# agent = Agent(
#     name="Hello Agent",
#     instructions="You answer history questions clearly and concisely.",
    
# )
# result = Runner.run_sync(agent, "Hello! Introduce yourself to my Agentic AI class.")
# print(result.final_output)

