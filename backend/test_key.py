import os
import sys
from dotenv import load_dotenv
from mistralai import Mistral

load_dotenv()

def test_connectivity():
    api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key:
        print("No API Key found")
        return

    client = Mistral(api_key=api_key)
    
    print("Testing mistral-tiny connectivity...")
    try:
        chat_response = client.chat.complete(
            model="mistral-tiny",
            messages=[{"role": "user", "content": "Hello"}]
        )
        print("Success! Response:", chat_response.choices[0].message.content)
    except Exception as e:
        print("Failed:", e)

if __name__ == "__main__":
    test_connectivity()
