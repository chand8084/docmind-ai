
import os
from dotenv import load_dotenv
from google import genai

load_dotenv(override=True)

api_key = os.getenv("GEMINI_API_KEY")
model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

if not api_key:
    raise ValueError("API key not found in .env")

print("Connecting to Gemini...")
print("Model:", model)
print("API key loaded:", bool(api_key))

client = genai.Client(api_key=api_key)

try:
    response = client.models.generate_content(
        model=model,
        contents="Reply with exactly: Gemini connection successful."
    )

    print("\nSUCCESS!")
    print(response.text)

except Exception as error:
    print("\nREQUEST FAILED:")
    print(repr(error))

print("\nTest finished.")
