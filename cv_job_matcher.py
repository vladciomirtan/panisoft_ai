import os
import sys
import heapq
from document_processor import extract_text, load_job_descriptions, load_cvs
from matcher import CVJobMatcher
from config import GEMINI_API_KEY

def get_cv_files(cv_id=None, base_dir=None):
    """
    Get CV files from the directory, optionally filtering by ID.
    
    Args:
        cv_id (str, optional): ID of the CV to filter by
        
    Returns:
        list: List of CV files
        dict: Dictionary mapping file names to display names
    """
    if base_dir is None:
        base_dir = os.path.dirname(os.path.abspath(__file__))
    cv_dir = os.path.join(base_dir, "DataSet", "cv")
    cv_files = [f for f in os.listdir(cv_dir) if f.endswith(('.docx', '.pdf'))]
    cv_display_names = {}
    
    for file in cv_files:
        if file.endswith('.docx') and file.startswith('cv_'):
            # Standard naming convention: cv_ID_Name.docx
            parts = file.split('_')
            if len(parts) >= 3:
                file_id = parts[1]
                name = '_'.join(parts[2:]).replace('.docx', '')
                cv_display_names[file] = f"ID {file_id} - {name}"
        elif file.endswith('.pdf'):
            # PDF files might not follow the naming convention
            if file.startswith('cv_'):
                # Try to extract ID if it follows the convention
                parts = file.split('_')
                if len(parts) >= 3:
                    file_id = parts[1]
                    name = '_'.join(parts[2:]).replace('.pdf', '')
                    cv_display_names[file] = f"ID {file_id} - {name}"
                else:
                    # For PDF files without standard naming
                    cv_display_names[file] = file.replace('.pdf', '')
            else:
                # For PDF files without standard naming
                cv_display_names[file] = file.replace('.pdf', '')
    
    # If cv_id is provided, filter the files
    if cv_id:
        if cv_id.isdigit():
            # Try to find by numeric ID
            filtered_files = [f for f in cv_files if f.endswith('.docx') and f.split('_')[1] == cv_id]
        else:
            # Assume cv_id is a filename
            filtered_files = [f for f in cv_files if f == cv_id or f.replace('.pdf', '') == cv_id or f.replace('.docx', '') == cv_id]
        
        return filtered_files, {k: cv_display_names[k] for k in filtered_files if k in cv_display_names}
    
    return cv_files, cv_display_names

def batch_match_cv_to_jobs(cv_path, num_jobs=20, top_matches=5, max_retries=3):
    """
    Compare a specific CV with multiple job descriptions and return the top matches.
    
    Args:
        cv_path (str): Path to the CV file to match against jobs
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
    base_dir = os.path.dirname(os.path.abspath(__file__))
    job_dir = os.path.join(base_dir, "DataSet", "job_descriptions")
    
    # Extract CV content
    cv_content = extract_text(cv_path)
    
    # Get display name for the CV
    cv_name = os.path.basename(cv_path)
    if cv_name.endswith('.docx') and cv_name.startswith('cv_'):
        parts = cv_name.split('_')
        if len(parts) >= 3:
            cv_id = parts[1]
            name = '_'.join(parts[2:]).replace('.docx', '')
            cv_name = f"ID {cv_id} - {name}"
    
    # Load job descriptions
    job_files = [f for f in os.listdir(job_dir) if f.endswith(('.docx', '.pdf'))]
    job_files.sort()
    
    # Limit to the specified number of jobs
    job_files = job_files[:num_jobs]
    
    # Initialize matcher
    matcher = CVJobMatcher()
    
    # Store results
    all_results = []
    
    print(f"Matching CV: {cv_name} with {len(job_files)} job descriptions...")
    
    # Process each job description
    for i, job_file in enumerate(job_files):
        retry_count = 0
        success = False
        
        while retry_count < max_retries and not success:
            try:
                # Extract job info
                if job_file.endswith('.docx') and job_file.startswith('job_description_'):
                    # Standard naming: job_description_ID_Title.docx
                    parts = job_file.split('_')
                    if len(parts) >= 4:
                        job_id = parts[2]
                        job_title = '_'.join(parts[3:]).replace('.docx', '')
                    else:
                        job_id = "N/A"
                        job_title = job_file.replace('job_description_', '').replace('.docx', '')
                else:
                    # For PDF files or non-standard naming
                    job_id = "N/A"
                    job_title = job_file.replace('.pdf', '').replace('.docx', '')
                
                # Display progress
                print(f"Processing {i+1}/{len(job_files)}: Job {job_id} - {job_title}")
                
                # Get job content
                job_path = os.path.abspath(os.path.join(job_dir, job_file))
                job_content = extract_text(job_path)
                
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
                    if job_file.endswith('.docx') and job_file.startswith('job_description_'):
                        job_id = job_file.split('_')[2]
                        job_title = '_'.join(job_file.split('_')[3:]).replace('.docx', '')
                    else:
                        job_id = "N/A"
                        job_title = job_file.replace('.pdf', '').replace('.docx', '')
                    
                    all_results.append({
                        'job_id': job_id,
                        'job_title': job_title,
                        'total_score': 0.0,
                        'industry_knowledge_score': 0.0,
                        'technical_skills_score': 0.0,
                        'job_description_match_score': 0.0,
                        'reasoning': f"Error processing: {str(e)}"
                    })
    
    # Sort results by total score (highest first)
    all_results.sort(key=lambda x: x['total_score'], reverse=True)
    
    # Return top matches
    return all_results[:top_matches], cv_name

def display_results(top_matches, cv_name):
    """Display the results in a formatted way."""
    print("\n" + "=" * 80)
    print(f"TOP 5 JOB MATCHES FOR CV: {cv_name}")
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
    
    # List all available CVs
    cv_files, cv_display_names = get_cv_files()
    
    print("\nAvailable CVs:")
    cv_list = [(f, cv_display_names[f]) for f in cv_files if f in cv_display_names]
    cv_list.sort(key=lambda x: x[1])  # Sort by display name
    
    for i, (filename, display_name) in enumerate(cv_list):
        print(f"{i+1}. {display_name}")
    
    # Get CV selection from user
    while True:
        try:
            choice = input("\nEnter CV number, ID, or filename: ")
            
            if choice.isdigit() and 1 <= int(choice) <= len(cv_list):
                # User entered a list number
                cv_file = cv_list[int(choice)-1][0]
                break
            elif choice in [f.split('_')[1] for f in cv_files if f.endswith('.docx') and f.startswith('cv_') and len(f.split('_')) > 1]:
                # User entered an ID
                cv_identifier = choice
                break
            elif choice in cv_files or choice.replace('.pdf', '') in [f.replace('.pdf', '') for f in cv_files]:
                # User entered a filename
                cv_identifier = choice
                break
            else:
                print("Invalid selection. Please try again.")
        except ValueError:
            print("Invalid input. Please try again.")
    
    # If user selected by number, get the identifier
    if 'cv_file' in locals():
        cv_identifier = cv_file
    
    # Ask for number of jobs to process
    try:
        num_jobs = int(input("Enter number of job descriptions to process (default: 20): ") or "20")
    except ValueError:
        print("Invalid input. Using default value of 20.")
        num_jobs = 20
    
    # Process and get top matches
    top_matches, cv_name = batch_match_cv_to_jobs(cv_identifier, num_jobs)
    
    # Display results
    if top_matches:
        display_results(top_matches, cv_name)
    else:
        print(f"No matches found for CV: {cv_identifier}.")

if __name__ == "__main__":
    main() 