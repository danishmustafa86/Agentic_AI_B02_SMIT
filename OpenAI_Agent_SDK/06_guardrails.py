import os
from dotenv import load_dotenv
from pydantic import BaseModel
from agents import (
    Agent,
    Runner,
    AsyncOpenAI,
    OpenAIChatCompletionsModel,
    set_tracing_disabled,
    input_guardrail,
    GuardrailFunctionOutput,
    InputGuardrailTripwireTriggered,
    RunContextWrapper,
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


# 1. A small helper agent whose ONLY job is to classify the user's question.
#    It returns a structured Yes/No decision.
class TopicCheck(BaseModel):
    is_about_math: bool
    reason: str


topic_checker = Agent(
    name="Topic Checker",
    instructions=(
        "Decide if the user's question is about mathematics "
        "(numbers, calculations, algebra, geometry, etc.). "
        "Return is_about_math=True only if it is clearly math."
    ),
    model=model,
    output_type=TopicCheck,
)


# 2. The guardrail function. It runs BEFORE the main agent.
#    If tripwire_triggered = True, the main agent is BLOCKED from running.
@input_guardrail
async def math_only_guardrail(
    ctx: RunContextWrapper,
    agent: Agent,
    user_input: str,
) -> GuardrailFunctionOutput:
    # Ask the small checker agent to look at the question first.
    check_result = await Runner.run(topic_checker, user_input, context=ctx.context)
    decision: TopicCheck = check_result.final_output

    return GuardrailFunctionOutput(
        output_info=decision,
        # Block the main agent if the question is NOT about math.
        tripwire_triggered=not decision.is_about_math,
    )


# 3. The main agent — a math tutor — with our guardrail attached.
math_tutor = Agent(
    name="Math Tutor",
    instructions="You are a helpful math tutor. Explain answers step by step.",
    model=model,
    input_guardrails=[math_only_guardrail],
)


# 4. Try running with different questions.
user_query = input("Ask a math question: ")

try:
    result = Runner.run_sync(math_tutor, user_query)
    print("\nTutor:", result.final_output)
except InputGuardrailTripwireTriggered:
    print("\nBlocked: I can only answer math-related questions. Please try again.")
