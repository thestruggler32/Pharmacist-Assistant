import os
import base64
from dotenv import load_dotenv
from mistralai import Mistral

load_dotenv()

def test_pixtral():
    api_key = os.getenv("MISTRAL_API_KEY")
    client = Mistral(api_key=api_key)
    
    # 1x1 transparent pixel
    tiny_img = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="
    
    print("Testing pixtral with tiny image...")
    try:
        chat_response = client.chat.complete(
            model="pixtral-12b-2409",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "What is this?"},
                        {"type": "image_url", "image_url": f"data:image/png;base64,{tiny_img}"}
                    ]
                }
            ]
        )
        print("Success! Response:", chat_response.choices[0].message.content)
    except Exception as e:
        print("Failed:", e)

if __name__ == "__main__":
    test_pixtral()
