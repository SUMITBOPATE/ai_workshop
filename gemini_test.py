import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.environ["GEMINI_API_KEY"]

client = genai.Client(api_key=api_key)

response = client.models.generate_content(
    model="gemini-3.5-flash",
    contents="Explain PostgreSQL in one simple sentence."
)

print(response.text)