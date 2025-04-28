import os
import sys
import heapq
import time
from document_processor import extract_text, load_job_descriptions, load_cvs
from matcher import CVJobMatcher
from config import GEMINI_API_KEY

def get_job_files(job_id=None, base_dir=None):
    """
    Get job description files from the directory, optionally filtering by ID.
    
    Args:
        job_id (str, optional): ID of the job to filter by
        base_dir (str, optional): Base directory path
        
    Returns:
        list: List of job files
        dict: Dictionary mapping file names to display names
    """
    if base_dir is None:
        base_dir = os.path.dirname(os.path.abspath(__file__))
    job_dir = os.path.join(base_dir, "DataSet", "job_descriptions")
    job_files = [f for f in os.listdir(job_dir) if f.endswith(('.docx', '.pdf'))]
    job_display_names = {}
    
    for file in job_files:
        if file.endswith('.docx') and file.startswith('job_description_'):
            # Standard naming convention: job_description_ID_Title.docx
            parts = file.split('_')
            if len(parts) >= 4:
                file_id = parts[2]
                name = '_'.join(parts[3:]).replace('.docx', '')
                job_display_names[file] = f"ID {file_id} - {name}"
        elif file.endswith('.pdf'):
            # PDF files might not follow the naming convention
            if file.startswith('job_description_'):
                # Try to extract ID if it follows the convention
                parts = file.split('_')
                if len(parts) >= 4:
                    file_id = parts[2]
                    name = '_'.join(parts[3:]).replace('.pdf', '')
                    job_display_names[file] = f"ID {file_id} - {name}"
                else:
                    # For PDF files without standard naming
                    job_display_names[file] = file.replace('.pdf', '')
            else:
                # For PDF files without standard naming
                job_display_names[file] = file.replace('.pdf', '')
    
    # If job_id is provided, filter the files
    if job_id:
        if job_id.isdigit():
            # Try to find by numeric ID
            filtered_files = [f for f in job_files if f.endswith('.docx') and f.split('_')[2] == job_id]
        else:
            # Assume job_id is a filename
            filtered_files = [f for f in job_files if f == job_id or f.replace('.pdf', '') == job_id or f.replace('.docx', '') == job_id]
        
        return filtered_files, {k: job_display_names[k] for k in filtered_files if k in job_display_names}
    
    return job_files, job_display_names

def get_cv_files(base_dir=None):
    """
    Get CV files from the directory.
    
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
    
    return cv_files, cv_display_names

def batch_match_job_to_cvs(job_path, num_cvs=20, top_matches=5, max_retries=3):
    """
    Compare a specific job description with multiple CVs and return the top matches.
    
    Args:
        job_path (str): Path to the job description file to match against
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
    base_dir = os.path.dirname(os.path.abspath(__file__))
    cv_dir = os.path.join(base_dir, "DataSet", "cv")
    
    # Extract job content
    job_content = extract_text(job_path)
    
    # Get display name for the job
    job_name = os.path.basename(job_path)
    if job_name.endswith('.docx') and job_name.startswith('job_description_'):
        parts = job_name.split('_')
        if len(parts) >= 4:
            job_id = parts[2]
            title = '_'.join(parts[3:]).replace('.docx', '')
            job_name = f"ID {job_id} - {title}"
    
    # Load CVs
    cv_files = [f for f in os.listdir(cv_dir) if f.endswith(('.docx', '.pdf'))]
    
    # Limit to the specified number of CVs
    if num_cvs < len(cv_files):
        cv_files = cv_files[:num_cvs]
    
    # Initialize matcher
    matcher = CVJobMatcher()
    
    # Store results
    all_results = []
    
    print(f"Matching Job: {job_name} with {len(cv_files)} CVs...")
    
    # Track API calls for rate limiting
    api_call_count = 0
    
    # Process each CV
    for i, cv_file in enumerate(cv_files):
        # Check if we need to pause for rate limiting (after 15 API calls)
        if api_call_count >= 15:
            print("\n=== RATE LIMIT REACHED ===")
            print("Pausing for 60 seconds to avoid API rate limiting...")
            for remaining in range(60, 0, -1):
                sys.stdout.write(f"\rResuming in {remaining} seconds...")
                sys.stdout.flush()
                time.sleep(1)
            print("\nResuming processing...")
            # Reset the counter after the pause
            api_call_count = 0
        
        retry_count = 0
        success = False
        
        while retry_count < max_retries and not success:
            try:
                # Get CV display name
                cv_name = cv_file
                if cv_file.endswith('.docx') and cv_file.startswith('cv_'):
                    parts = cv_file.split('_')
                    if len(parts) >= 3:
                        cv_id = parts[1]
                        name = '_'.join(parts[2:]).replace('.docx', '')
                        cv_name = f"ID {cv_id} - {name}"
                
                # If it's a standard CV file, extract ID
                if cv_file.endswith('.docx') and cv_file.startswith('cv_') and len(cv_file.split('_')) >= 3:
                    cv_id = cv_file.split('_')[1]
                else:
                    # For non-standard files, use placeholder
                    cv_id = "N/A"
                
                # Display progress
                print(f"Processing {i+1}/{len(cv_files)}: {cv_name}")
                
                # Get CV content
                cv_path = os.path.join(cv_dir, cv_file)
                cv_content = extract_text(cv_path)
                
                # Match CV with job description
                result = matcher.match(cv_content, job_content)
                
                # Increment API call counter after successful call
                api_call_count += 1
                
                # Store result with CV info
                all_results.append({
                    'cv_id': cv_id,
                    'cv_name': cv_name.replace('ID ' + cv_id + ' - ', '') if cv_id != "N/A" else cv_name,
                    'cv_file': cv_file,
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
                    cv_name = cv_file
                    if cv_file.endswith('.docx') and cv_file.startswith('cv_') and len(cv_file.split('_')) >= 3:
                        cv_id = cv_file.split('_')[1]
                    else:
                        cv_id = "N/A"
                    
                    all_results.append({
                        'cv_id': cv_id,
                        'cv_name': cv_name.replace('ID ' + cv_id + ' - ', '') if cv_id != "N/A" else cv_name,
                        'cv_file': cv_file,
                        'total_score': 0.0,
                        'industry_knowledge_score': 0.0,
                        'technical_skills_score': 0.0,
                        'job_description_match_score': 0.0,
                        'reasoning': f"Error processing: {str(e)}"
                    })
    
    # Sort results by total score (highest first)
    all_results.sort(key=lambda x: x['total_score'], reverse=True)
    
    # Return top matches
    return all_results[:top_matches], job_name

def display_results(top_matches, job_name):
    """Display the results in a formatted way."""
    print("\n" + "=" * 80)
    print(f"TOP 5 MATCHES FOR JOB: {job_name}")
    print("=" * 80)
    
    for i, match in enumerate(top_matches):
        if match['cv_id'] != "N/A":
            cv_display = f"ID: {match['cv_id']} - {match['cv_name']}"
        else:
            cv_display = match['cv_name']
            
        print(f"\n{i+1}. {cv_display}")
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
    
    # List all available jobs
    job_files, job_display_names = get_job_files()
    
    print("\nAvailable Jobs:")
    job_list = [(f, job_display_names[f]) for f in job_files if f in job_display_names]
    job_list.sort(key=lambda x: x[1])  # Sort by display name
    
    for i, (filename, display_name) in enumerate(job_list):
        print(f"{i+1}. {display_name}")
    
    # Get job selection from user
    while True:
        try:
            choice = input("\nEnter job number, ID, or filename: ")
            
            if choice.isdigit() and 1 <= int(choice) <= len(job_list):
                # User entered a list number
                job_file = job_list[int(choice)-1][0]
                break
            elif choice in [f.split('_')[2] for f in job_files if f.endswith('.docx') and f.startswith('job_description_') and len(f.split('_')) > 3]:
                # User entered an ID
                job_identifier = choice
                break
            elif choice in job_files or choice.replace('.pdf', '') in [f.replace('.pdf', '') for f in job_files]:
                # User entered a filename
                job_identifier = choice
                break
            else:
                print("Invalid selection. Please try again.")
        except ValueError:
            print("Invalid input. Please try again.")
    
    # If user selected by number, get the identifier
    if 'job_file' in locals():
        job_identifier = job_file
    
    # Ask for number of CVs to process
    try:
        num_cvs = int(input("Enter number of CVs to process (default: 20): ") or "20")
    except ValueError:
        print("Invalid input. Using default value of 20.")
        num_cvs = 20
    
    # Process and get top matches
    top_matches, job_name = batch_match_job_to_cvs(job_identifier, num_cvs)
    
    # Display results
    if top_matches:
        display_results(top_matches, job_name)
    else:
        print(f"No matches found for job: {job_identifier}.")

if __name__ == "__main__":
    main() 