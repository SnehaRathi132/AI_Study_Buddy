import streamlit as st
from core.explainer import explain_concept
from core.summarizer import summarize_text
from core.quizzer import (
    generate_questions,
    solve_questions,
    evaluate_answers
)


def get_previous_messages_summary(messages, limit=3):
    context_messages = messages[-2 * limit:]
    return "\n".join(f"{m['role'].capitalize()}: {m['content']}" for m in context_messages)


def chat_ui(selected_mode, selected_sub_mode=None):
    """Main chat interface with mode and optional sub-mode for Quizzer."""

    # Build subheader dynamically
    if selected_sub_mode:
        st.subheader(f"💬 StudyBuddy Chat — {selected_mode} | {selected_sub_mode}")
    else:
        st.subheader(f"💬 StudyBuddy Chat — {selected_mode}")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Render previous messages
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat input
    prompt = st.chat_input("Type your message…")
    if not prompt:
        return

    # Store user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    previous_context = get_previous_messages_summary(
        st.session_state.messages[:-1], limit=3
    )
    assistant_response = ""

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        try:
            with st.spinner("💡 Study Buddy is thinking…"):

                # ---------------- EXPLAINER MODE ----------------
                if selected_mode == "💡 Explainer":
                    assistant_response = explain_concept(prompt, previous_context)

                # ---------------- SUMMARIZER MODE ----------------
                elif selected_mode == "📰 Summarizer":
                    # ✅ Read from session_state (set by handle_pdf_upload)
                    pdf = st.session_state.get("pdf_content", "")
                    user_focus = st.session_state.get("user_focus", "")

                    p = prompt.strip()
                    first_word = p.split()[0].lower() if p else ""
                    is_short = len(p.split()) <= 12
                    is_question = p.endswith("?") or first_word in (
                        "what",
                        "why",
                        "how",
                        "when",
                        "which",
                        "who",
                        "where",
                        "explain",
                        "describe",
                    )
                    is_followup = bool(p) and (is_short or is_question)

                    if pdf:  # ✅ PDF detected
                        if is_followup:
                            extra = (
                                f"Follow-up question: {p}. "
                                f"Use the previous assistant response and the PDF content to answer concisely."
                            )
                        else:
                            extra = p or user_focus

                        assistant_response = summarize_text(
                            text=pdf,
                            previous_context=previous_context,
                            user_focus=user_focus,
                            extra_instruction=extra,
                        )
                    else:
                        # No PDF loaded — summarize the user's prompt directly
                        assistant_response = summarize_text(p, previous_context)

                # ---------------- QUIZZER MODE ----------------
                elif selected_mode == "🧩 Quizzer":
                    # Generate theory questions (prefer PDF content)
                    if selected_sub_mode == "📝 Generate Questions":
                        pdf = st.session_state.get("pdf_content", "")
                        user_focus = st.session_state.get("user_focus", "")

                        if pdf:
                            st.info(
                                "Using the uploaded PDF as the source material. "
                                "Your message will be treated as extra instructions "
                                "(e.g., exam level, chapter focus, question style)."
                            )
                            # Build context for style / guidance ONLY
                            extra_context_parts = [
                                previous_context.strip(),
                                user_focus.strip(),
                                f"Extra instruction from user: {prompt.strip()}",
                            ]
                            extra_context = "\n".join(
                                [part for part in extra_context_parts if part]
                            )
                            assistant_response = generate_questions(
                                pdf, extra_context
                            )
                        else:
                            st.info(
                                "No PDF detected. Questions will be generated directly "
                                "from your message content."
                            )
                            # Fallback: treat the prompt itself as the source text
                            assistant_response = generate_questions(
                                prompt, previous_context
                            )

                    # Solve questions
                    elif selected_sub_mode == "📖 Solve Questions":
                        st.info(
                            "Paste your exam questions here. "
                            "If specifying marks/word range, include this in each question."
                        )
                        assistant_response = solve_questions(
                            prompt, previous_context
                        )

                    # Evaluate answers
                    elif selected_sub_mode == "✅ Evaluate Answers":
                        st.info(
                            "Paste questions and answers in the format:\n\n"
                            "Questions here...\n"
                            "---\n"
                            "Answers here..."
                        )
                        try:
                            qs_ans = prompt.split("---")
                            questions = qs_ans[0].strip()
                            answers = qs_ans[1].strip() if len(qs_ans) > 1 else ""
                            if not answers:
                                assistant_response = (
                                    "⚠️ Please provide both questions and answers, "
                                    "separated by a line with `---`."
                                )
                            else:
                                assistant_response = evaluate_answers(
                                    questions, answers, previous_context
                                )
                        except Exception as e:
                            assistant_response = (
                                "⚠️ Could not parse your input. Make sure you separate "
                                "questions and answers with a line containing `---`.\n\n"
                                f"Error details: {e}"
                            )
                    else:
                        assistant_response = "⚠️ Unknown Quizzer sub-mode."

                # ---------------- UNKNOWN MODE ----------------
                else:
                    assistant_response = "⚠️ Unknown mode selected."
        except Exception as e:
            assistant_response = (
                "❌ Sorry, there was an error processing your request. "
                "Please try again in a few seconds.\n\n"
                f"Error: {str(e)}"
            )

        # Show assistant response
        response_placeholder.markdown(assistant_response)

        # (Optional) also show raw markdown code – you can remove this if you don't want it
        st.code(assistant_response, language="markdown")

        # Feedback buttons
        st.markdown("**Was this response helpful?**")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("👍 Helpful", key=f"fb_yes_{len(st.session_state.messages)}"):
                st.success("Thank you for your feedback!")
        with col2:
            if st.button("👎 Not Helpful", key=f"fb_no_{len(st.session_state.messages)}"):
                st.info(
                    "We appreciate your input! Please let us know how we can improve."
                )

    # Store assistant message
    st.session_state.messages.append(
        {"role": "assistant", "content": assistant_response}
    )
