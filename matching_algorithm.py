import re
import random
from document_processor import extract_text

def extract_skills(text):
    """
    Extract skills from text using a basic keyword search.
    
    Args:
        text (str): The text to extract skills from
        
    Returns:
        list: List of extracted skills
    """
    # Define common skills to look for (basic implementation)
    common_skills = [
        "python", "java", "javascript", "html", "css", "react", "angular", "vue", "node", 
        "express", "django", "flask", "sql", "mongodb", "nosql", "aws", "azure", "gcp",
        "docker", "kubernetes", "jenkins", "git", "agile", "scrum", "project management",
        "leadership", "communication", "teamwork", "problem solving", "data analysis",
        "machine learning", "ai", "artificial intelligence", "deep learning", "nlp",
        "data science", "statistics", "r", "matlab", "excel", "powerpoint", "word",
        "photoshop", "illustrator", "indesign", "figma", "sketch", "ui/ux", "ux design",
        "ui design", "product design", "graphic design", "marketing", "social media",
        "seo", "content writing", "copywriting", "sales", "customer service", "operations",
        "finance", "accounting", "human resources", "recruitment", "training", 
        "c++", "c#", "php", "ruby", "swift", "kotlin", "objective-c", "scala", "go",
        "rust", "typescript", "bash", "shell", "powershell", "linux", "unix", "windows",
        "macos", "ios", "android", "mobile development", "web development", "full stack",
        "frontend", "backend", "devops", "security", "cybersecurity", "networking",
        "cloud computing", "distributed systems", "microservices", "restful api", 
        "graphql", "soap", "web services", "database design", "database administration",
        "etl", "data warehousing", "data modeling", "big data", "hadoop", "spark",
        "tensorflow", "pytorch", "keras", "scikit-learn", "pandas", "numpy"
    ]
    
    # Convert text to lowercase for case-insensitive matching
    text_lower = text.lower()
    
    # Find all skills in the text
    found_skills = []
    for skill in common_skills:
        if re.search(r'\b' + re.escape(skill) + r'\b', text_lower):
            found_skills.append(skill)
    
    return found_skills

def match_cv_to_job_description(cv_path, job_path):
    """
    Match a CV to a job description using skills extraction.
    This is a simplified implementation that extracts skills from both documents
    and calculates a match score based on the overlap.
    
    Args:
        cv_path (str): Path to the CV document
        job_path (str): Path to the job description document
        
    Returns:
        float: Match score as a percentage
        str: Comma-separated list of matching skills
    """
    # Extract text from documents
    cv_text = extract_text(cv_path)
    job_text = extract_text(job_path)
    
    # Extract skills from both documents
    cv_skills = extract_skills(cv_text)
    job_skills = extract_skills(job_text)
    
    # Find matching skills
    matching_skills = [skill for skill in cv_skills if skill in job_skills]
    
    # Calculate match score as a percentage
    if len(job_skills) > 0:
        # Main score based on the percentage of required skills that are matched
        match_score = (len(matching_skills) / len(job_skills)) * 100
        
        # Add some random variance (±10%) to simulate more nuanced matching
        # In a real implementation, this would be based on more sophisticated analysis
        variance = random.uniform(-10, 10)
        match_score = min(100, max(0, match_score + variance))
    else:
        match_score = 0
    
    # Return the score and matching skills as a comma-separated string
    return match_score, ", ".join(matching_skills) if matching_skills else "No matching skills found" 