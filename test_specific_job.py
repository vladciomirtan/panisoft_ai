import os
import sys
import random
from document_processor import extract_text_from_docx
from matcher import CVJobMatcher, MatchResult
from config import OPENROUTE_API_KEY

def test_specific_job():
    """Test 5 random CVs against a specific job description."""
    
    # Check if API key is provided
    if not OPENROUTE_API_KEY:
        print("Error: OPENROUTE_API_KEY is not set.")
        print("Please set your API key in the config.py file or as an environment variable.")
        sys.exit(1)
    
    print("=" * 80)
    print("Testing 5 Random CVs Against a Specific Job Description")
    print("=" * 80)
    
    # Get paths to sample files
    cv_dir = "DataSet/cv"
    job_dir = "DataSet/job_descriptions"
    
    # List all CV files and job description files
    cv_files = [f for f in os.listdir(cv_dir) if f.endswith('.docx')]
    job_files = [f for f in os.listdir(job_dir) if f.endswith('.docx')]
    
    if not cv_files or not job_files:
        print("Error: No CV or job description files found.")
        sys.exit(1)
    
    # Let user select a specific job description
    print("\nAvailable job descriptions:")
    for i, job_file in enumerate(job_files[:10]): # Show first 10 jobs
        job_name = job_file.replace('.docx', '').replace('job_description_', '')
        print(f"{i+1}. {job_name}")
    
    job_choice = int(input("\nEnter the number of the job description to use: "))
    if job_choice < 1 or job_choice > len(job_files[:10]):
        print("Invalid choice. Using the first job description.")
        job_choice = 1
    
    selected_job_file = job_files[job_choice-1]
    job_path = os.path.join(job_dir, selected_job_file)
    print(f"\nSelected job: {selected_job_file}")
    
    # Select 5 random CVs
    selected_cv_files = random.sample(cv_files, 5)
    print("\nSelected 5 random CVs:")
    for i, cv_file in enumerate(selected_cv_files):
        print(f"{i+1}. {cv_file}")
    
    # Extract job description
    job_content = extract_text_from_docx(job_path)
    
    # Initialize matcher
    matcher = CVJobMatcher()
    
    # Match each CV with the job description
    results = []
    
    print("\nMatching CVs with job description...")
    print("=" * 80)
    
    for cv_file in selected_cv_files:
        cv_path = os.path.join(cv_dir, cv_file)
        cv_content = extract_text_from_docx(cv_path)
        
        print(f"Processing: {cv_file}...")
        result = matcher.match(cv_content, job_content)
        results.append((cv_file, result))
    
    # Sort results by total score (descending)
    results.sort(key=lambda x: x[1].total_score, reverse=True)
    
    # Display results
    print("\n" + "=" * 80)
    print(f"Results for job: {selected_job_file}")
    print("=" * 80)
    
    for i, (cv_file, result) in enumerate(results):
        print(f"\n{i+1}. {cv_file}")
        print(f"   Total Score: {result.total_score:.2f}")
        print(f"   Industry: {result.industry_knowledge_score:.2f} | Technical: {result.technical_skills_score:.2f} | Match: {result.job_description_match_score:.2f}")
        print(f"   Reasoning: {result.reasoning[:200]}...")
    
    # Print the best match
    best_cv, best_result = results[0]
    print("\n" + "=" * 80)
    print(f"Best match: {best_cv}")
    print(f"Score: {best_result.total_score:.2f}")
    print("=" * 80)
    
    print("\nTest completed successfully.")

if __name__ == "__main__":
    test_specific_job() 