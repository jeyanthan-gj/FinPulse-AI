"""
FinPulse AI - Personal Indian Financial Research Terminal
Streamlit Interface connecting via asynchronous Background Jobs with live polling.
Zero HTTP read timeouts, zero timers displayed to the user.
"""

import os
import time
import requests
import streamlit as st

# ==============================================================================
# CONFIGURATION & CONSTANTS
# ==============================================================================
DEFAULT_API_BASE = os.getenv("API_BASE_URL", "http://127.0.0.1:8001")

st.set_page_config(
    page_title="FinPulse AI | Personal Market Research",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling
st.markdown(
    """
    <style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1100px;
    }
    .header-card {
        padding: 1.2rem 1.5rem;
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border-radius: 12px;
        color: #ffffff;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .header-title {
        font-size: 1.6rem;
        font-weight: 700;
        margin: 0;
        color: #f8fafc;
    }
    .header-desc {
        font-size: 0.95rem;
        color: #94a3b8;
        margin: 0.3rem 0 0 0;
    }
    .status-online {
        display: inline-block;
        padding: 0.2rem 0.6rem;
        font-size: 0.75rem;
        font-weight: 600;
        border-radius: 9999px;
        background-color: #dcfce7;
        color: #15803d;
    }
    .status-offline {
        display: inline-block;
        padding: 0.2rem 0.6rem;
        font-size: 0.75rem;
        font-weight: 600;
        border-radius: 9999px;
        background-color: #fee2e2;
        color: #b91c1c;
    }
    div[data-testid="stSidebar"] button {
        text-align: left;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ==============================================================================
# API CLIENT (HTTP REQUESTS ONLY)
# ==============================================================================
class BackendAPIClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    def check_health(self) -> dict:
        try:
            res = requests.get(f"{self.base_url}/", timeout=4)
            if res.status_code == 200:
                return {"online": True, "data": res.json()}
        except Exception as e:
            return {"online": False, "error": str(e)}
        return {"online": False, "error": f"Status {res.status_code}"}

    def get_sessions(self) -> list:
        try:
            res = requests.get(f"{self.base_url}/sessions", timeout=5)
            if res.status_code == 200:
                return res.json()
        except Exception:
            pass
        return []

    def get_session_history(self, session_id: str) -> list:
        try:
            res = requests.get(f"{self.base_url}/sessions/{session_id}/history", timeout=5)
            if res.status_code == 200:
                return res.json().get("messages", [])
        except Exception:
            pass
        return []

    def submit_job(self, message: str, session_id: str | None = None) -> dict:
        """Submit a job asynchronously. Returns immediately with job_id and session_id."""
        payload = {"message": message}
        if session_id:
            payload["session_id"] = session_id
        res = requests.post(
            f"{self.base_url}/jobs/submit",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10,
        )
        res.raise_for_status()
        return res.json()

    def get_job_status(self, job_id: str) -> dict:
        """Poll the job status. Returns in milliseconds."""
        res = requests.get(f"{self.base_url}/jobs/{job_id}", timeout=5)
        res.raise_for_status()
        return res.json()

    def delete_session(self, session_id: str) -> bool:
        try:
            res = requests.delete(f"{self.base_url}/sessions/{session_id}", timeout=5)
            return res.status_code == 200
        except Exception:
            return False

    def clear_all_sessions(self) -> bool:
        try:
            res = requests.delete(f"{self.base_url}/sessions", timeout=5)
            return res.status_code == 200
        except Exception:
            return False


# ==============================================================================
# STATE INITIALIZATION
# ==============================================================================
if "active_session_id" not in st.session_state:
    st.session_state.active_session_id = None

if "messages" not in st.session_state:
    st.session_state.messages = []

if "api_url" not in st.session_state:
    st.session_state.api_url = DEFAULT_API_BASE

if "prompt_to_submit" not in st.session_state:
    st.session_state.prompt_to_submit = None

api = BackendAPIClient(st.session_state.api_url)


# ==============================================================================
# SIDEBAR: SESSIONS & SETTINGS
# ==============================================================================
with st.sidebar:
    st.title("📈 FinPulse AI")
    st.caption("Personal Market Research Engine")

    health = api.check_health()
    if health["online"]:
        st.markdown(
            '<span class="status-online">● Server Connected</span>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<span class="status-offline">● Backend Offline</span>',
            unsafe_allow_html=True,
        )
        st.warning(f"Could not connect to {st.session_state.api_url}")

    st.divider()

    if st.button("➕ New Research", use_container_width=True, type="primary"):
        st.session_state.active_session_id = None
        st.session_state.messages = []
        st.rerun()

    st.subheader("Saved Sessions")

    sessions = api.get_sessions() if health["online"] else []

    if not sessions:
        st.info("No prior sessions found.")
    else:
        for s in sessions:
            sid = s.get("session_id")
            title = s.get("title") or sid
            label = title if len(title) <= 28 else title[:25] + "..."

            is_active = st.session_state.active_session_id == sid
            btn_type = "secondary" if not is_active else "primary"

            col_sess, col_del = st.columns([0.82, 0.18])
            with col_sess:
                if st.button(
                    f"{'📌 ' if is_active else ''}{label}",
                    key=f"sess_{sid}",
                    use_container_width=True,
                    type=btn_type,
                    help=title,
                ):
                    st.session_state.active_session_id = sid
                    hist = api.get_session_history(sid)
                    st.session_state.messages = [
                        {
                            "role": "user" if m.get("role") in ("human", "user") else "assistant",
                            "content": m.get("content", ""),
                        }
                        for m in hist
                    ]
                    st.rerun()

            with col_del:
                if st.button("🗑️", key=f"del_{sid}", help="Delete this session"):
                    api.delete_session(sid)
                    if st.session_state.active_session_id == sid:
                        st.session_state.active_session_id = None
                        st.session_state.messages = []
                    st.rerun()

    st.divider()

    with st.expander("⚙️ Connection Settings"):
        new_url = st.text_input(
            "Backend API URL",
            value=st.session_state.api_url,
            help="FastAPI endpoint base URL",
        )
        if new_url != st.session_state.api_url:
            st.session_state.api_url = new_url
            st.rerun()

        if st.button("Clear All History", type="secondary", use_container_width=True):
            if api.clear_all_sessions():
                st.session_state.active_session_id = None
                st.session_state.messages = []
                st.success("All sessions cleared.")
                st.rerun()


# ==============================================================================
# MAIN CHAT VIEW
# ==============================================================================

st.markdown(
    """
    <div class="header-card">
        <h2 class="header-title">FinPulse AI Terminal</h2>
        <p class="header-desc">Personal Verified Intelligence for Indian Equities, Derivatives, Mutual Funds & Macroeconomics.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

if not st.session_state.messages:
    st.markdown("#### Quick Research Templates")
    templates = [
        "Analyse Reliance fundamentals and tell me if its valuation is fair.",
        "Compare TCS vs Infosys. Which one has better margins and dividend yield?",
        "How has Kotak Multicap Fund performed over the last 3 years for monthly SIP?",
        "What is the market sentiment and options chain PCR for NIFTY?",
        "Find fundamentally strong mid-cap stocks with ROCE > 20%",
        "Show today's institutional FII / DII net activity",
    ]

    cols = st.columns(3)
    for idx, prompt_text in enumerate(templates):
        with cols[idx % 3]:
            if st.button(prompt_text, key=f"tpl_{idx}", use_container_width=True):
                st.session_state.prompt_to_submit = prompt_text
                st.rerun()

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_query = st.chat_input("Ask about Indian stocks, balance sheets, F&O options, or mutual funds...")

if st.session_state.prompt_to_submit:
    user_query = st.session_state.prompt_to_submit
    st.session_state.prompt_to_submit = None

if user_query:
    # 1. Add user message to UI immediately
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)

    # 2. Submit Background Job (returns in <50ms, no timeout possible)
    with st.chat_message("assistant"):
        with st.spinner("Analyzing live exchange feeds, financial statements, and indicators..."):
            try:
                active_id = st.session_state.active_session_id
                job_data = api.submit_job(message=user_query, session_id=active_id)
                job_id = job_data.get("job_id")
                st.session_state.active_session_id = job_data.get("session_id")

                # Poll job status every 3 seconds until completed or failed
                ai_reply = None
                while True:
                    time.sleep(3)
                    status_info = api.get_job_status(job_id)
                    curr_status = status_info.get("status")

                    if curr_status == "completed":
                        ai_reply = status_info.get("result") or "Analysis completed."
                        break
                    elif curr_status == "failed":
                        err_text = status_info.get("error") or "Unknown execution error"
                        raise RuntimeError(err_text)

                st.markdown(ai_reply)
                st.session_state.messages.append({"role": "assistant", "content": ai_reply})

            except requests.exceptions.ConnectionError:
                err_msg = f"⚠️ Could not reach the backend API at `{st.session_state.api_url}`. Make sure FastAPI server is running."
                st.error(err_msg)
                st.session_state.messages.append({"role": "assistant", "content": err_msg})
            except Exception as e:
                err_msg = f"⚠️ Request error: {str(e)}"
                st.error(err_msg)
                st.session_state.messages.append({"role": "assistant", "content": err_msg})

    st.rerun()
