import streamlit as st
import base64
from scheduler import start

st.set_page_config(
    page_title="FIFA WC 2026",
    page_icon="static/logo.png",
    layout="wide"
)
st.logo("static/logo.png")

# ── Scheduler ─────────────────────────────────────────────────────────────────
if 'scheduler_started' not in st.session_state:
    start()
    st.session_state.scheduler_started = True

# ── Load Tusker as base64 ─────────────────────────────────────────────────────
def load_font(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

tusker_800 = load_font("static/fonts/TuskerGrotesk-8700Bold.woff2")
tusker_700 = load_font("static/fonts/TuskerGrotesk-7700Bold.woff2")
tusker_600 = load_font("static/fonts/TuskerGrotesk-6700Bold.woff2")

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

@font-face {{
    font-family: 'Tusker Grotesk';
    src: url('data:font/woff2;base64,{tusker_600}') format('woff2');
    font-weight: 600;
    font-display: swap;
}}
@font-face {{
    font-family: 'Tusker Grotesk';
    src: url('data:font/woff2;base64,{tusker_700}') format('woff2');
    font-weight: 700;
    font-display: swap;
}}
@font-face {{
    font-family: 'Tusker Grotesk';
    src: url('data:font/woff2;base64,{tusker_800}') format('woff2');
    font-weight: 800;
    font-display: swap;
}}

* {{ font-family: 'Inter', sans-serif; }}
h1 {{ font-family: 'Tusker Grotesk', sans-serif !important; font-weight: 800 !important; }}
h2, h3 {{ font-family: 'Tusker Grotesk', sans-serif !important; font-weight: 700 !important; }}

[data-testid="stAppViewContainer"] {{
    background-image: url("app/static/bg.png");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
    background-repeat: no-repeat;
}}
[data-testid="stHeader"] {{
    background: transparent;
    backdrop-filter: blur(25px);
}}
[data-testid="stHeader"] * {{ font-family: 'Inter', sans-serif !important; }}
[data-testid="stNavLink"] {{
    font-family: 'Inter', sans-serif !important;
    font-size: 0.85rem;
    letter-spacing: 0.5px;
}}
[data-testid="stSidebar"] {{ background: rgba(14, 17, 23, 0.9); }}
</style>
""", unsafe_allow_html=True)

# ── Navigation ────────────────────────────────────────────────────────────────
pages = [
    st.Page("pages/0_home.py",   title="Home"),
    st.Page("pages/1_fixtures.py",   title="Fixtures"),
    st.Page("pages/2_results.py",    title="Results"),
    st.Page("pages/3_standings.py",    title="Standings"),
    st.Page("pages/4_knockouts.py",           title="Knockouts"),
    st.Page("pages/5_admin.py",        title="Admin"),
]

pg = st.navigation(pages, position='top')
pg.run()