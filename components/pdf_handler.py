import streamlit as st
from PyPDF2 import PdfReader


def handle_pdf_upload():
    """
    Handles single or multiple PDF uploads with editable extraction.
    Returns tuple: (pdf_text, user_extra_prompt, summarize_clicked)

    - pdf_text: the current edited text (can be used for summary, quiz, explainer, etc.)
    - user_extra_prompt: user focus / custom instruction string
    - summarize_clicked: True only when the 'Summarize' button is pressed with valid text
    """
    uploaded_files = st.file_uploader(
        "📚 Upload your study material (PDF)",
        type=["pdf"],
        accept_multiple_files=True,
    )

    pdf_text = ""
    user_extra = ""

    if uploaded_files:
        with st.spinner("Extracting text from PDF(s)..."):
            try:
                combined_text = ""
                file_names = []

                for uploaded_file in uploaded_files:
                    reader = PdfReader(uploaded_file)
                    file_text = ""
                    for page in reader.pages:
                        file_text += page.extract_text() or ""

                    # Separator between multiple PDFs (optional)
                    if combined_text and file_text:
                        combined_text += "\n\n" + ("-" * 50) + "\n\n"

                    combined_text += file_text
                    file_names.append(
                        uploaded_file.name
                        if hasattr(uploaded_file, "name")
                        else "Unnamed PDF"
                    )

                pdf_text = combined_text

            except Exception as e:
                st.error(f"❌ Error reading PDF(s): {str(e)}")
                return None, None, False

        st.success("✅ PDF(s) processed successfully!")
        st.caption("Processed files: " + ", ".join(file_names))

        # 🔹 Use FULL extracted text as preview by default
        preview = pdf_text or ""
        last_names = tuple(file_names)

        # Reset raw/edited state if files changed or first upload
        if ("pdf_raw" not in st.session_state) or (
            st.session_state.get("last_upload_names") != last_names
        ):
            st.session_state["pdf_raw"] = pdf_text      # full text (all PDFs)
            st.session_state["pdf_edited"] = preview    # editable full text
            st.session_state["last_upload_names"] = last_names

        # ---------------- Editable Text Area ----------------
        st.markdown("### 📝 Review & Edit Extracted Text")
        st.text_area(
            "Edit extracted text below (review, trim, or add notes):",
            value=st.session_state.get("pdf_edited", preview),
            height=300,
            help="You can modify the text before summarizing or generating questions.",
            key="pdf_edited",
        )

        raw_len = len(st.session_state.get("pdf_raw", "").strip())
        edited_len = len(st.session_state.get("pdf_edited", "").strip())
        st.caption(
            f"Full extracted text (all PDFs combined): {raw_len} chars — "
            f"Current editable text: {edited_len} chars"
        )
        if raw_len < 50:
            st.info(
                "Text extraction is very short (<50 chars). "
                "Summarization will be blocked. Try another PDF or use OCR for scanned documents."
            )

        # ---------------- Extra Instructions ----------------
        st.markdown("### 🎯 Customization Options")
        user_extra = st.text_input(
            "Any specific focus? (e.g., 'Focus on applications', 'Make exam-ready', 'Explain with examples')",
            value=st.session_state.get("pdf_user_extra", ""),
            key="pdf_user_extra",
            placeholder="Leave empty for general summary or quiz generation",
            help="This will guide the AI on how to summarize or ask questions.",
        )

        # ---------------- Action Buttons ----------------
        col1, col2, col3 = st.columns(3)

        # Summarize button
        with col1:
            if st.button("🚀 Summarize", use_container_width=True, key="summarize_btn"):
                edited = st.session_state.get("pdf_edited", "").strip()
                raw = st.session_state.get("pdf_raw", "").strip()

                # Prefer the edited version if present
                text_to_summarize = edited or raw

                if text_to_summarize and len(text_to_summarize) >= 50:
                    # Return the text chosen for summarization
                    return text_to_summarize, user_extra, True
                else:
                    st.warning(
                        "⚠️ No valid text to summarize. Please upload valid PDF(s) "
                        "and ensure the extracted text is at least 50 characters."
                    )
                    return None, None, False

        # Clear button
        with col2:
            if st.button("🔄 Clear", use_container_width=True, key="clear_btn"):
                for k in ("pdf_raw", "pdf_edited", "last_upload_names", "pdf_user_extra"):
                    if k in st.session_state:
                        del st.session_state[k]
                st.rerun()

        # Default return when PDFs are uploaded but Summarize not clicked:
        # give the current edited text (for quiz/explainer/summarizer usage)
        return st.session_state.get("pdf_edited", preview), user_extra, False

    # No files uploaded
    return None, None, False
