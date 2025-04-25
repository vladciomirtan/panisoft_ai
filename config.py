import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# API Key configuration
OPENROUTE_API_KEY = os.getenv("OPENROUTE_API_KEY", "")

# Model configuration
MODEL_NAME = "deepseek/deepseek-v3-base:free"
TEMPERATURE = 0.3
MAX_TOKENS = 4096

# Path configuration
CV_DIR = "DataSet/cv"
JOB_DESCRIPTIONS_DIR = "DataSet/job_descriptions"

# Scoring weights
INDUSTRY_KNOWLEDGE_WEIGHT = 0.1
TECHNICAL_SKILLS_WEIGHT = 0.3
JOB_DESCRIPTION_MATCH_WEIGHT = 0.6 