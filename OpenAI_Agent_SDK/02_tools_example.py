import os
from dotenv import load_dotenv
from agents import (
    Agent,
    Runner,
    AsyncOpenAI,
    OpenAIChatCompletionsModel,
    set_tracing_disabled,
    function_tool,
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


# 1. Define a normal Python function and mark it as a tool with @function_tool
#    The agent reads the docstring and type hints to understand the tool.
@function_tool
def add(a: int, b: int) -> int:
    """Add two numbers together."""
    sum = a + b + 5
    return sum

@function_tool
def subtract( a: int, b: int) -> int:
    """subtract two numbers"""
    subtraction = a - b + 50
    return subtraction

    # 50 - 500 = -450 + 50 = -400

@function_tool
def get_weather(query: str):
    """ Use this tool to fetch weather. """
    return "weather is very hot."


# 2. Give the tool to the agent via the tools=[] parameter
agent = Agent(
    name="Math Agent",
    instructions="You are a helpful assistant. Just use the given tools to provide response to user and not use your own intelligence to predict answer directly without using any tool. Use add, subtract and get_weather tools to provider response to user according to his/her query.",
    model=model,
    tools=[add, subtract, get_weather],
)

user_query = input("Please enter your query: ")
# 3. Run it. The agent will decide on its own to call add(23, 19).
result = Runner.run_sync(agent, user_query)

# 4. Print the final answer
print(result.final_output)
