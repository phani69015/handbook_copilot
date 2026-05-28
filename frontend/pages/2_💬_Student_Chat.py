"""Student Chat - Enter college code and ask questions."""

import os

import httpx
import streamlit as st

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(page_title="Student Chat", page_icon="💬", layout="wide", initial_sidebar_state="collapsed")

# Hide sidebar completely
st.markdown(
    """
    <style>
    [data-testid="stSidebar"] { display: none; }
    [data-testid="stSidebarNav"] { display: none; }
    [data-testid="collapsedControl"] { display: none; }
    </style>
    """,
    unsafe_allow_html=True,
)

# Initialize session state
if "student_college" not in st.session_state:
    st.session_state.student_college = None

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

# ─── College Code Entry ──────────────────────────────────────
if not st.session_state.student_college:
    # Navigation bar
    col_nav1, col_nav2, col_nav3 = st.columns([1, 1, 4])
    with col_nav1:
        st.page_link("streamlit_app.py", label="← Home", icon="🏠")
    with col_nav2:
        st.page_link("pages/1_🏫_Register_College.py", label="Register College", icon="🏫")

    st.title("💬 Student Chat")
    st.markdown("Enter your college code to start asking questions about the handbook.")
    st.markdown("---")

    with st.form("college_code_form"):
        code = st.text_input(
            "College Code",
            placeholder="e.g., SPC-a3b2",
            help="Get this code from your college administration.",
        )
        entered = st.form_submit_button("Enter Chat", type="primary")

    if entered and code:
        try:
            response = httpx.get(f"{BACKEND_URL}/colleges/{code}", timeout=5.0)
            if response.status_code == 200:
                data = response.json()
                if not data["is_indexed"]:
                    st.error(
                        "This college's handbook hasn't been uploaded yet. "
                        "Please ask your administrator to upload it."
                    )
                else:
                    st.session_state.student_college = data
                    st.session_state.chat_messages = []
                    st.rerun()
            else:
                st.error("Invalid code. Please check with your college administration.")
        except httpx.ConnectError:
            st.error("Cannot connect to the service. Please try again later.")
        except Exception as e:
            st.error(f"Error: {e}")

else:
    # ─── Chat Interface ──────────────────────────────────────
    college = st.session_state.student_college
    college_code = college["college_code"]
    college_name = college["college_name"]

    # Top navigation bar
    col_nav1, col_nav2, col_nav3, col_nav4 = st.columns([1, 1, 1, 3])
    with col_nav1:
        st.page_link("streamlit_app.py", label="Home", icon="🏠")
    with col_nav2:
        if st.button("🔄 Switch College"):
            st.session_state.student_college = None
            st.session_state.chat_messages = []
            st.rerun()
    with col_nav3:
        if st.button("🗑️ Clear Chat"):
            st.session_state.chat_messages = []
            st.rerun()

    # Header
    st.title(f"💬 {college_name}")
    st.caption(f"Ask questions about your college handbook | Code: `{college_code}`")
    st.markdown("---")

    # Display chat history
    for message in st.session_state.chat_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message.get("citations"):
                with st.expander("📄 Sources"):
                    for citation in message["citations"]:
                        st.markdown(
                            f"- **{citation['section']}** (Page {citation['page']}) "
                            f"— Relevance: {citation['relevance_score']:.0%}"
                        )

    # Chat input
    if prompt := st.chat_input("Ask a question about the handbook..."):
        # Display user message
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Call backend
        with st.chat_message("assistant"):
            with st.spinner("Searching handbook..."):
                try:
                    response = httpx.post(
                        f"{BACKEND_URL}/colleges/{college_code}/query",
                        json={"question": prompt},
                        timeout=120.0,
                    )

                    if response.status_code == 200:
                        data = response.json()
                        answer = data["answer"]
                        citations = data.get("citations", [])
                        chunks_used = data.get("chunks_used", 0)
                        confidence = data.get("confidence", 0)

                        st.markdown(answer)

                        # Show metadata
                        col1, col2 = st.columns(2)
                        with col1:
                            st.caption(f"Chunks used: {chunks_used}")
                        with col2:
                            st.caption(f"Confidence: {confidence:.0%}")

                        # Show citations
                        if citations:
                            with st.expander("📄 Sources"):
                                for citation in citations:
                                    st.markdown(
                                        f"- **{citation['section']}** (Page {citation['page']}) "
                                        f"— Relevance: {citation['relevance_score']:.0%}"
                                    )

                        # Store in history
                        st.session_state.chat_messages.append({
                            "role": "assistant",
                            "content": answer,
                            "citations": citations,
                        })
                    else:
                        error_detail = "Unknown error"
                        try:
                            error_detail = response.json().get("detail", error_detail)
                        except Exception:
                            pass
                        error_msg = f"Error: {error_detail}"
                        st.error(error_msg)
                        st.session_state.chat_messages.append({
                            "role": "assistant",
                            "content": error_msg,
                        })

                except httpx.ConnectError:
                    error_msg = "Cannot connect to the service. Please try again later."
                    st.error(error_msg)
                    st.session_state.chat_messages.append({
                        "role": "assistant",
                        "content": error_msg,
                    })
                except httpx.ReadTimeout:
                    error_msg = (
                        "The request timed out. The AI model may be loading. "
                        "Please try again in a moment."
                    )
                    st.error(error_msg)
                    st.session_state.chat_messages.append({
                        "role": "assistant",
                        "content": error_msg,
                    })
