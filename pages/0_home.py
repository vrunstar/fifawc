import streamlit as st
import streamlit.components.v1 as components
import base64

st.set_page_config(
    page_title="FIFA WC Predictor",
    page_icon="static/logo.png",
    layout="wide",
)

if 'scheduler_started' not in st.session_state:
    from scheduler import start
    start()
    st.session_state.scheduler_started = True

with open("static/fonts/TuskerGrotesk-8700Bold.woff2", "rb") as f:
    t800 = base64.b64encode(f.read()).decode()

components.html(f"""
<style>
@font-face {{
    font-family: 'Tusker Grotesk';
    src: url('data:font/woff2;base64,{t800}') format('woff2');
    font-weight: 800;
}}
h1 {{
    text-align: center;
    font-family: 'Tusker Grotesk', sans-serif;
    font-weight: 800;
    font-size: 5rem;
    color: white;
    margin: 0;
    line-height: 1.1;
}}
</style>
<h1><br>WELCOME TO MY<br>2026 FIFA WORLD CUP<br>PREDICTOR</h1>
""", height=600)
