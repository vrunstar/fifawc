import base64
import streamlit.components.v1 as components

def tusker_title(text: str, size: str = "3rem"):
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
        font-size: {size};
        color: white;
        margin: 0;
        padding: 10px 0;
    }}
    </style>
    <h1>{text}</h1>
    """, height=90)