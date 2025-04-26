import os
import sys
import heapq
from document_processor import extract_text_from_docx, load_job_descriptions, load_cvs
from matcher import CVJobMatcher
from config import GEMINI_API_KEY

def batch_match_cv_to_jobs(cv_id, num_jobs=20, top_matches=5, max_retries=3):
    """
    Compare a specific CV with multiple job descriptions and return the top matches.
    
    Args:
        cv_id (str): ID of the CV to match against jobs
        num_jobs (int): Number of job descriptions to process (default: 20)
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
    
    # Load CVs and find the specific CV
    cvs = load_cvs()
    if cv_id not in cvs:
        # Find CV file manually if it's not in the dictionary
        cv_files = [f for f in os.listdir(cv_dir) if f.endswith('.docx')]
        matching_cvs = [f for f in cv_files if f.split('_')[1] == cv_id]
        
        if not matching_cvs:
            print(f"No CV found with ID {cv_id}.")
            return []
        
        cv_file = matching_cvs[0]
        cv_path = os.path.join(cv_dir, cv_file)
        cv_content = extract_text_from_docx(cv_path)
        cv_name = '_'.join(cv_file.split('_')[2:]).replace('.docx', '')
    else:
        cv_content = cvs[cv_id]
        # Find the CV file to get the name
        cv_files = [f for f in os.listdir(cv_dir) if f.endswith('.docx') and f.split('_')[1] == cv_id]
        cv_name = '_'.join(cv_files[0].split('_')[2:]).replace('.docx', '') if cv_files else f"CV {cv_id}"
    
    # Load job descriptions
    job_files = [f for f in os.listdir(job_dir) if f.endswith('.docx')]
    job_files.sort()
    
    # Limit to the specified number of jobs
    job_files = job_files[:num_jobs]
    
    # Initialize matcher
    matcher = CVJobMatcher()
    
    # Store results
    all_results = []
    
    print(f"Matching CV ID {cv_id} ({cv_name}) with {len(job_files)} job descriptions...")
    
    # Process each job description
    for i, job_file in enumerate(job_files):
        retry_count = 0
        success = False
        
        while retry_count < max_retries and not success:
            try:
                # Extract job info
                job_id = job_file.split('_')[2]
                job_title = '_'.join(job_file.split('_')[3:]).replace('.docx', '')
                
                # Display progress
                print(f"Processing {i+1}/{len(job_files)}: Job {job_id} - {job_title}")
                
                # Get job content
                job_path = os.path.join(job_dir, job_file)
                job_content = extract_text_from_docx(job_path)
                
                # Match CV with job description
                result = matcher.match(cv_content, job_content)
                
                # Store result with job info
                all_results.append({
                    'job_id': job_id,
                    'job_title': job_title,
                    'total_score': result.total_score,
                    'industry_knowledge_score': result.industry_knowledge_score,
                    'technical_skills_score': result.technical_skills_score,
                    'job_description_match_score': result.job_description_match_score,
                    'reasoning': result.reasoning
                })
                
                success = True
                
            except Exception as e:
                retry_count += 1
                print(f"Error processing job {job_file}: {e}")
                
                if retry_count < max_retries:
                    print(f"Retrying... (Attempt {retry_count+1}/{max_retries})")
                else:
                    print(f"Failed to process job {job_file} after {max_retries} attempts. Skipping.")
                    # Add a placeholder result to ensure we have data for reporting
                    all_results.append({
                        'job_id': job_file.split('_')[2],
                        'job_title': '_'.join(job_file.split('_')[3:]).replace('.docx', ''),
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

def display_results(top_matches, cv_id, cv_name):
    """Display the results in a formatted way."""
    print("\n" + "=" * 80)
    print(f"TOP 5 JOB MATCHES FOR CV: {cv_id} - {cv_name}")
    print("=" * 80)
    
    for i, match in enumerate(top_matches):
        print(f"\n{i+1}. Job ID: {match['job_id']} - {match['job_title']}")
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
    print("CV-to-Jobs Batch Matcher")
    print("=" * 80)
    
    # Get CV ID from user
    cv_id = input("\nEnter CV ID to match against jobs: ")
    
    # Get CV name
    cv_dir = "DataSet/cv"
    cv_files = [f for f in os.listdir(cv_dir) if f.endswith('.docx') and f.split('_')[1] == cv_id]
    
    if not cv_files:
        print(f"No CV found with ID {cv_id}.")
        return
    
    cv_name = '_'.join(cv_files[0].split('_')[2:]).replace('.docx', '')
    
    # Ask for number of jobs to process
    try:
        num_jobs = int(input("Enter number of job descriptions to process (default: 20): ") or "20")
    except ValueError:
        print("Invalid input. Using default value of 20.")
        num_jobs = 20
    
    # Process and get top matches
    top_matches = batch_match_cv_to_jobs(cv_id, num_jobs)
    
    # Display results
    if top_matches:
        display_results(top_matches, cv_id, cv_name)
    else:
        print(f"No matches found for CV ID {cv_id}.")

if __name__ == "__main__":
    main() 