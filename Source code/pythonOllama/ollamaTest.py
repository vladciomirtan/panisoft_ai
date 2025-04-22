import requests
import json

# Example job description (you can replace these with real data)
job_data = {
    "job_title": "Senior Backend Developer",
    "company_description": [
        "Tech-focused startup", "Remote-first culture", "Fast-paced and innovative"
    ],
    "job_description": [
        "Develop RESTful APIs", "Optimize database performance", "Ensure code quality and test coverage"
    ],
    "required_qualifications": [
        "5+ years of backend experience", "Proficient in Python and Django", "Experience with PostgreSQL"
    ],
    "preferred_skills": [
        "Familiarity with Docker and Kubernetes", "Understanding of CI/CD pipelines", "Knowledge of microservices architecture"
    ],
    "benefits": [
        "Flexible schedule", "Equity options", "Annual learning stipend"
    ]
}

# Format the job description as a prompt
job_prompt = "\n".join([
    f"Job Title: {job_data['job_title']}",
    "\nCompany Description:\n- " + "\n- ".join(job_data["company_description"]),
    "\nJob Description:\n- " + "\n- ".join(job_data["job_description"]),
    "\nRequired Qualifications:\n- " + "\n- ".join(job_data["required_qualifications"]),
    "\nPreferred Skills:\n- " + "\n- ".join(job_data["preferred_skills"]),
    "\nBenefits:\n- " + "\n- ".join(job_data["benefits"]),
])

# Build the prompt for Ollama
prompt = f"""
Extract 10–20 relevant skills, technologies, or preferences from the following job description.
Return a JSON list in this format:
[{{"skill": "Skill Name", "importance": 1-10}}]

Job Description:
{job_prompt}
"""

# Send the prompt to Ollama's local API
response = requests.post(
    "http://localhost:11434/api/generate",
    json={
        "model": "mistral",
        "prompt": prompt,
        "stream": False
    }
)

# Extract and print the result
text_output = response.json().get("response", "")
try:
    skills = json.loads(text_output)
    print("\nExtracted Skills and Importance Scores:")
    for s in skills:
        print(f"{s['skill']}: {s['importance']}")
except json.JSONDecodeError:
    print("Failed to parse JSON. Raw output:\n", text_output)
