import streamlit as st
import requests
import base64
from db import get_client, get_ist, fixtures_today, pred_by_match, standings_all
import streamlit.components.v1 as components
from utils.styles import inject_styles
inject_styles()

st.set_page_config(page_title="Match Prediction", page_icon="static/logo.png", layout="wide")
st.logo("static/logo.png")

@st.cache_data(ttl=86400)
def flag(team_code: str) -> str:
    return f"app/static/flags/{team_code}.png"

# ── Position map ──────────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def build_position_map(_supabase) -> dict:
    all_standings = standings_all(_supabase)
    groups = {}
    for row in all_standings:
        g = row['group_name']
        if g not in groups:
            groups[g] = []
        groups[g].append(row)
    position_map = {}
    for g, rows in groups.items():
        sorted_rows = sorted(rows, key=lambda x: (-x['points'], -x['gd'], -x['gf']))
        for i, row in enumerate(sorted_rows, 1):
            position_map[row['team_id']] = f"{g}{i}"
    return position_map

# ── CSS ───────────────────────────────────────────────────────────────────────
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
    font-size: 3rem;
    color: white;
    margin: 0;
}
</style>
<h1>TODAY'S FIXTURES</h1>
""", height=80)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

@font-face {
    font-family: 'Tusker Grotesk';
    src: url('app/static/fonts/TuskerGrotesk-5700Bold.woff2') format('woff2');
    font-weight: 400;
}
@font-face {
    font-family: 'Tusker Grotesk';
    src: url('app/static/fonts/TuskerGrotesk-6500Bold.woff2') format('woff2');
    font-weight: 600;
}
@font-face {
    font-family: 'Tusker Grotesk';
    src: url('app/static/fonts/TuskerGrotesk-7700Bold.woff2') format('woff2');
    font-weight: 700;
}
@font-face {
    font-family: 'Tusker Grotesk';
    src: url('app/static/fonts/TuskerGrotesk-8700Bold.woff2') format('woff2');
    font-weight: 800;
}


            
.kickoff  { font-family: 'Inter', sans-serif; font-size: 0.9rem; font-weight: 900; color: #888; margin-top: 2px; }
.team-meta { font-family: 'Inter', sans-serif; font-size: 0.9rem; font-weight: 900; color: #888; letter-spacing: 1px; }
.split-label-row { font-family: 'Inter', sans-serif; display: flex; font-size: 0.9rem;
                   font-weight: 600; margin-bottom: 2px; white-space: nowrap; overflow: hidden; }
.split-label-row div { white-space: nowrap; overflow: hidden; }
.split-label-row div:last-child { text-align: right; overflow: visible; flex-shrink: 0; }

            
[data-testid="stAppViewContainer"] {
    background-image: url("app/static/bg.png");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
    background-repeat: no-repeat;
}
[data-testid="stHeader"] { background: transparent; }
[data-testid="stSidebar"] { background: rgba(14, 17, 23, 0.9); }


.match-card {
    background: #1a1d27;
    border: 2px solid #2d3148;
    border-radius: 15px;
    padding: 14px 24px;
    margin-bottom: 10px;
}
.teams-row {
    display: grid;
    grid-template-columns: 1fr auto 1fr;
    align-items: center;
    gap: 1px;
}
.flag-code-home { display: flex; align-items: center; gap: 10px; }
.flag-code-away { display: flex; align-items: center; justify-content: flex-end; gap: 10px; }
.team-code      { font-size: 1.75rem; font-weight: 800; color: #e0e0e0; letter-spacing: 1px; }
.vs-block       { text-align: center; }
.pred-score-big { font-size: 1.75rem; font-weight: 800; color: #e0e0e0;
                  letter-spacing: 2px; margin-bottom: 2px; }
.divider        { border: none; border-top: 1px solid #2d3148; margin: 2px 0; }
.split-bar-wrap { margin: 5px 0; }
.split-bar      { display: flex; height: 8px; border-radius: 2px;
                  overflow: hidden; background: #2d3148; }
</style>
""", unsafe_allow_html=True)

# ── Data ──────────────────────────────────────────────────────────────────────
supabase = get_client()
fixtures = fixtures_today(supabase)
positions = build_position_map(supabase)

st.markdown(f"<p style='text-align:center; color:#888; font-family:Inter,sans-serif; font-weight: 900; font-size:0.9rem'>{get_ist().strftime('%A, %d %B %Y')} · IST</p>", unsafe_allow_html=True)
st.divider()

if not fixtures:
    st.info("No matches scheduled for today.")
    st.stop()

# ── Render ────────────────────────────────────────────────────────────────────
def render_card(f, pred, positions):
    home = f['home']
    away = f['away']

    home_flag = flag(home['team_code'])
    away_flag = flag(away['team_code'])
    home_pos  = positions.get(home['team_id'], home['group_name'])
    away_pos  = positions.get(away['team_id'], away['group_name'])
    kickoff   = f['kickoff_ist'][11:16]

    if pred:
        hw = f"{pred['home_win_prob']*100:.1f}%"
        dw = f"{pred['draw_prob']*100:.1f}%"
        aw = f"{pred['away_win_prob']*100:.1f}%"
        pred_score = f"{pred['pred_home_goals']} – {pred['pred_away_goals']}"
        confidence = f"{pred['model_confidence']*100:.1f}%"
    else:
        hw, dw, aw = "33%", "34%", "33%"
        pred_score = "? – ?"
        confidence = "—"

    bottom_row = f'<div class="kickoff">{kickoff} IST · {f["city"]} · {confidence}</div>'

    st.markdown(f"""
    <div class="match-card">
      <div class="teams-row">
        <div class="team-home">
          <div class="flag-code-home">
            <img src="{home_flag}" width="45" style="border-radius:3px;">
            <span class="team-code">{home['team_code']}</span>
            <span class="team-meta">{home_pos}</span>
          </div>
        </div>
        <div class="vs-block">
          <div class="pred-score-big">{pred_score}</div>
          {bottom_row}
        </div>
        <div class="team-away">
          <div class="flag-code-away">
            <span class="team-meta">{away_pos}</span>
            <span class="team-code">{away['team_code']}</span>
            <img src="{away_flag}" width="45" style="border-radius:5px; vertical-align:middle">
          </div>
        </div>
      </div>
      <hr class="divider">
      <div class="split-bar-wrap">
        <div class="split-label-row">
          <div style="width:{hw}; color:#4c8bf5;">{hw}</div>
          <div style="width:{dw}; color:#777; text-align:center">{dw}</div>
          <div style="margin-left:auto; color:#f5884c;">{aw}</div>
        </div>
        <div class="split-bar">
          <div style="width:{hw}; background:#4c8bf5; height:100%; border-radius:4px 0 0 4px"></div>
          <div style="width:{dw}; background:#444; height:100%"></div>
          <div style="width:{aw}; background:#f5884c; height:100%; border-radius:0 4px 4px 0"></div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

for f in fixtures:
    pred   = pred_by_match(supabase, f['match_id'])
    render_card(f, pred, positions)