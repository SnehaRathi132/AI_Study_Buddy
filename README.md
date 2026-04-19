# AI Study Buddy

AI Study Buddy is a Streamlit app that helps students study faster with Gemini-powered learning tools.

## Features
- `Explainer`: explains concepts in simple, exam-friendly language.
- `Summarizer`: summarizes uploaded PDF notes/content into structured revision points.
- `Quizzer`:
  - generate questions from uploaded PDF or prompt text
  - solve exam-style questions
  - evaluate answers with feedback

## Tech Stack
- Python
- Streamlit
- Google Gemini API (`google-generativeai`)
- PyPDF2

## Project Structure
```text
AI_StudyBuddy-main/
  components/   # UI and PDF upload handlers
  core/         # explainer, summarizer, quiz logic
  utils/        # Gemini API helper
  main.py       # app entry point
```

## Setup
1. Clone the repository:
```bash
git clone https://github.com/SnehaRathi132/AI_Study_Buddy.git
cd AI_Study_Buddy
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
# Windows PowerShell
venv\Scripts\Activate.ps1
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Add environment variables in `.env`:
```env
GEMINI_API_KEY=your_api_key_here
```

5. Run the app:
```bash
streamlit run main.py
```

## Notes
- Do not commit your `.env` file or API keys.
- If text is too short, the summarizer asks for longer content.
