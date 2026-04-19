# core/ai_utils.py
#Handles API selection, loading keys, and LLM initialization.
import os
from dotenv import load_dotenv
from openai import OpenAI
import google.generativeai as genai

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def get_llm_client(api_choice="OpenAI"):
    """Initialize and return LLM client based on user choice."""
    if api_choice == "OpenAI":
        if not OPENAI_API_KEY:
            raise ValueError("❌ Missing OpenAI API Key in .env")
        client = OpenAI(api_key=OPENAI_API_KEY)
        return client, "OpenAI"
    elif api_choice == "Gemini":
        if not GEMINI_API_KEY:
            raise ValueError("❌ Missing Gemini API Key in .env")
        genai.configure(api_key=GEMINI_API_KEY)
        return genai, "Gemini"
    else:
        raise ValueError("Invalid API choice. Use 'OpenAI' or 'Gemini'.")

print("🔑 OpenAI key loaded:", bool(os.getenv("OPENAI_API_KEY")))
print(os.getenv("OPENAI_API_KEY"))
print("🔑 Gemini key loaded:", bool(os.getenv("GEMINI_API_KEY")))
print(os.getenv("GEMINI_API_KEY"))