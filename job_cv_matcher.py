import os
import sys
import heapq
from document_processor import extract_text_from_docx, load_job_descriptions, load_cvs
from matcher import CVJobMatcher
from config import GEMINI_API_KEY

def batch_match_job_to_cvs(job_id, num_cvs=20, top_matches=5, max_retries=3):
    """
    Compare a specific job description with multiple CVs and return the top matches.
    
    Args:
        job_id (str): ID of the job description to match against
        num_cvs (int): Number of CVs to process (default: 20)
        top_matches (int): Number of top matches to return (default: 5)
        max_retries (int): Maximum number of retries for API calls
    
    Returns:
        list: Top matches sorted by score (highest first)
    """
    # Check if Gemini API key is provided
    if not GEMINI_API_KEY:
        print("Error: GEMINI_API_KEY is not set.")
        print("Please set your API key in the config.py file or as an environment variable.")
        sys.exit(1)
    
    print(f"Using Gemini API")
    
    # Get paths to directories
    cv_dir = "DataSet/cv"
    job_dir = "DataSet/job_descriptions"
    
    # Load job descriptions and find the specific job
    job_descriptions = load_job_descriptions()
    if job_id not in job_descriptions:
        # Find job file manually if it's not in the dictionary
        job_files = [f for f in os.listdir(job_dir) if f.endswith('.docx')]
        matching_jobs = [f for f in job_files if f.split('_')[2] == job_id]
        
        if not matching_jobs:
            print(f"No job found with ID {job_id}.")
            return []
        
        job_file = matching_jobs[0]
        job_path = os.path.join(job_dir, job_file)
        job_content = extract_text_from_docx(job_path)
        job_title = '_'.join(job_file.split('_')[3:]).replace('.docx', '')
    else:
        job_content = job_descriptions[job_id]
        # Find the job file to get the title
        job_files = [f for f in os.listdir(job_dir) if f.endswith('.docx') and f.split('_')[2] == job_id]
        job_title = '_'.join(job_files[0].split('_')[3:]).replace('.docx', '') if job_files else f"Job {job_id}"
    
    # Load CVs
    cv_files = [f for f in os.listdir(cv_dir) if f.endswith('.docx')]
    cv_files.sort()
    
    # Limit to the specified number of CVs
    cv_files = cv_files[:num_cvs]
    
    # Initialize matcher
    matcher = CVJobMatcher()
    
    # Store results
    all_results = []
    
    print(f"Matching Job ID {job_id} ({job_title}) with {len(cv_files)} CVs...")
    
    # Process each CV
    for i, cv_file in enumerate(cv_files):
        retry_count = 0
        success = False
        
        while retry_count < max_retries and not success:
            try:
                # Extract CV info
                cv_id = cv_file.split('_')[1]
                cv_name = '_'.join(cv_file.split('_')[2:]).replace('.docx', '')
                
                # Display progress
                print(f"Processing {i+1}/{len(cv_files)}: CV {cv_id} - {cv_name}")
                
                # Get CV content
                cv_path = os.path.join(cv_dir, cv_file)
                cv_content = extract_text_from_docx(cv_path)
                
                # Match CV with job description
                result = matcher.match(cv_content, job_content)
                
                # Store result with CV info
                all_results.append({
                    'cv_id': cv_id,
                    'cv_name': cv_name,
                    'total_score': result.total_score,
                    'industry_knowledge_score': result.industry_knowledge_score,
                    'technical_skills_score': result.technical_skills_score,
                    'job_description_match_score': result.job_description_match_score,
                    'reasoning': result.reasoning
                })
                
                success = True
                
            except Exception as e:
                retry_count += 1
                print(f"Error processing CV {cv_file}: {e}")
                
                if retry_count < max_retries:
                    print(f"Retrying... (Attempt {retry_count+1}/{max_retries})")
                else:
                    print(f"Failed to process CV {cv_file} after {max_retries} attempts. Skipping.")
                    # Add a placeholder result to ensure we have data for reporting
                    all_results.append({
                        'cv_id': cv_file.split('_')[1],
                        'cv_name': '_'.join(cv_file.split('_')[2:]).replace('.docx', ''),
                        'total_score': 0.0,
                        'industry_knowledge_score': 0.0,
                        'technical_skills_score': 0.0,
                        'job_description_match_score': 0.0,
                        'reasoning': f"Error processing: {str(e)}"
                    })
    
    # Sort results by total score (highest first)
    all_results.sort(key=lambda x: x['total_score'], reverse=True)
    
    # Return top matches
    return all_results[:top_matches]

def display_results(top_matches, job_id, job_title):
    """Display the results in a formatted way."""
    print("\n" + "=" * 80)
    print(f"TOP 5 MATCHES FOR JOB: {job_id} - {job_title}")
    print("=" * 80)
    
    for i, match in enumerate(top_matches):
        print(f"\n{i+1}. CV ID: {match['cv_id']} - {match['cv_name']}")
        print(f"   Total Score: {match['total_score']:.2f} ({match['total_score']*100:.0f}%)")
        print(f"   Industry Knowledge: {match['industry_knowledge_score']:.2f} ({match['industry_knowledge_score']*100:.0f}%)")
        print(f"   Technical Skills: {match['technical_skills_score']:.2f} ({match['technical_skills_score']*100:.0f}%)")
        print(f"   Job Description Match: {match['job_description_match_score']:.2f} ({match['job_description_match_score']*100:.0f}%)")
        
        # Add rating stars
        print(f"   Rating: ", end="")
        total = match['total_score']
        if total >= 0.8:
            print("Excellent Match ⭐⭐⭐⭐⭐")
        elif total >= 0.6:
            print("Strong Match ⭐⭐⭐⭐")
        elif total >= 0.4:
            print("Good Match ⭐⭐⭐")
        elif total >= 0.2:
            print("Fair Match ⭐⭐")
        else:
            print("Poor Match ⭐")
        
        print("\n   Reasoning:")
        print(f"   {match['reasoning']}")
        print("\n" + "-" * 80)
    
    print("=" * 80)

def main():
    """Main function to run the script."""
    # Display welcome message
    print("\n" + "=" * 80)
    print("Job-to-CVs Batch Matcher")
    print("=" * 80)
    
    # Get job ID from user
    job_id = input("\nEnter Job ID to match against: ")
    
    # Get job title
    job_dir = "DataSet/job_descriptions"
    job_files = [f for f in os.listdir(job_dir) if f.endswith('.docx') and f.split('_')[2] == job_id]
    
    if not job_files:
        print(f"No job found with ID {job_id}.")
        return
    
    job_title = '_'.join(job_files[0].split('_')[3:]).replace('.docx', '')
    
    # Ask for number of CVs to process
    try:
        num_cvs = int(input("Enter number of CVs to process (default: 20): ") or "20")
    except ValueError:
        print("Invalid input. Using default value of 20.")
        num_cvs = 20
    
    # Process and get top matches
    top_matches = batch_match_job_to_cvs(job_id, num_cvs)
    
    # Display results
    if top_matches:
        display_results(top_matches, job_id, job_title)
    else:
        print(f"No matches found for Job ID {job_id}.")

if __name__ == "__main__":
    main() 