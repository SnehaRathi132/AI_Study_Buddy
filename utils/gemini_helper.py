import os
from dotenv import load_dotenv
import google.generativeai as genai

# ------------------ LOAD ENV & CONFIGURE GEMINI ------------------

# Load local .env for development (won't affect deployed env vars)
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

api_configured = False
_config_error = ""

if GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        api_configured = True
    except Exception as e:
        _config_error = str(e)
        api_configured = False
else:
    _config_error = "GEMINI_API_KEY not set in environment."

MODEL = "models/gemini-2.5-flash"


def generate_response(prompt: str) -> str:
    """
    Low-level helper to talk to the Gemini model.

    Returns:
        - Model text response on success.
        - A helpful error string if configuration or API call fails.
    """
    if not api_configured:
        return (
            "❌ Gemini API not configured. Set GEMINI_API_KEY as an environment variable "
            "or in Streamlit secrets. Details: " + _config_error
        )

    try:
        model = genai.GenerativeModel(MODEL)
        response = model.generate_content(prompt)
        return response.text.strip() if response and getattr(response, "text", None) else "⚠️ No response generated."
    except Exception as e:
        return f"❌ Error generating response: {e}"


# ------------------ HIGH-LEVEL STUDY BUDDY HELPERS ------------------


def generate_questions(text: str, previous_context: str = "") -> str:
    """
    Generate a theory-focused quiz based strictly on the given source text.

    Default behavior:
    - Only theory / conceptual questions (no MCQs).
    - MCQs appear ONLY if explicitly requested in `previous_context`
      (e.g., mentions of "MCQ", "multiple choice", "options A-D", etc.).
    """
    prompt = f"""
You are Study Buddy, an academic quiz generator for exam preparation.

IMPORTANT RULES:
- Use ONLY the following SOURCE MATERIAL to create questions.
- Do NOT invent new topics or rely on generic outside knowledge.
- If the source is about topic X, ALL questions must be about topic X.
- Do NOT switch to unrelated topics like "Effective Study Strategies"
  unless that exact content clearly appears in the source text.

SOURCE MATERIAL:
{text}

Additional user instructions (style/tone; may mention MCQs):
{previous_context}

DEFAULT QUESTION BEHAVIOR (VERY IMPORTANT):
- By default, generate ONLY **theory / conceptual questions**.
- DO NOT create Multiple Choice Questions (MCQs) unless the user explicitly asks for:
  "MCQs", "multiple choice", "objective with options", "A–D options", etc.
- If such an explicit request appears in the additional instructions,
  you may include some MCQs with options A–D.

Question types (theory-first):
- Short descriptive / theoretical questions.
- Longer descriptive / explain-the-concept questions.
- OPTIONAL: MCQs with options A–D ONLY IF explicitly requested.

Restrictions:
- DO NOT create numerical / calculation-based problems unless such examples
  are explicitly present in the source material.
- DO NOT add generic study tips, time-management advice, or life-skill content
  unless it actually appears in the source text.

Formatting:
- Number every question in order: 1., 2., 3., ...
- Do NOT show the correct answer immediately after each question.
- After ALL questions, provide a numbered **Answer Key** listing each answer
  (e.g., "1. True", "2. Photosynthesis", "3. B", ...).
- Make the formatting clean so a student can first attempt, then check the answers.
"""
    return generate_response(prompt.strip())



def solve_questions(user_questions: str, previous_context: str = "", word_limit: int = 100) -> str:
    """
    Solve exam-style questions.

    - Detects the type/length of answer needed implicitly.
    - `word_limit` is available if you want to enforce a general cap externally.
    """
    prompt = f"""
You are Study Buddy, a question-solving AI.

Questions:
{user_questions}

Recent context (may include syllabus level, exam type, etc.):
{previous_context}

Instructions:
- For each question, first understand what type it is:
  • Very short answer (objective, 0.5–1 mark): 25–40 words or 1–2 sentences.
  • Short answer (2–3 marks): roughly 90–130 words; mention diagrams if relevant.
  • Long answer (4–5 marks): roughly 160–220 words; use stepwise explanation and structured points.
- If the user explicitly gives a word limit or mark value, follow that over the general guideline.
- Number all answers to match the question numbers.
- Use Markdown formatting:
  • **Bold** for key terms.
  • Bullet points / steps where helpful.
  • If a diagram would help, describe it in text (no actual image needed).
"""
    # word_limit is not strictly enforced inside the prompt but can be used by caller if needed.
    return generate_response(prompt.strip())


def evaluate_answers(questions: str, user_answers: str, previous_context: str = "") -> str:
    """
    Evaluate user's answers against the given questions.

    Returns structured feedback, correctness, marks, and improvement tips.
    """
    prompt = f"""
You are Study Buddy, an exam answer evaluator.

Questions:
{questions}

User's Answers:
{user_answers}

Recent chat / context:
{previous_context}

Instructions:
- For each question:
  • Indicate if the answer is correct, partially correct, or incorrect.
  • Point out specific missing facts, definitions, keywords, or examples.
  • Give a short, improved model answer or key points if needed.
  • Assign a reasonable score (e.g., out of 1, 3, 5 marks) based on depth and accuracy.
- Use clear, numbered feedback aligned with the question numbers.
- At the end, give a brief summary of:
  • Overall strengths (what the student is doing well).
  • Main improvement areas (what to focus on next).
- Keep feedback concise but specific and helpful.
"""
    return generate_response(prompt.strip())
