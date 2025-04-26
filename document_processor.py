import os
import docx
from typing import Dict, List, Tuple
from config import CV_DIR, JOB_DESCRIPTIONS_DIR

def extract_text_from_docx(file_path: str) -> str:
    """
    Extract text from a .docx file.
    
    Args:
        file_path (str): Path to the .docx file
        
    Returns:
        str: Extracted text from the document
    """
    try:
        doc = docx.Document(file_path)
        full_text = []
        for para in doc.paragraphs:
            full_text.append(para.text)
        return '\n'.join(full_text)
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return ""

def load_cvs() -> Dict[str, str]:
    """
    Load all CVs from the CV directory.
    
    Returns:
        Dict[str, str]: Dictionary mapping CV IDs to their content
    """
    cvs = {}
    for filename in os.listdir(CV_DIR):
        if filename.endswith('.docx'):
            cv_id = filename.split('_')[1]  # Extract ID number
            name = '_'.join(filename.split('_')[2:]).replace('.docx', '')  # Extract name
            file_path = os.path.join(CV_DIR, filename)
            content = extract_text_from_docx(file_path)
            cvs[f"{cv_id}_{name}"] = content
    return cvs

def load_job_descriptions() -> Dict[str, str]:
    """
    Load all job descriptions from the job descriptions directory.
    
    Returns:
        Dict[str, str]: Dictionary mapping job description IDs to their content
    """
    job_descriptions = {}
    for filename in os.listdir(JOB_DESCRIPTIONS_DIR):
        if filename.endswith('.docx'):
            job_id = filename.split('_')[2]  # Extract ID number
            job_title = '_'.join(filename.split('_')[3:]).replace('.docx', '')  # Extract job title
            file_path = os.path.join(JOB_DESCRIPTIONS_DIR, filename)
            content = extract_text_from_docx(file_path)
            job_descriptions[f"{job_id}_{job_title}"] = content
    return job_descriptions 