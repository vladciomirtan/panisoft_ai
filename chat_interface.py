import os
import sys
from document_processor import extract_text
from matcher import CVJobMatcher
from config import GEMINI_API_KEY

def chat_interface():
    """Interactive chat interface for CV-Job matching."""
    
    # Check if API key is provided
    if not GEMINI_API_KEY:
        print("Error: GEMINI_API_KEY is not set.")
        print("Please set your API key in the config.py file or as an environment variable.")
        sys.exit(1)
    
    print(f"Using Gemini API")
    
    # Get paths to files
    cv_dir = "DataSet/cv"
    job_dir = "DataSet/job_descriptions"
    
    # Get list of CV and job description files
    cv_files = [f for f in os.listdir(cv_dir) if f.endswith(('.docx', '.pdf'))]
    job_files = [f for f in os.listdir(job_dir) if f.endswith(('.docx', '.pdf'))]
    
    # Sort files to ensure consistent ordering
    cv_files.sort()
    job_files.sort()
    
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
            # CV Selection options
            print("\nCV Selection Options:")
            print("1. Browse CVs")
            print("2. Search by CV ID")
            print("3. Browse PDF CVs (without IDs)")
            
            cv_selection_choice = input("Choose option (1-3): ")
            
            if cv_selection_choice == "1":
                # Show available CVs
                print("\nAvailable CVs:")
                docx_cv_files = [f for f in cv_files if f.endswith('.docx')]
                for i, cv_file in enumerate(docx_cv_files[:10]):  # Show first 10 CVs
                    cv_id = cv_file.split('_')[1]
                    cv_name = '_'.join(cv_file.split('_')[2:]).replace('.docx', '')
                    print(f"{i+1}. ID: {cv_id} - {cv_name}")
                
                print("Enter a number (1-10) or type 'more' to see more CVs")
                cv_choice = input("Select a CV: ")
                
                if cv_choice.lower() == 'more':
                    # Show all CVs with ID filter option
                    cv_id_filter = input("Enter ID to filter CVs (or press Enter to show all): ")
                    filtered_cvs = [f for f in docx_cv_files if cv_id_filter in f.split('_')[1]] if cv_id_filter else docx_cv_files
                    
                    for i, cv_file in enumerate(filtered_cvs):
                        cv_id = cv_file.split('_')[1]
                        cv_name = '_'.join(cv_file.split('_')[2:]).replace('.docx', '')
                        print(f"{i+1}. ID: {cv_id} - {cv_name}")
                    
                    cv_index = int(input("Select a CV by number: ")) - 1
                    if cv_index < 0 or cv_index >= len(filtered_cvs):
                        print("Invalid selection. Please try again.")
                        continue
                    
                    selected_cv_file = filtered_cvs[cv_index]
                else:
                    try:
                        cv_index = int(cv_choice) - 1
                        if cv_index < 0 or cv_index >= min(10, len(docx_cv_files)):
                            print("Invalid selection. Please try again.")
                            continue
                        
                        selected_cv_file = docx_cv_files[cv_index]
                    except ValueError:
                        print("Invalid input. Please enter a number.")
                        continue
            
            elif cv_selection_choice == "2":
                # Search by CV ID
                cv_id_to_find = input("Enter CV ID: ")
                docx_cv_files = [f for f in cv_files if f.endswith('.docx')]
                matching_cvs = [f for f in docx_cv_files if f.split('_')[1] == cv_id_to_find]
                
                if not matching_cvs:
                    print(f"No CV found with ID {cv_id_to_find}.")
                    # Show closest matches
                    print("Closest matches:")
                    for f in docx_cv_files[:5]:
                        cv_id = f.split('_')[1]
                        cv_name = '_'.join(f.split('_')[2:]).replace('.docx', '')
                        print(f"ID: {cv_id} - {cv_name}")
                    continue
                
                if len(matching_cvs) == 1:
                    selected_cv_file = matching_cvs[0]
                    cv_id = selected_cv_file.split('_')[1]
                    cv_name = '_'.join(selected_cv_file.split('_')[2:]).replace('.docx', '')
                    print(f"Found CV: ID {cv_id} - {cv_name}")
                else:
                    print("Multiple CVs found with that ID:")
                    for i, cv_file in enumerate(matching_cvs):
                        cv_id = cv_file.split('_')[1]
                        cv_name = '_'.join(cv_file.split('_')[2:]).replace('.docx', '')
                        print(f"{i+1}. ID: {cv_id} - {cv_name}")
                    
                    cv_index = int(input("Select a CV by number: ")) - 1
                    if cv_index < 0 or cv_index >= len(matching_cvs):
                        print("Invalid selection. Please try again.")
                        continue
                    
                    selected_cv_file = matching_cvs[cv_index]
            
            elif cv_selection_choice == "3":
                # Browse PDF CVs without IDs
                pdf_cv_files = [f for f in cv_files if f.endswith('.pdf')]
                
                if not pdf_cv_files:
                    print("No PDF CV files found in the directory.")
                    continue
                
                print("\nAvailable PDF CVs:")
                for i, cv_file in enumerate(pdf_cv_files):
                    # For PDFs without standardized naming, just show the filename
                    print(f"{i+1}. {cv_file}")
                
                try:
                    cv_index = int(input("Select a PDF CV by number: ")) - 1
                    if cv_index < 0 or cv_index >= len(pdf_cv_files):
                        print("Invalid selection. Please try again.")
                        continue
                    
                    selected_cv_file = pdf_cv_files[cv_index]
                except ValueError:
                    print("Invalid input. Please enter a number.")
                    continue
            else:
                print("Invalid option. Please try again.")
                continue
            
            # Job Selection options
            print("\nJob Description Selection Options:")
            print("1. Browse Job Descriptions")
            print("2. Search by Job ID")
            
            job_selection_choice = input("Choose option (1-2): ")
            
            if job_selection_choice == "1":
                # Show available job descriptions
                print("\nAvailable Job Descriptions:")
                for i, job_file in enumerate(job_files[:10]):  # Show first 10 jobs
                    if job_file.endswith('.docx'):
                        job_id = job_file.split('_')[2]
                        job_title = '_'.join(job_file.split('_')[3:]).replace('.docx', '')
                        print(f"{i+1}. ID: {job_id} - {job_title}")
                    else:  # PDF files
                        print(f"{i+1}. {job_file}")
                
                print("Enter a number (1-10) or type 'more' to see more jobs")
                job_choice = input("Select a Job Description: ")
                
                if job_choice.lower() == 'more':
                    # Show all jobs with title filter option
                    job_title_filter = input("Enter job title keyword to filter (or press Enter to show all): ")
                    filtered_jobs = [f for f in job_files if job_title_filter.lower() in f.lower()] if job_title_filter else job_files
                    
                    for i, job_file in enumerate(filtered_jobs):
                        if job_file.endswith('.docx'):
                            job_id = job_file.split('_')[2]
                            job_title = '_'.join(job_file.split('_')[3:]).replace('.docx', '')
                            print(f"{i+1}. ID: {job_id} - {job_title}")
                        else:  # PDF files
                            print(f"{i+1}. {job_file}")
                    
                    job_index = int(input("Select a Job Description by number: ")) - 1
                    if job_index < 0 or job_index >= len(filtered_jobs):
                        print("Invalid selection. Please try again.")
                        continue
                    
                    selected_job_file = filtered_jobs[job_index]
                else:
                    try:
                        job_index = int(job_choice) - 1
                        if job_index < 0 or job_index >= min(10, len(job_files)):
                            print("Invalid selection. Please try again.")
                            continue
                        
                        selected_job_file = job_files[job_index]
                    except ValueError:
                        print("Invalid input. Please enter a number.")
                        continue
            
            elif job_selection_choice == "2":
                # Search by job ID
                job_id_to_find = input("Enter Job ID: ")
                docx_job_files = [f for f in job_files if f.endswith('.docx')]
                matching_jobs = [f for f in docx_job_files if f.split('_')[2] == job_id_to_find]
                
                if not matching_jobs:
                    print(f"No job found with ID {job_id_to_find}.")
                    # Show closest matches
                    print("Closest matches:")
                    for f in docx_job_files[:5]:
                        job_id = f.split('_')[2]
                        job_title = '_'.join(f.split('_')[3:]).replace('.docx', '')
                        print(f"ID: {job_id} - {job_title}")
                    continue
                
                if len(matching_jobs) == 1:
                    selected_job_file = matching_jobs[0]
                    job_id = selected_job_file.split('_')[2]
                    job_title = '_'.join(selected_job_file.split('_')[3:]).replace('.docx', '')
                    print(f"Found Job: ID {job_id} - {job_title}")
                else:
                    print("Multiple jobs found with that ID:")
                    for i, job_file in enumerate(matching_jobs):
                        job_id = job_file.split('_')[2]
                        job_title = '_'.join(job_file.split('_')[3:]).replace('.docx', '')
                        print(f"{i+1}. ID: {job_id} - {job_title}")
                    
                    job_index = int(input("Select a Job Description by number: ")) - 1
                    if job_index < 0 or job_index >= len(matching_jobs):
                        print("Invalid selection. Please try again.")
                        continue
                    
                    selected_job_file = matching_jobs[job_index]
            else:
                print("Invalid option. Please try again.")
                continue
            
            # Get full paths
            cv_path = os.path.join(cv_dir, selected_cv_file)
            job_path = os.path.join(job_dir, selected_job_file)
            
            # Extract CV and job info for display
            if selected_cv_file.endswith('.docx'):
                cv_id = selected_cv_file.split('_')[1]
                cv_name = '_'.join(selected_cv_file.split('_')[2:]).replace('.docx', '')
                cv_display = f"ID {cv_id} - {cv_name}"
            else:  # PDF files without standard naming
                cv_display = selected_cv_file
            
            if selected_job_file.endswith('.docx'):
                job_id = selected_job_file.split('_')[2]
                job_title = '_'.join(selected_job_file.split('_')[3:]).replace('.docx', '')
                job_display = f"ID {job_id} - {job_title}"
            else:  # PDF files without standard naming
                job_display = selected_job_file
            
            print(f"\nSelected CV: {cv_display}")
            print(f"Selected Job: {job_display}")
            
            try:
                # Extract text from the files
                print("\nExtracting text from files...")
                cv_content = extract_text(cv_path)
                job_content = extract_text(job_path)
                
                # Initialize matcher
                matcher = CVJobMatcher()
                
                # Match CV with job description
                print("\nMatching CV with job description...")
                result = matcher.match(cv_content, job_content)
                
                # Display results
                print("\n" + "=" * 80)
                print(f"MATCH ANALYSIS: {cv_display} → {job_display}")
                print("=" * 80)
                
                print(f"\nIndustry Knowledge Score: {result.industry_knowledge_score:.2f} ({result.industry_knowledge_score*100:.0f}%)")
                print(f"Technical Skills Score: {result.technical_skills_score:.2f} ({result.technical_skills_score*100:.0f}%)")
                print(f"Job Description Match Score: {result.job_description_match_score:.2f} ({result.job_description_match_score*100:.0f}%)")
                print(f"Total Score: {result.total_score:.2f} ({result.total_score*100:.0f}%)")
                
                print("\nReasoning:")
                print(result.reasoning)
                
                print("\n" + "=" * 80)
                print(f"Match Rating: ", end="")
                total = result.total_score
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
                print("=" * 80)
                
            except Exception as e:
                print(f"Error: {e}")
        
        else:
            print("Invalid choice. Please enter 1 or 2.")

if __name__ == "__main__":
    chat_interface() 