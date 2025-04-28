import os
import sys
import gc
import time
from document_processor import load_cvs, load_job_descriptions
from matcher import CVJobMatcher, format_top_matches
from config import GEMINI_API_KEY, OUTPUT_DIR, CV_DIR, JOB_DESCRIPTIONS_DIR

def main():
    start_time = time.time()
    try:
        # Check if API key is provided
        if not GEMINI_API_KEY:
            print("Error: GEMINI_API_KEY is not set.")
            print("Please set your API key in the config.py file or as an environment variable.")
            sys.exit(1)
            
        print("Loading CVs and job descriptions...")
        cvs = load_cvs(CV_DIR)
        job_descriptions = load_job_descriptions(JOB_DESCRIPTIONS_DIR)
        
        print(f"Loaded {len(cvs)} CVs and {len(job_descriptions)} job descriptions.")
        
        # Initialize the matcher
        matcher = CVJobMatcher()
        
        # Match all CVs with all job descriptions
        print("Starting the matching process using Gemini API...")
        matches = matcher.match_all(cvs, job_descriptions)
        
        # Format and display the results
        results = format_top_matches(matches, top_n=5)
        
        # Create output directory if it doesn't exist
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        
        # Save results to file in the output directory
        output_file = os.path.join(OUTPUT_DIR, "matching_results.txt")
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(results)
            
        print(f"Matching completed. Results saved to '{output_file}'.")
        
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
                
        # Clean up large objects to free memory
        del matches, results, cvs, job_descriptions
        
        # Calculate and display total execution time
        end_time = time.time()
        total_time = end_time - start_time
        hours, remainder = divmod(total_time, 3600)
        minutes, seconds = divmod(remainder, 60)
        print(f"\nTotal execution time: {int(hours)}h {int(minutes)}m {int(seconds)}s")
    
    finally:
        # Force garbage collection to clean up resources
        gc.collect()
        # Ensure proper termination
        print("Process completed successfully.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # One final garbage collection to ensure all resources are freed
        gc.collect()
        # Exit explicitly
        sys.exit(0) 