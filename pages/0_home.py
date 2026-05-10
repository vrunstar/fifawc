import streamlit as st
import streamlit.components.v1 as components
from utils.styles import inject_styles
inject_styles()

import base64

def load_font(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

t800 = load_font("static/fonts/TuskerGrotesk-8700Bold.woff2")

st.markdown(f"""
<style>
@font-face {{
    font-family: 'Tusker Grotesk';
    src: url('data:font/woff2;base64,{t800}') format('woff2');
    font-weight: 800;
    font-display: swap;
}}
h1 {{ font-family: 'Tusker Grotesk', sans-serif !important; font-weight: 800 !important; }}
</style>
""", unsafe_allow_html=True)

st.set_page_config(
    page_title="FIFA WC Predictor",
    page_icon="static/logo.png",
    layout="wide",
)

if 'scheduler_started' not in st.session_state:
    from scheduler import start
    start()
    st.session_state.scheduler_started = True

components.html("""
<style>
@font-face {
    font-family: 'Tusker Grotesk';
    src: url('/app/static/fonts/TuskerGrotesk-8700Bold.woff2') format('woff2');
    font-weight: 800;
}
h1 {
    text-align: center;
    font-family: 'Tusker Grotesk', sans-serif;
    font-weight: 800;
    font-size: 5rem;
    color: white;
    margin: 0;
}
</style>
<h1><br>
    WELCOME TO MY<br>
    2026 FIFA WORLD CUP<br>
    PREDICTOR</h1>
""", height=600)