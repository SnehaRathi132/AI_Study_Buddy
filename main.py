import streamlit as st
from components.sidebar import sidebar_ui
from components.chat_ui import chat_ui
from components.pdf_handler import handle_pdf_upload

st.set_page_config(page_title="StudyBuddy", page_icon="🧠", layout="wide")

# ---------------- SESSION STATE INIT ----------------
if "pdf_content" not in st.session_state:
    # This is what chat_ui will read
    st.session_state["pdf_content"] = ""
if "user_focus" not in st.session_state:
    st.session_state["user_focus"] = ""

# ---------------- SIDEBAR: MODE SELECTION ----------------
selected_mode, selected_sub_mode = sidebar_ui()

# ---------------- HEADER ----------------
st.title("🧠 StudyBuddy - Your Smart Study Assistant")

# ---------------- PDF HANDLER ----------------
st.markdown("### 📚 Upload a PDF")

# handle_pdf_upload returns: (pdf_text, user_extra_prompt, summarize_clicked)
pdf_text, user_focus, summarize_clicked = handle_pdf_upload()

# ✅ Always store the current edited PDF text (if any) into session_state
# so Summarizer/Quizzer can detect it via st.session_state["pdf_content"]
if pdf_text:
    st.session_state["pdf_content"] = pdf_text

# Only overwrite user_focus if handler returned a value (None means "no change")
if user_focus is not None:
    st.session_state["user_focus"] = user_focus

# Optional UX: show success message when user explicitly clicks "Summarize"
if summarize_clicked and pdf_text:
    st.divider()
    st.success("✅ PDF loaded! You can now chat, summarize, or generate questions from this PDF.")

st.divider()

# ---------------- CHAT UI ----------------
# chat_ui internally reads st.session_state["pdf_content"] and ["user_focus"]
chat_ui(selected_mode, selected_sub_mode)
