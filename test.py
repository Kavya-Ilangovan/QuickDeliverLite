import openai
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Get the API key from the environment
api_key = os.getenv("OPENAI_API_KEY")
print("Loaded API Key:", api_key)

# Set the API key
openai.api_key = api_key

# Try listing models to test the connection
try:
    response = openai.models.list()
    print("✅ OpenAI API connection successful. Available models:")
    for model in response.data:
        print("-", model.id)
except Exception as e:
    print("❌ OpenAI API connection failed:")
    print(e)
