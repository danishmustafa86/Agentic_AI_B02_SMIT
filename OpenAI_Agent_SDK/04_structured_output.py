import os
from dotenv import load_dotenv
from pydantic import BaseModel
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
    model="openai/gpt-oss-20b",
    openai_client=client,
)


# 1. Define the exact shape you want the agent to return.
#    Pydantic BaseModel = a "schema" or "blueprint" for the answer.
class StudentProfile(BaseModel):
    name: str
    age: int
    city: str
    favorite_subject: str
class StudentProfile(BaseModel):
    name: str
    age: int
    city: str
    favorite_subject: str



# 2. Give the model to the agent via `output_type=...`.
#    Now the agent MUST return data that fits StudentProfile
#    instead of just plain text.
agent = Agent(
    name="Profile Extractor",
    instructions=(
        "You extract student information from the user's message "
        "and return it in the required structured format."
    ),
    model=model,
    output_type=StudentProfile,
)

# 3. Run it with a natural-language sentence.
user_message ="Hi, my name is Ali, I am 20 years old, I live in Lahore, and my favorite subject is Mathematics."

result = Runner.run_sync(agent, user_message)

# 4. result.final_output is now a StudentProfile object,
#    not a string. You can access fields like a normal Python object.
profile: StudentProfile = result.final_output

print("Name           :", profile.name)
print("Age            :", profile.age)
print("City           :", profile.city)
print("Favorite Subject:", profile.favorite_subject)

# 5. You can also convert it to a dictionary or JSON easily.
# print("\nAs dictionary:", profile.model_dump())
# print("As JSON      :", profile.model_dump_json())
