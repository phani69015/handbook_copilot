"""Handbook Copilot - Product Landing Page."""

import os

import httpx
import streamlit as st

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(
    page_title="Handbook Copilot",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed",
)

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

# ─── Hero Section ────────────────────────────────────────────
st.markdown(
    """
    <div style="text-align: center; padding: 3rem 0 1rem 0;">
        <h1 style="font-size: 3.2rem; margin-bottom: 0.5rem;">📚 Handbook Copilot</h1>
        <p style="font-size: 1.4rem; color: #555; max-width: 600px; margin: 0 auto;">
            AI-powered handbook assistant for universities and colleges.
            Instant, cited answers from your student handbook.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("---")

# ─── Value Proposition ───────────────────────────────────────
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### ⚡ Instant Answers")
    st.markdown(
        "Students get accurate, cited answers from the handbook in seconds. "
        "No more digging through 300-page PDFs."
    )

with col2:
    st.markdown("### 📄 Cited Sources")
    st.markdown(
        "Every answer comes with exact section and page references. "
        "Students can verify directly in the original document."
    )

with col3:
    st.markdown("### 🏫 Any College")
    st.markdown(
        "Register your institution, upload your handbook PDF, "
        "and your students are ready to go."
    )

st.markdown("---")

# ─── How It Works ────────────────────────────────────────────
st.markdown("## How It Works")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("**1. Register**")
    st.markdown("Admin registers the college with an invite code.")

with col2:
    st.markdown("**2. Upload**")
    st.markdown("Upload the student handbook PDF. We index it automatically.")

with col3:
    st.markdown("**3. Share**")
    st.markdown("Share the college access code with students.")

with col4:
    st.markdown("**4. Ask**")
    st.markdown("Students enter the code and start asking questions.")

st.markdown("---")

# ─── CTA Buttons (Highlighted) ───────────────────────────────
st.markdown("## Get Started")
st.markdown("")

col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown(
        """
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    padding: 2rem; border-radius: 16px; text-align: center; color: white;
                    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);">
            <h2 style="color: white; margin-bottom: 0.5rem;">🏫 College Admin</h2>
            <p style="color: rgba(255,255,255,0.9); font-size: 1.1rem;">
                Register your college and upload your student handbook.
                You'll need an invite code from the platform admin.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.page_link(
        "pages/1_🏫_Register_College.py",
        label="Register College →",
        icon="🏫",
        use_container_width=True,
    )

with col2:
    st.markdown(
        """
        <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                    padding: 2rem; border-radius: 16px; text-align: center; color: white;
                    box-shadow: 0 4px 15px rgba(245, 87, 108, 0.4);">
            <h2 style="color: white; margin-bottom: 0.5rem;">💬 Student</h2>
            <p style="color: rgba(255,255,255,0.9); font-size: 1.1rem;">
                Enter your college code and start asking questions
                about your handbook. Get instant, cited answers.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.page_link(
        "pages/2_💬_Student_Chat.py",
        label="Student Chat →",
        icon="💬",
        use_container_width=True,
    )

st.markdown("---")

# ─── Registered Colleges ─────────────────────────────────────
st.markdown("## Registered Colleges")

try:
    response = httpx.get(f"{BACKEND_URL}/colleges", timeout=5.0)
    if response.status_code == 200:
        data = response.json()
        if data["total"] > 0:
            for college in data["colleges"]:
                status = "✅ Indexed" if college["is_indexed"] else "⏳ Pending upload"
                openai_badge = " | 🚀 Fast (OpenAI)" if college.get("has_openai_key") else ""
                st.markdown(
                    f"- **{college['college_name']}** — Code: `{college['college_code']}` — "
                    f"{status} ({college['total_chunks']} chunks){openai_badge}"
                )
        else:
            st.info("No colleges registered yet. Be the first!")
    else:
        st.warning("Could not fetch college list.")
except httpx.ConnectError:
    st.warning("Backend not available. Please ensure the service is running.")
except Exception:
    st.warning("Could not connect to the backend.")

# ─── Footer ──────────────────────────────────────────────────
st.markdown("---")
st.caption("Handbook Copilot — Built with FastAPI, Qdrant, Ollama/OpenAI, and Streamlit")
