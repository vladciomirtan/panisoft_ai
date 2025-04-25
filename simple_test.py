import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()

# Get API key from environment variables
api_key = os.getenv("OPENROUTE_API_KEY")

print(f"API Key found: {'Yes' if api_key else 'No'}")

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key=api_key,
)

try:
    completion = client.chat.completions.create(
      extra_headers={
        "HTTP-Referer": "https://example.com", # For OpenRouter rankings
      },
      model="deepseek/deepseek-v3-base:free",  # Using the model from the example
      messages=[
        {
          "role": "user",
          "content": "Write a simple Python function to calculate factorial."
        }
      ]
    )
    
    print("\nAPI Response:")
    print(completion.choices[0].message.content)
    print("\nTest successful! Your API key is working correctly.")
    
except Exception as e:
    print(f"\nError: {e}")
    print("\nTest failed. There might be an issue with your API key or the API service.") 