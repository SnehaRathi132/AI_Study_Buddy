# AI Study Buddy

AI Study Buddy is a Streamlit-based learning assistant that helps you understand topics faster, summarize study material, and practice with exam-style questions using Google Gemini.

## Why This Project
- Turn long notes into concise revision points.
- Explain difficult concepts in student-friendly language.
- Practice with generated questions and answer feedback.
- Keep everything in one simple web app.

## Features
- `Explainer`
  - Explains concepts step by step in clear, exam-oriented language.
- `Summarizer`
  - Extracts text from uploaded PDFs.
  - Creates structured summaries for quick revision.
- `Quizzer`
  - Generates questions from your PDF or a custom prompt.
  - Supports solving and evaluating answers with feedback.

## Tech Stack
- Python
- Streamlit
- Google Gemini API (`google-generativeai`)
- `python-dotenv`
- `PyPDF2`
- `langchain`

## Project Structure
```text
AI_StudyBuddy-main/
  components/
    chat_ui.py              # Main chat and interaction UI
    pdf_handler.py          # PDF upload + extraction pipeline
    sidebar.py              # Mode and sub-mode selectors
  core/
    explainer.py            # Concept explanation logic
    summarizer.py           # Summarization logic
    quizzer.py              # Question generation and evaluation
    ai_utils.py             # Shared AI helper logic
  utils/
    gemini_helper.py        # Gemini model integration helpers
  main.py                   # Streamlit app entry point
  requirements.txt
  README.md
```

## Prerequisites
- Python 3.10+
- A Google Gemini API key

## Local Setup
1. Clone the repository:
```bash
git clone https://github.com/SnehaRathi132/AI_Study_Buddy.git
cd AI_Study_Buddy
```

2. Create and activate a virtual environment:

Windows (PowerShell):
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

macOS/Linux:
```bash
python -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root:
```env
GEMINI_API_KEY=your_api_key_here
```

5. Run the app:
```bash
streamlit run main.py
```

6. Open the URL shown in your terminal (typically `http://localhost:8501`).

## How To Use
1. Choose a mode from the sidebar (`Explainer`, `Summarizer`, `Quizzer`).
2. Upload a PDF if you want PDF-based learning.
3. Add a custom focus prompt (optional).
4. Ask questions, generate summaries, or practice quizzes.

## Troubleshooting
- `ModuleNotFoundError`: Activate your virtual environment and reinstall dependencies.
- API errors: Verify `GEMINI_API_KEY` in `.env`.
- Empty/poor summaries: Ensure uploaded PDFs contain selectable text (not only scanned images).

## Security Notes
- Never commit `.env` or API keys.
- Rotate your API key if it is exposed accidentally.

## Future Improvements
- Topic-wise quiz difficulty levels
- Progress tracking and saved sessions
- Better handling for scanned PDFs (OCR)

## License
Add a license file (for example, MIT) if you plan to distribute this project publicly.
