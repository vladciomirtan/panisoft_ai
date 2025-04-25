# CV-Job Matching AI

This project uses AI to match CVs with job descriptions based on multiple criteria:

1. Industry Knowledge (10%)
2. Technical Skills and Qualifications (30%)
3. Job Description Match (60%)

## Project Structure

- `config.py` - Configuration settings
- `document_processor.py` - Functions to extract text from docx files
- `matcher.py` - Core matching logic using LangChain and DeepSeek AI
- `main.py` - Main application entry point
- `prompts.py` - System and user prompts
- `requirements.txt` - Required dependencies

## Setup

1. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Set your OpenRoute API key:
   - Edit `config.py` and add your API key directly
   - OR set the `OPENROUTE_API_KEY` environment variable

3. Ensure your data is in the correct structure:
   ```
   DataSet/
   ├── cv/ (contains CV .docx files)
   └── job_descriptions/ (contains job description .docx files)
   ```

## Usage

Run the main application:
```
python main.py
```

This will:
1. Load all CVs and job descriptions
2. Match each CV against each job description
3. Generate scores for each match based on the criteria
4. Save results to `matching_results.txt`
5. Display sample results in the console

## How It Works

The system uses LangChain with DeepSeek AI to:

1. Extract text from CV and job description files
2. Process each CV-job pair through a specialized prompt
3. Generate scores for each matching criterion
4. Calculate a weighted total score
5. Provide reasoning for the match
6. Rank candidates for each job based on their total score

## Customization

- Adjust weights in `config.py` to change the importance of each criterion
- Modify prompts in `prompts.py` to change how the AI evaluates matches
- Customize output format in `matcher.py` 