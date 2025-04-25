import os
import sys
import pandas as pd
from tqdm import tqdm
from document_processor import extract_text_from_docx, load_cvs, load_job_descriptions
from matcher import CVJobMatcher
from config import OPENROUTE_API_KEY

def generate_excel_report(sample_size=None):
    """
    Generate an Excel report of CV-Job matches.
    
    Args:
        sample_size (int, optional): Number of CVs and jobs to use (for testing with smaller dataset)
    """
    
    # Check if API key is provided
    if not OPENROUTE_API_KEY:
        print("Error: OPENROUTE_API_KEY is not set.")
        print("Please set your API key in the config.py file or as an environment variable.")
        sys.exit(1)
    
    print("=" * 80)
    print("Generating Excel Report for CV-Job Matching")
    print("=" * 80)
    
    # Get paths to sample files
    cv_dir = "DataSet/cv"
    job_dir = "DataSet/job_descriptions"
    
    # Load the CVs and job descriptions
    print("Loading CVs and job descriptions...")
    cv_files = [f for f in os.listdir(cv_dir) if f.endswith('.docx')]
    job_files = [f for f in os.listdir(job_dir) if f.endswith('.docx')]
    
    # If sample size is specified, limit the number of files
    if sample_size:
        print(f"Using sample size: {sample_size} CVs and job descriptions")
        cv_files = cv_files[:sample_size]
        job_files = job_files[:sample_size]
    
    # Initialize matcher
    matcher = CVJobMatcher()
    
    # Create a DataFrame to store the results
    # Headers: CV, Job, Industry Score, Technical Score, Match Score, Total Score, Reasoning
    results = []
    
    # Create a lookup to convert file names to more readable names
    cv_names = {f: f.replace('cv_', '').replace('.docx', '') for f in cv_files}
    job_names = {f: f.replace('job_description_', '').replace('.docx', '') for f in job_files}
    
    # Calculate total number of matches
    total_matches = len(cv_files) * len(job_files)
    print(f"Running {total_matches} matches ({len(cv_files)} CVs x {len(job_files)} jobs)...")
    
    # Create progress bar
    progress = tqdm(total=total_matches, desc="Matching CVs with Jobs")
    
    # For each CV and job description, calculate the match
    for job_file in job_files:
        job_path = os.path.join(job_dir, job_file)
        job_content = extract_text_from_docx(job_path)
        
        for cv_file in cv_files:
            cv_path = os.path.join(cv_dir, cv_file)
            cv_content = extract_text_from_docx(cv_path)
            
            # Match CV with job description
            result = matcher.match(cv_content, job_content)
            
            # Store the result
            results.append({
                'CV': cv_names[cv_file],
                'CV_File': cv_file,
                'Job': job_names[job_file],
                'Job_File': job_file,
                'Industry_Score': result.industry_knowledge_score,
                'Technical_Score': result.technical_skills_score,
                'Match_Score': result.job_description_match_score,
                'Total_Score': result.total_score,
                'Reasoning': result.reasoning[:500]  # Limit reasoning length to avoid Excel issues
            })
            
            # Update progress bar
            progress.update(1)
    
    # Close progress bar
    progress.close()
    
    # Convert to DataFrame
    df = pd.DataFrame(results)
    
    # Add percentage columns for easier reading
    df['Industry_Score_Pct'] = df['Industry_Score'] * 100
    df['Technical_Score_Pct'] = df['Technical_Score'] * 100
    df['Match_Score_Pct'] = df['Match_Score'] * 100
    df['Total_Score_Pct'] = df['Total_Score'] * 100
    
    # Create Excel file
    excel_file = "cv_job_matching_results.xlsx"
    print(f"\nSaving results to {excel_file}...")
    
    # Create a Pandas Excel writer
    with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
        # Write the main results sheet
        df.to_excel(writer, sheet_name='All_Matches', index=False)
        
        # Create a sheet with the best CV for each job
        best_matches = df.loc[df.groupby('Job')['Total_Score'].idxmax()]
        best_matches = best_matches.sort_values('Total_Score', ascending=False)
        best_matches.to_excel(writer, sheet_name='Best_Match_Per_Job', index=False)
        
        # Create a sheet with the top 5 jobs for each CV
        top_jobs_per_cv = pd.DataFrame()
        for cv in df['CV'].unique():
            cv_data = df[df['CV'] == cv].sort_values('Total_Score', ascending=False).head(5)
            top_jobs_per_cv = pd.concat([top_jobs_per_cv, cv_data])
        top_jobs_per_cv.to_excel(writer, sheet_name='Top5_Jobs_Per_CV', index=False)
        
        # Create a sheet with the top 5 CVs for each job
        top_cvs_per_job = pd.DataFrame()
        for job in df['Job'].unique():
            job_data = df[df['Job'] == job].sort_values('Total_Score', ascending=False).head(5)
            top_cvs_per_job = pd.concat([top_cvs_per_job, job_data])
        top_cvs_per_job.to_excel(writer, sheet_name='Top5_CVs_Per_Job', index=False)
    
    print(f"Excel file created: {excel_file}")
    print("\nThe Excel file contains the following sheets:")
    print("1. All_Matches: All CV-job combinations")
    print("2. Best_Match_Per_Job: The best CV for each job")
    print("3. Top5_Jobs_Per_CV: The top 5 jobs for each CV")
    print("4. Top5_CVs_Per_Job: The top 5 CVs for each job")
    print("\nScores are provided in both decimal (0-1) and percentage (0-100%) formats.")
    print("Process completed successfully!")

if __name__ == "__main__":
    # Check if a sample size is provided as command line argument
    sample_size = None
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        sample_size = int(sys.argv[1])
    
    generate_excel_report(sample_size) 