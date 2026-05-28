"""Register College - Admin page with invite code gate and OpenAI key option."""

import os

import httpx
import streamlit as st

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(page_title="Register College", page_icon="🏫", layout="wide", initial_sidebar_state="collapsed")

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

# Navigation bar
col_nav1, col_nav2, col_nav3 = st.columns([1, 1, 4])
with col_nav1:
    st.page_link("streamlit_app.py", label="← Home", icon="🏠")
with col_nav2:
    st.page_link("pages/2_💬_Student_Chat.py", label="Student Chat", icon="💬")

st.title("🏫 Register Your College")
st.markdown("Register your institution and upload the student handbook to get started.")
st.markdown("---")

# Initialize session state
if "registered_college" not in st.session_state:
    st.session_state.registered_college = None

if "ingestion_done" not in st.session_state:
    st.session_state.ingestion_done = False

# ─── Registration Form (with invite code + optional OpenAI key) ────
st.markdown("### Register New College")
st.markdown(
    "You need an **invite code** from the platform administrator to register. "
    "This ensures only authorized college staff can register."
)

with st.form("register_form"):
    invite_code = st.text_input(
        "Invite Code *",
        placeholder="e.g., INV-a8f3c2",
        help="Contact the platform administrator to get an invite code.",
    )

    college_name = st.text_input(
        "College Name *",
        placeholder="e.g., St. Paul's College, Kalamassery",
        help="Enter the full official name of your college.",
    )

    st.markdown("---")
    st.markdown("**Optional: OpenAI API Key** (for faster AI responses)")
    st.caption(
        "If provided, student queries will use OpenAI GPT-4o (~1-2s responses) "
        "instead of the local model (~5-10s). The key is stored securely on the server "
        "and is never visible to students."
    )

    openai_key = st.text_input(
        "OpenAI API Key (optional)",
        placeholder="sk-...",
        type="password",
        help="Get one at https://platform.openai.com/api-keys",
    )

    submitted = st.form_submit_button("Register College", type="primary")

if submitted:
    if not invite_code:
        st.error("Invite code is required.")
    elif not college_name:
        st.error("College name is required.")
    elif len(college_name) < 3:
        st.error("College name must be at least 3 characters.")
    else:
        try:
            response = httpx.post(
                f"{BACKEND_URL}/colleges/register",
                json={
                    "college_name": college_name,
                    "invite_code": invite_code,
                    "openai_api_key": openai_key,
                },
                timeout=10.0,
            )
            if response.status_code == 200:
                data = response.json()
                st.session_state.registered_college = data
                st.session_state.ingestion_done = False
                st.success(
                    f"College registered! Your unique access code is: **`{data['college_code']}`**"
                )
                if data.get("has_openai_key"):
                    st.info("🚀 OpenAI key configured — students will get faster responses.")
            elif response.status_code == 403:
                st.error(
                    "Invalid or already used invite code. "
                    "Please contact the platform administrator for a new one."
                )
            else:
                st.error(f"Registration failed: {response.json().get('detail', 'Unknown error')}")
        except httpx.ConnectError:
            st.error("Cannot connect to backend. Is the service running?")
        except Exception as e:
            st.error(f"Error: {e}")

# Show registered college info
if st.session_state.registered_college:
    college = st.session_state.registered_college
    st.markdown("---")

    st.markdown("### Your College Details")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("College Name", college["college_name"])
    with col2:
        st.metric("Access Code", college["college_code"])
    with col3:
        openai_status = "🚀 Enabled" if college.get("has_openai_key") else "⚪ Not set"
        st.metric("OpenAI", openai_status)

    st.info(
        f"Share this code with your students: **`{college['college_code']}`** — "
        "they'll use it to access the handbook chat."
    )

    # ─── Upload Handbook ─────────────────────────────────────
    st.markdown("---")
    st.markdown("### Upload Student Handbook PDF")

    uploaded_file = st.file_uploader(
        "Drop your handbook PDF here",
        type=["pdf"],
        help="Upload the student handbook. We'll index it for AI-powered search.",
        key="handbook_upload",
    )

    if uploaded_file is not None:
        st.info(f"📄 {uploaded_file.name} ({uploaded_file.size / (1024*1024):.1f} MB)")

        col1, col2 = st.columns([1, 3])
        with col1:
            force_reindex = st.checkbox("Force re-index", value=False)

        if st.button("🚀 Upload & Index Handbook", type="primary"):
            with st.spinner("Uploading and indexing... This may take a few minutes."):
                try:
                    files = {
                        "file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")
                    }
                    data_form = {"force_reindex": str(force_reindex).lower()}

                    response = httpx.post(
                        f"{BACKEND_URL}/colleges/{college['college_code']}/ingest",
                        files=files,
                        data=data_form,
                        timeout=300.0,
                    )

                    if response.status_code == 200:
                        result = response.json()
                        st.session_state.ingestion_done = True
                        st.success(
                            f"Handbook indexed successfully! "
                            f"**{result['chunks_created']}** chunks created from "
                            f"**{result['pages_processed']}** pages."
                        )
                    else:
                        st.error(
                            f"Ingestion failed: {response.json().get('detail', 'Unknown error')}"
                        )
                except httpx.ReadTimeout:
                    st.error("Upload timed out. The file may be very large. Try again.")
                except Exception as e:
                    st.error(f"Error: {e}")

    # ─── Success ─────────────────────────────────────────────
    if st.session_state.ingestion_done:
        st.markdown("---")
        st.markdown("### All Set!")
        st.balloons()
        st.markdown(
            f"""
            Your college handbook is now indexed and ready for student queries.

            **Share these instructions with your students:**

            1. Go to **Student Chat** page
            2. Enter code: **`{college['college_code']}`**
            3. Start asking questions about the handbook!
            """
        )
        st.page_link("pages/2_💬_Student_Chat.py", label="Try Student Chat →", icon="💬")

# ─── Already Registered? ─────────────────────────────────────
st.markdown("---")
st.markdown("### Already Registered?")
st.markdown("If you've already registered, you can look up your college and upload a new handbook.")

with st.form("existing_college_form"):
    existing_code = st.text_input(
        "Enter your college code",
        placeholder="e.g., SPC-a3b2",
    )
    lookup = st.form_submit_button("Look Up College")

if lookup and existing_code:
    try:
        response = httpx.get(f"{BACKEND_URL}/colleges/{existing_code}", timeout=5.0)
        if response.status_code == 200:
            data = response.json()
            st.session_state.registered_college = {
                "college_name": data["college_name"],
                "college_code": data["college_code"],
                "has_openai_key": data.get("has_openai_key", False),
            }
            st.success(f"Found: **{data['college_name']}** — You can upload a new handbook above.")
            st.rerun()
        else:
            st.error("College not found. Check the code and try again.")
    except Exception as e:
        st.error(f"Error: {e}")
