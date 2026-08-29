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


# 1. Two specialist agents — same idea as in the handoffs example.
urdu_translator = Agent(
    name="Urdu Translator",
    instructions="You translate the given English text into fluent Urdu. Only output the translation.",
    model=model,
)

french_translator = Agent(
    name="French Translator",
    instructions="You translate the given English text into fluent French. Only output the translation.",
    model=model,
)


# 2. This time the manager agent does NOT hand off.
#    It stays in control and uses the specialists as TOOLS.
#    Difference from handoffs:
#      - handoff  = "you take over completely"
#      - as_tool  = "do this small piece and give me the result back"
manager = Agent(
    name="Translation Manager",
    instructions=(
        "You are a translation manager. "
        "The user will give you an English sentence. "
        "Use the translate_to_urdu tool AND the translate_to_french tool, "
        "then combine both translations in a clear final answer like:\n"
        "Urdu: ...\nFrench: ..."
    ),
    model=model,
    tools=[
        urdu_translator.as_tool(
            tool_name="translate_to_urdu",
            tool_description="Translate an English sentence into Urdu.",
        ),
        french_translator.as_tool(
            tool_name="translate_to_french",
            tool_description="Translate an English sentence into French.",
        ),
    ],
)


# 3. Run the manager. It will call BOTH tools on its own and merge the results.
user_sentence = input("Enter an English sentence to translate: ")
result = Runner.run_sync(manager, user_sentence)

print("\n" + result.final_output)
