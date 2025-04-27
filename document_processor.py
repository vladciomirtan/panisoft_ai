import os
import docx
from typing import List, Dict, Optional, Any
import re
import fitz  # PyMuPDF for PDF processing
from config import CV_DIR, JOB_DESCRIPTIONS_DIR

def extract_text(file_path: str) -> str:
    """
    Extract text from a document file.

    Args:
        file_path (str): Path to the document file (.docx or .pdf)

    Returns:
        str: Extracted text
    """
    if file_path.lower().endswith('.docx'):
        return extract_text_from_docx(file_path)
    elif file_path.lower().endswith('.pdf'):
        return extract_text_from_pdf(file_path)
    else:
        raise ValueError(f"Unsupported file format: {file_path}")

def extract_text_from_docx(file_path: str) -> str:
    """
    Extract text from a .docx file.

    Args:
        file_path (str): Path to the .docx file

    Returns:
        str: Extracted text
    """
    try:
        doc = docx.Document(file_path)
        return "\n".join([para.text for para in doc.paragraphs])
    except Exception as e:
        print(f"Error extracting text from {file_path}: {e}")
        return ""

def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract text from a PDF file using PyMuPDF (fitz).

    Args:
        file_path (str): Path to the PDF file

    Returns:
        str: Extracted text
    """
    try:
        text = ""
        with fitz.open(file_path) as doc:
            for page in doc:
                text += page.get_text()
        return text
    except Exception as e:
        print(f"Error extracting text from PDF {file_path}: {e}")
        return ""

def load_cvs(directory: str) -> Dict[str, str]:
    """
    Load CVs from a directory.

    Args:
        directory (str): Directory containing CV files

    Returns:
        Dict[str, str]: Dictionary mapping CV IDs to their content
    """
    cvs = {}
    for filename in os.listdir(directory):
        if filename.endswith(('.docx', '.pdf')):
            file_path = os.path.join(directory, filename)
            
            # Extract ID from filename (assuming naming convention like cv_1.docx or 1.pdf)
            if filename.startswith('cv_') and filename.endswith('.docx'):
                cv_id = filename.replace('cv_', '').replace('.docx', '')
            elif filename.endswith('.pdf'):
                # For PDF files without ID in filename, use the filename without extension
                cv_id = filename.replace('.pdf', '')
            else:
                cv_id = filename.replace('.docx', '')
                
            cvs[cv_id] = extract_text(file_path)
    return cvs

def load_job_descriptions(directory: str) -> Dict[str, str]:
    """
    Load job descriptions from a directory.

    Args:
        directory (str): Directory containing job description files

    Returns:
        Dict[str, str]: Dictionary mapping job IDs to their descriptions
    """
    jobs = {}
    for filename in os.listdir(directory):
        if filename.endswith(('.docx', '.pdf')):
            file_path = os.path.join(directory, filename)
            
            # Extract ID from filename
            if filename.startswith('job_description_') and filename.endswith('.docx'):
                job_id = filename.replace('job_description_', '').replace('.docx', '')
            elif filename.endswith('.pdf'):
                # For PDF files, use the filename without extension
                job_id = filename.replace('.pdf', '')
            else:
                job_id = filename.replace('.docx', '')
                
            jobs[job_id] = extract_text(file_path)
    return jobs 