import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("AGENTROUTER_API_KEY")
base_url = "https://agentrouter.org/v1"

print(f"DEBUG: Testing AgentRouter Connection")
print(f"DEBUG: API Key: {api_key[:10]}...{api_key[-5:] if api_key else 'None'}")
print(f"DEBUG: Base URL: {base_url}")

client = OpenAI(
    api_key=api_key,
    base_url=base_url
)

try:
    print("DEBUG: Sending request...")
    response = client.chat.completions.create(
        model="anthropic/claude-sonnet-4-5-20250929",
        messages=[
            {"role": "user", "content": "Hello, are you working?"}
        ],
        max_tokens=10
    )
    print("SUCCESS!")
    print(response)
except Exception as e:
    print("FAILURE!")
    print(f"Error: {e}")
