import os
from typing import Dict, List, Tuple
import numpy as np
from tqdm import tqdm
import requests
import json

from pydantic import BaseModel, Field

from config import (
    GEMINI_API_KEY,
    MODEL_NAME,
    TEMPERATURE,
    MAX_TOKENS,
    INDUSTRY_KNOWLEDGE_WEIGHT,
    TECHNICAL_SKILLS_WEIGHT,
    JOB_DESCRIPTION_MATCH_WEIGHT,
    GEMINI_MODEL
)
from document_processor import load_cvs, load_job_descriptions

class MatchResult(BaseModel):
    """Data model for match results."""
    industry_knowledge_score: float = Field(description="Score between 0 and 1 for industry knowledge")
    technical_skills_score: float = Field(description="Score between 0 and 1 for technical skills")
    job_description_match_score: float = Field(description="Score between 0 and 1 for overall job description match")
    total_score: float = Field(description="Weighted total score between 0 and 1")
    reasoning: str = Field(description="Reasoning for the scores")

class CVJobMatcher:
    """Class for matching CVs with job descriptions."""
    
    def __init__(self, api_key: str = None):
        """
        Initialize the CVJobMatcher with an API key.
        
        Args:
            api_key: API key to use (if None, will use the one from config)
        """
        self.api_key = api_key or GEMINI_API_KEY
        
        # Define the prompt template for matching
        self.system_prompt = """
        You are an AI expert in HR and talent acquisition. Your task is to analyze a CV and a job description, then determine how well the candidate matches the job requirements.
        
        You should evaluate based on three key criteria:
        1. Industry Knowledge (10%): Assess the candidate's experience in the specific industry relevant to the job.
        2. Technical Skills (30%): Evaluate the candidate's technical skills and qualifications against the job requirements.
        3. Overall Job Description Match (60%): Measure the overall alignment between the job description and the candidate's qualifications.
        
        For each criterion, assign a score between 0 and 1, where 0 means no match and 1 means perfect match.
        Calculate the weighted total score using the weights mentioned above.
        Provide detailed reasoning for your scores.
        
        Format your response as follows:
        INDUSTRY_KNOWLEDGE_SCORE: [score between 0 and 1]
        TECHNICAL_SKILLS_SCORE: [score between 0 and 1]
        JOB_DESCRIPTION_MATCH_SCORE: [score between 0 and 1]
        TOTAL_SCORE: [weighted total score between 0 and 1]
        
        REASONING:
        [Your detailed reasoning for the scores]
        """
        
    def match(self, cv_content: str, job_description: str) -> MatchResult:
        """
        Match a CV with a job description.
        
        Args:
            cv_content (str): Content of the CV
            job_description (str): Content of the job description
            
        Returns:
            MatchResult: The match result containing scores and reasoning
        """
        try:
            # Create the prompt with CV and job description
            user_content = f"""
            ## CV:
            {cv_content}
            
            ## Job Description:
            {job_description}
            
            Analyze the match between this CV and job description according to the criteria.
            """
            
            # Call Gemini API
            text = self._call_gemini_api(user_content)
            
            # Extract scores from the response
            lines = text.strip().split('\n')
            
            # Find the score lines 
            industry_score_line = next((line for line in lines if 'INDUSTRY_KNOWLEDGE_SCORE' in line), None)
            technical_score_line = next((line for line in lines if 'TECHNICAL_SKILLS_SCORE' in line), None)
            job_match_score_line = next((line for line in lines if 'JOB_DESCRIPTION_MATCH_SCORE' in line), None)
            total_score_line = next((line for line in lines if 'TOTAL_SCORE' in line), None)
            
            # Extract scores
            try:
                industry_score = float(industry_score_line.split(':')[1].strip()) if industry_score_line else 0.0
                technical_score = float(technical_score_line.split(':')[1].strip()) if technical_score_line else 0.0
                description_score = float(job_match_score_line.split(':')[1].strip()) if job_match_score_line else 0.0
                total = float(total_score_line.split(':')[1].strip()) if total_score_line else 0.0
                
                # Get the reasoning (everything after "REASONING:")
                reasoning_idx = text.find("REASONING:")
                reasoning = text[reasoning_idx + 10:] if reasoning_idx != -1 else "No reasoning provided."
                
                return MatchResult(
                    industry_knowledge_score=industry_score,
                    technical_skills_score=technical_score,
                    job_description_match_score=description_score,
                    total_score=total,
                    reasoning=reasoning.strip()
                )
            except Exception as e:
                print(f"Error parsing scores: {e}")
                print(f"Raw text: {text}")
                
                # Calculate fallback total if needed
                fallback_total = (
                    INDUSTRY_KNOWLEDGE_WEIGHT * (industry_score if 'industry_score' in locals() else 0.0) +
                    TECHNICAL_SKILLS_WEIGHT * (technical_score if 'technical_score' in locals() else 0.0) +
                    JOB_DESCRIPTION_MATCH_WEIGHT * (description_score if 'description_score' in locals() else 0.0)
                )
                
                return MatchResult(
                    industry_knowledge_score=industry_score if 'industry_score' in locals() else 0.0,
                    technical_skills_score=technical_score if 'technical_score' in locals() else 0.0,
                    job_description_match_score=description_score if 'description_score' in locals() else 0.0,
                    total_score=total if 'total' in locals() else fallback_total,
                    reasoning="Error parsing the scores. Raw response: " + text[:200] + "..."
                )
                
        except Exception as e:
            print(f"Error calling API: {e}")
            return MatchResult(
                industry_knowledge_score=0.0,
                technical_skills_score=0.0,
                job_description_match_score=0.0,
                total_score=0.0,
                reasoning=f"Error calling the API: {str(e)}"
            )
    
    def _call_gemini_api(self, user_content: str) -> str:
        """Call the Gemini API and return the response text."""
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={self.api_key}"
        
        headers = {
            'Content-Type': 'application/json'
        }
        
        # Combine system prompt and user content for Gemini
        combined_prompt = f"{self.system_prompt}\n\n{user_content}"
        
        data = {
            "contents": [{
                "parts": [{"text": combined_prompt}]
            }],
            "generationConfig": {
                "temperature": TEMPERATURE,
                "maxOutputTokens": MAX_TOKENS
            }
        }
        
        response = requests.post(url, headers=headers, data=json.dumps(data))
        
        if response.status_code != 200:
            raise Exception(f"Gemini API error: {response.status_code} - {response.text}")
        
        response_json = response.json()
        
        # Extract the text from the response
        try:
            return response_json["candidates"][0]["content"]["parts"][0]["text"]
        except KeyError:
            raise Exception(f"Unexpected Gemini API response format: {response_json}")
    
    def match_all(self, cvs: Dict[str, str], job_descriptions: Dict[str, str]) -> Dict[str, List[Tuple[str, MatchResult]]]:
        """
        Match all CVs with all job descriptions and return top matches for each job.
        
        Args:
            cvs (Dict[str, str]): Dictionary of CV IDs to CV content
            job_descriptions (Dict[str, str]): Dictionary of job description IDs to job description content
            
        Returns:
            Dict[str, List[Tuple[str, MatchResult]]]: Dictionary mapping job IDs to list of (CV ID, match result) tuples
        """
        results = {}
        
        total_comparisons = len(cvs) * len(job_descriptions)
        progress = tqdm(total=total_comparisons, desc="Matching CVs with Jobs")
        
        for job_id, job_desc in job_descriptions.items():
            job_results = []
            
            for cv_id, cv_content in cvs.items():
                match_result = self.match(cv_content, job_desc)
                job_results.append((cv_id, match_result))
                progress.update(1)
            
            # Sort by total score in descending order
            job_results.sort(key=lambda x: x[1].total_score, reverse=True)
            results[job_id] = job_results
        
        progress.close()
        return results

def format_top_matches(matches: Dict[str, List[Tuple[str, MatchResult]]], top_n: int = 5) -> str:
    """
    Format the top matches for each job in a readable format.
    
    Args:
        matches (Dict[str, List[Tuple[str, MatchResult]]]): The matches for each job
        top_n (int): Number of top matches to include
        
    Returns:
        str: Formatted string of top matches
    """
    output = []
    
    for job_id, job_matches in matches.items():
        output.append(f"## Job: {job_id}")
        output.append("Top matches:")
        
        for i, (cv_id, result) in enumerate(job_matches[:top_n]):
            output.append(f"{i+1}. {cv_id} - Score: {result.total_score:.2f}")
            output.append(f"   Industry: {result.industry_knowledge_score:.2f} | Technical: {result.technical_skills_score:.2f} | Match: {result.job_description_match_score:.2f}")
            output.append(f"   Reasoning: {result.reasoning[:150]}...")  # Truncate reasoning for readability
            output.append("")
        
        output.append("-" * 80)
    
    return '\n'.join(output) 