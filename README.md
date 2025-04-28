# CV-Job Matching AI

This project uses AI to match CVs with job descriptions based on multiple criteria:

1. Industry Knowledge (10%)
2. Technical Skills and Qualifications (30%)
3. Job Description Match (60%)

## Project Structure

- `config.py` - Configuration settings and API keys
- `document_processor.py` - Functions to extract text from docx files
- `matcher.py` - Core matching logic using Google's Gemini API
- `main.py` - Batch processing of all CVs against all job descriptions
- `job_cv_matcher.py` - Match a specific job against multiple CVs
- `cv_job_matcher.py` - Match a specific CV against multiple job descriptions
- `chat_interface.py` - Interactive interface for one-to-one matching
- `prompts.py` - System prompts for the AI
- `requirements.txt` - Required dependencies

## Setup

1. Inside the project folder, install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Set your Gemini API key:
   - Edit `config.py` and add your API key directly
   - OR set the `GEMINI_API_KEY` environment variable
   - OR create a `.env` file with `GEMINI_API_KEY=your_key_here`

3. Ensure your data is in the correct structure:
   ```
   DataSet/
   ├── cv/ (contains CV .docx files)
   └── job_descriptions/ (contains job description .docx files)
   ```

# Usage
## Grapical Interface
To enter the graphical interface, first change the current directory to `panisoft_ai\interface`. Your parent directory may differ, so take that into consideration:
```
cd D:\Documents\panisoft_ai\interface
```
Run the application `app.py`:
```
python app.py
```
## Command line tools
### Full Batch Processing
Run the main application to process all CVs against all job descriptions:
```
python main.py
```

### Match a Specific Job to CVs
Find the best CVs for a specific job:
```
python job_cv_matcher.py
```

### Match a Specific CV to Jobs
Find the best jobs for a specific CV:
```
python cv_job_matcher.py
```

### Interactive Chat Interface
Use the chat interface for guided matching:
```
python chat_interface.py
```

## How It Works

The system uses Google's Gemini AI to:

1. Extract text from CV and job description files
2. Process each CV-job pair through a specialized prompt
3. Generate scores for each matching criterion
4. Calculate a weighted total score
5. Provide detailed reasoning for the match
6. Rank candidates for each job or jobs for each candidate based on total score

## Customization

- Adjust weights in `config.py` to change the importance of each criterion
- Modify prompts in `prompts.py` to change how the AI evaluates matches
- Customize output format in `matcher.py`
- Adjust the Gemini model in `config.py` (gemini-2.0-flash or gemini-2.0-pro) 