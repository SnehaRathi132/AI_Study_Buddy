import streamlit as st
import time
def sidebar_ui():
    """Sidebar with mode and Quizzer sub-mode selectors, and core controls."""

    # Mode selection
    st.sidebar.markdown("### 🧩 Choose Mode")
    mode = st.sidebar.radio(
        "Select a core function:",
        ["💡 Explainer", "📰 Summarizer", "🧩 Quizzer"],
        index=0
    )

    # Nested radio for Quizzer
    sub_mode = None
    if mode == "🧩 Quizzer":
        st.sidebar.markdown("### ✨ Quizzer Action")
        sub_mode = st.sidebar.radio(
            "Choose Quizzer action:",
            [
                "📝 Generate Questions",
                "📖 Solve Questions",
                "✅ Evaluate Answers"
            ],
            index=0
        )

    st.sidebar.markdown("---")
    if st.sidebar.button("🆕 New Chat"):
        st.session_state.messages = []
        # Success message that auto-disappears after 2 seconds
        success_placeholder = st.sidebar.empty()
        with success_placeholder.container():
            st.success("Started a new chat!")
        time.sleep(2)
        success_placeholder.empty()

    st.sidebar.markdown("---")


    return mode, sub_mode
