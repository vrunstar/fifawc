import streamlit as st
from scheduler import start

st.set_page_config(
    page_title="FIFA WC 2026",
    page_icon="static/logo3.png",
    layout="wide"
)
st.logo("static/logo3.png")

# ── Scheduler ─────────────────────────────────────────────────────────────────
if 'scheduler_started' not in st.session_state:
    start()
    st.session_state.scheduler_started = True

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

/* Base font */
* { font-family: 'Inter', sans-serif; }

/* Background */
[data-testid="stAppViewContainer"] {
    background-image: url("app/static/bg1.png");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
    background-repeat: no-repeat;
}

/* Header */
[data-testid="stHeader"] {
    background: transparent;
    backdrop-filter: blur(25px);
}
[data-testid="stHeader"] * { font-family: 'Inter', sans-serif !important; }

/* Nav links */
[data-testid="stNavLink"] {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.85rem;
    letter-spacing: 0.5px;
}

/* Sidebar */
[data-testid="stSidebar"] { background: rgba(14, 17, 23, 0.9); }
</style>
""", unsafe_allow_html=True)

# ── Navigation ────────────────────────────────────────────────────────────────
pages = [
    st.Page("pages/0_home.py",   title="Home"),
    st.Page("pages/1_match_pred.py",   title="Fixtures"),
    st.Page("pages/2_past_pred.py",    title="Results"),
    st.Page("pages/3_standings.py", title="Standings"),
    st.Page("pages/4_ko.py",     title="Knockouts"),
    st.Page("pages/5_login.py",     title="Admin")
]

pg = st.navigation(pages, position='top')
pg.run()