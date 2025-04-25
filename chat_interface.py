import os
import sys
from openai import OpenAI

from config import OPENROUTE_API_KEY, MODEL_NAME, TEMPERATURE, MAX_TOKENS
from prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE
from document_processor import extract_text_from_docx

def chat_interface():
    """Simple command-line chat interface for the CV-Job matching AI."""
    
    # Check if API key is provided
    if not OPENROUTE_API_KEY:
        print("Error: OPENROUTE_API_KEY is not set.")
        print("Please set your API key in the config.py file or as an environment variable.")
        sys.exit(1)
    
    # Initialize the client
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTE_API_KEY
    )
    
    # Display welcome message
    print("\n" + "=" * 80)
    print("CV-Job Matching AI Chat Interface")
    print("=" * 80)
    print("\nOptions:")
    print("1. Match a specific CV to a job description")
    print("2. Exit")
    
    while True:
        choice = input("\nEnter your choice (1-2): ")
        
        if choice == "2":
            print("Exiting. Goodbye!")
            break
        
        elif choice == "1":
            # Get CV and job description files
            cv_path = input("\nEnter the path to the CV file (.docx): ")
            job_desc_path = input("Enter the path to the job description file (.docx): ")
            
            # Validate files
            if not os.path.exists(cv_path) or not cv_path.endswith('.docx'):
                print(f"Error: CV file '{cv_path}' does not exist or is not a .docx file.")
                continue
                
            if not os.path.exists(job_desc_path) or not job_desc_path.endswith('.docx'):
                print(f"Error: Job description file '{job_desc_path}' does not exist or is not a .docx file.")
                continue
            
            try:
                # Extract text from the files
                print("\nExtracting text from files...")
                cv_content = extract_text_from_docx(cv_path)
                job_description = extract_text_from_docx(job_desc_path)
                
                # Format user content
                user_content = f"""
                ## CV:
                {cv_content}
                
                ## Job Description:
                {job_description}
                
                Analyze the match between this CV and job description according to the criteria.
                """
                
                # Get the response
                print("\nAnalyzing the match... (this may take a moment)")
                response = client.chat.completions.create(
                    extra_headers={
                        "HTTP-Referer": "https://example.com", # Required by OpenRouter
                    },
                    model=MODEL_NAME,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_content}
                    ],
                    temperature=TEMPERATURE,
                    max_tokens=MAX_TOKENS
                )
                
                # Display the response
                print("\n" + "=" * 80)
                print("MATCH ANALYSIS")
                print("=" * 80 + "\n")
                print(response.choices[0].message.content)
                print("\n" + "=" * 80)
                
            except Exception as e:
                print(f"Error: {e}")
        
        else:
            print("Invalid choice. Please enter 1 or 2.")

if __name__ == "__main__":
    chat_interface() 