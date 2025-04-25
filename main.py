import os
import sys
from document_processor import load_cvs, load_job_descriptions
from matcher import CVJobMatcher, format_top_matches
from config import OPENROUTE_API_KEY

def main():
    # Check if API key is provided
    if not OPENROUTE_API_KEY:
        print("Error: OPENROUTE_API_KEY is not set.")
        print("Please set your API key in the config.py file or as an environment variable.")
        sys.exit(1)
        
    print("Loading CVs and job descriptions...")
    cvs = load_cvs()
    job_descriptions = load_job_descriptions()
    
    print(f"Loaded {len(cvs)} CVs and {len(job_descriptions)} job descriptions.")
    
    # Initialize the matcher
    matcher = CVJobMatcher()
    
    # Match all CVs with all job descriptions
    print("Starting the matching process...")
    matches = matcher.match_all(cvs, job_descriptions)
    
    # Format and display the results
    results = format_top_matches(matches, top_n=5)
    
    # Save results to file
    with open("matching_results.txt", "w", encoding="utf-8") as f:
        f.write(results)
        
    print("Matching completed. Results saved to 'matching_results.txt'.")
    
    # Display some sample results
    print("\nSample results:")
    sample_job_ids = list(matches.keys())[:3]  # Show results for first 3 jobs
    
    for job_id in sample_job_ids:
        job_matches = matches[job_id]
        print(f"\nJob: {job_id}")
        print("Top 3 matches:")
        
        for i, (cv_id, result) in enumerate(job_matches[:3]):
            print(f"{i+1}. {cv_id} - Score: {result.total_score:.2f}")
            print(f"   Industry: {result.industry_knowledge_score:.2f} | Technical: {result.technical_skills_score:.2f} | Match: {result.job_description_match_score:.2f}")

if __name__ == "__main__":
    main() 