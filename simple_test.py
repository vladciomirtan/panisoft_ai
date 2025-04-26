import os
from dotenv import load_dotenv
import requests
import json

# Load environment variables from .env file
load_dotenv()

# Get API key from environment variables
api_key = os.getenv("GEMINI_API_KEY")

def test_gemini_api():
    """Test if the Gemini API key is working properly."""
    
    print(f"Gemini API Key found: {'Yes' if api_key else 'No'}")
    
    if not api_key:
        print("Error: No API key found in environment variables.")
        print("Please set your Gemini API key in the .env file.")
        return
    
    try:
        # Call the Gemini API with a simple prompt
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
        
        headers = {
            'Content-Type': 'application/json'
        }
        
        data = {
            "contents": [{
                "parts": [{"text": "Write a simple Python function to calculate factorial."}]
            }],
            "generationConfig": {
                "temperature": 0.3,
                "maxOutputTokens": 1024
            }
        }
        
        print("\nTesting Gemini API connection...")
        response = requests.post(url, headers=headers, data=json.dumps(data))
        
        if response.status_code != 200:
            print(f"Error connecting to Gemini API: {response.status_code} - {response.text}")
            return
        
        response_json = response.json()
        
        # Extract the text from the response
        text = response_json["candidates"][0]["content"]["parts"][0]["text"]
        
        print("\nAPI Response:")
        print(text)
        print("\nTest successful! Your Gemini API key is working correctly.")
        
    except Exception as e:
        print(f"\nError: {e}")
        print("\nTest failed. There might be an issue with your API key or the Gemini API service.")

if __name__ == "__main__":
    test_gemini_api() 