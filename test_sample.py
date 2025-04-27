import os
import sys
import random
from document_processor import extract_text
from matcher import CVJobMatcher
from config import GEMINI_API_KEY

def test_sample(cv_index=None, job_index=None):
    """Test the matcher with a single CV and job description."""
    
    # Check if API key is provided
    if not GEMINI_API_KEY:
        print("Error: GEMINI_API_KEY is not set.")
        print("Please set your API key in the config.py file or as an environment variable.")
        sys.exit(1)
    
    print("Testing CV-Job matching with Gemini API...")
    
    # Get paths to sample files
    cv_dir = "DataSet/cv"
    job_dir = "DataSet/job_descriptions"
    
    # Get all CV and job description files
    cv_files = sorted([f for f in os.listdir(cv_dir) if f.endswith('.docx')], 
                     key=lambda x: int(x.split('_')[1]))  # Sort CVs numerically by number after cv_
    job_files = sorted([f for f in os.listdir(job_dir) if f.endswith('.docx')], 
                      key=lambda x: int(x.split('_')[2]))  # Sort jobs numerically by number after job_description_
    
    if not cv_files or not job_files:
        print("Error: No CV or job description files found.")
        sys.exit(1)
    
    # select files based on provided indices or randomly
    cv_index = cv_index if cv_index is not None else random.randint(0, len(cv_files) - 1)
    job_index = job_index if job_index is not None else random.randint(0, len(job_files) - 1)
    
    sample_cv_path = os.path.join(cv_dir, cv_files[cv_index])
    sample_job_path = os.path.join(job_dir, job_files[job_index])
    
    print(f"Using CV: {sample_cv_path}")
    print(f"Using Job: {sample_job_path}")
    
    # Extract text
    cv_content = extract_text(sample_cv_path)
    job_content = extract_text(sample_job_path)
    
    # Initialize matcher
    matcher = CVJobMatcher()
    
    # Match CV with job description
    print("\nMatching CV with job description using Gemini API...")
    result = matcher.match(cv_content, job_content)
    
    # Display results
    print("\nMatch Results:")
    print(f"Industry Knowledge Score: {result.industry_knowledge_score:.2f}")
    print(f"Technical Skills Score: {result.technical_skills_score:.2f}")
    print(f"Job Description Match Score: {result.job_description_match_score:.2f}")
    print(f"Total Score: {result.total_score:.2f}")
    print("\nReasoning:")
    print(result.reasoning)
    
    # Test successful
    print("\nTest completed successfully.")

if __name__ == "__main__":
    test_sample()