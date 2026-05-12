import streamlit as st
from db import get_client, login, logout, fixtures_group, update_after_res
from utils.styles import tusker_title

st.set_page_config(page_title="Admin", page_icon="static/logo.png", layout="wide")
st.logo("static/logo.png")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

@font-face {
    font-family: 'Tusker Grotesk';
    src: url('app/static/fonts/TuskerGrotesk-8700Bold.woff2') format('woff2');
    font-weight: 800;
    font-display: block;
}
h1 { font-family: 'Tusker Grotesk', sans-serif !important; font-weight: 800 !important; }

[data-testid="stAppViewContainer"] {
    background-image: url("app/static/bg.png");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
    background-repeat: no-repeat;
}
[data-testid="stHeader"] { background: transparent !important; backdrop-filter: blur(10px); }
[data-testid="stHeader"] * { font-family: 'Inter', sans-serif !important; }
[data-testid="stSidebar"] { background: rgba(14, 17, 23, 0.9); }
</style>
""", unsafe_allow_html=True)

supabase = get_client()

# ── Auth gate ─────────────────────────────────────────────────────────────────
if 'admin_user' not in st.session_state:
    st.session_state.admin_user = None

if not st.session_state.admin_user:
    tusker_title("ADMIN PANEL")
    st.divider()

    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        email    = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("Login", type="primary", use_container_width=True):
            user = login(supabase, email, password)
            if user:
                st.session_state.admin_user = user
                st.rerun()
            else:
                st.error("Invalid credentials")
    st.stop()

# ── Admin panel ───────────────────────────────────────────────────────────────
st.markdown("<h1 style='text-align:center'>ADMIN PANEL</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align:center; color:#888; font-family:Inter,sans-serif'>Hello sir</p>", unsafe_allow_html=True)

if st.button("Logout", type="secondary"):
    logout(supabase)
    st.session_state.admin_user = None
    st.rerun()

st.divider()

# ── Enter result ──────────────────────────────────────────────────────────────
st.subheader("Enter Match Result")

fixtures  = fixtures_group(supabase)
incomplete = [f for f in fixtures if f.get('status') != 'completed']

if not incomplete:
    st.info("All group fixtures completed.")
    st.stop()

fixture_options = {
    f"#{f['match_no']} {f['home']['name']} vs {f['away']['name']}": f['match_id']
    for f in incomplete
}

selected = st.selectbox("Select Match", options=list(fixture_options.keys()))
match_id = fixture_options[selected]

col1, col2 = st.columns(2)
with col1:
    home_goals = st.number_input("Home Goals", min_value=0, max_value=20, step=1)
with col2:
    away_goals = st.number_input("Away Goals", min_value=0, max_value=20, step=1)

col1, col2 = st.columns(2)
with col1:
    extra_time = st.checkbox("Extra Time")
with col2:
    penalties = st.checkbox("Penalties")

if st.button("Submit Result", type="primary", use_container_width=True):
    with st.spinner("Updating standings and ELO..."):
        update_after_res(supabase, match_id, int(home_goals), int(away_goals))
    st.success("✓ Result saved · Standings updated · ELO recalculated")
    st.rerun()