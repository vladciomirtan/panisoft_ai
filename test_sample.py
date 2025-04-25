import os
import sys
from document_processor import extract_text_from_docx
from matcher import CVJobMatcher
from config import OPENROUTE_API_KEY

def test_sample():
    """Test the matcher with a single CV and job description."""
    
    # Check if API key is provided
    if not OPENROUTE_API_KEY:
        print("Error: OPENROUTE_API_KEY is not set.")
        print("Please set your API key in the config.py file or as an environment variable.")
        sys.exit(1)
    
    print("Testing CV-Job matching with a sample...")
    
    # Get paths to sample files
    cv_dir = "DataSet/cv"
    job_dir = "DataSet/job_descriptions"
    
    # Get first available CV and job description
    cv_files = [f for f in os.listdir(cv_dir) if f.endswith('.docx')]
    job_files = [f for f in os.listdir(job_dir) if f.endswith('.docx')]
    
    if not cv_files or not job_files:
        print("Error: No CV or job description files found.")
        sys.exit(1)
    
    sample_cv_path = os.path.join(cv_dir, cv_files[0])
    sample_job_path = os.path.join(job_dir, job_files[0])
    
    print(f"Using CV: {sample_cv_path}")
    print(f"Using Job: {sample_job_path}")
    
    # Extract text
    cv_content = extract_text_from_docx(sample_cv_path)
    job_content = extract_text_from_docx(sample_job_path)
    
    # Initialize matcher
    matcher = CVJobMatcher()
    
    # Match CV with job description
    print("\nMatching CV with job description...")
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