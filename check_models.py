import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("No API Key found")
else:
    client = genai.Client(api_key=api_key)
    print("Available models:")
    try:
        for model in client.models.list():
            if "gemini" in model.name:
                print(f"- {model.name}")
    except Exception as e:
        print(e)