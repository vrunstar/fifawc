import base64
import streamlit as st

def load_font(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def inject_styles():
    tusker_800 = load_font("static/fonts/TuskerGrotesk-8700Bold.woff2")
    tusker_700 = load_font("static/fonts/TuskerGrotesk-7700Bold.woff2")

    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

    @font-face {{
        font-family: 'Tusker Grotesk';
        src: url('data:font/woff2;base64,{tusker_800}') format('woff2');
        font-weight: 800;
        font-display: swap;
    }}
    @font-face {{
        font-family: 'Tusker Grotesk';
        src: url('data:font/woff2;base64,{tusker_700}') format('woff2');
        font-weight: 700;
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
    }}
    [data-testid="stSidebar"] {{ background: rgba(14, 17, 23, 0.9); }}
    </style>
    """, unsafe_allow_html=True)