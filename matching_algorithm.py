import re
from document_processor import extract_text
from typing import List, Dict, Tuple

def extract_skills_with_context(text: str) -> Dict[str, float]:
    """
    Extract skills from text with context and proficiency levels.
    
    Args:
        text (str): The text to extract skills from
        
    Returns:
        Dict[str, float]: Dictionary mapping skills to their proficiency scores (0-1)
    """
    # Define common skills with their variations
    skill_patterns = {
        'python': r'(python|py|django|flask|pandas|numpy|scikit-learn)',
        'java': r'(java|spring|hibernate|j2ee|jsp)',
        'javascript': r'(javascript|js|node\.?js|react|angular|vue)',
        'sql': r'(sql|mysql|postgresql|oracle|mssql)',
        'cloud': r'(aws|azure|gcp|cloud|amazon web services)',
        'devops': r'(devops|docker|kubernetes|jenkins|ci/cd)',
        'machine_learning': r'(machine learning|ml|ai|artificial intelligence|deep learning)',
        'data_analysis': r'(data analysis|data science|statistics|analytics)',
        'project_management': r'(project management|agile|scrum|kanban)',
        'communication': r'(communication|presentation|public speaking)',
        'leadership': r'(leadership|team management|mentoring)',
        'problem_solving': r'(problem solving|critical thinking|analytical)'
    }
    
    # Proficiency indicators
    proficiency_indicators = {
        'expert': 1.0,
        'advanced': 0.8,
        'proficient': 0.6,
        'intermediate': 0.4,
        'basic': 0.2,
        'familiar': 0.1
    }
    
    # Experience indicators
    experience_indicators = {
        r'(\d+)\s*(?:year|yr)s?': 0.1,  # Each year adds 0.1 to the score
        r'(\d+)\s*(?:month|mo)s?': 0.008  # Each month adds 0.008 to the score
    }
    
    skills = {}
    text_lower = text.lower()
    
    # Extract skills with context
    for skill, pattern in skill_patterns.items():
        matches = re.finditer(pattern, text_lower)
        for match in matches:
            # Get context around the match
            start = max(0, match.start() - 50)
            end = min(len(text_lower), match.end() + 50)
            context = text_lower[start:end]
            
            # Check for proficiency indicators
            proficiency = 0.5  # Default proficiency
            for indicator, score in proficiency_indicators.items():
                if indicator in context:
                    proficiency = max(proficiency, score)
            
            # Check for experience indicators
            for exp_pattern, exp_score in experience_indicators.items():
                exp_matches = re.finditer(exp_pattern, context)
                for exp_match in exp_matches:
                    try:
                        years = float(exp_match.group(1))
                        proficiency = min(1.0, proficiency + (years * exp_score))
                    except:
                        continue
            
            # Update skill score
            if skill in skills:
                skills[skill] = max(skills[skill], proficiency)
            else:
                skills[skill] = proficiency
    
    return skills

def match_cv_to_job_description(cv_path: str, job_path: str) -> Tuple[float, str]:
    """
    Match a CV to a job description using weighted skills and context analysis.
    
    Args:
        cv_path (str): Path to the CV document
        job_path (str): Path to the job description document
        
    Returns:
        Tuple[float, str]: Match score (0-100) and matching skills with weights
    """
    # Extract text from documents
    cv_text = extract_text(cv_path)
    job_text = extract_text(job_path)
    
    # Extract skills with context and weights
    cv_skills = extract_skills_with_context(cv_text)
    job_skills = extract_skills_with_context(job_text)
    
    if not job_skills:
        return 0.0, "No required skills found in job description"
    
    # Calculate weighted match score
    total_weight = sum(job_skills.values())
    match_score = 0.0
    matching_skills = []
    
    for skill, job_weight in job_skills.items():
        if skill in cv_skills:
            # Calculate skill match score (0-1)
            skill_match = min(1.0, cv_skills[skill] / job_weight)
            # Add weighted contribution to total score
            match_score += skill_match * (job_weight / total_weight)
            matching_skills.append(f"{skill} ({skill_match:.1%})")
    
    # Convert to percentage
    match_score *= 100
    
    # Format matching skills string
    skills_str = ", ".join(matching_skills) if matching_skills else "No matching skills found"
    
    return match_score, skills_str 