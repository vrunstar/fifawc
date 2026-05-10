import streamlit as st
import requests
import base64
from datetime import datetime
from db import get_client, pred_all, standings_all
import pytz
import streamlit.components.v1 as components

st.set_page_config(page_title="Results", page_icon="static/logo.png", layout="wide")
st.logo("static/logo.png")

@st.cache_data(ttl=86400)
def flag(team_code: str) -> str:
    return f"app/static/flags/{team_code}.png"

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
<h1>RESULTS</h1>
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

/* Tusker for main text */
.sub-text    { font-family: 'Inter', sans-serif; font-size: 0.9rem; color: #888; margin-top: 2px; }
.team-meta   { font-family: 'Inter', sans-serif; font-size: 0.9rem; color: #888; letter-spacing: 1px; }
.date-header { font-family: 'Inter', sans-serif; font-size: 0.85rem; font-weight: 700; color: #888;
               margin: 40px 0 40px 0; text-transform: uppercase; letter-spacing: 2px;
               border-bottom: 1px solid #2d3148; padding-bottom: 10px;
               display: flex; align-items: center; gap: 20px; }
.accuracy-badge { font-family: 'Inter', sans-serif; font-size: 0.72rem; font-weight: 600;
                  padding: 2px 10px; border-radius: 99px; }

/* Background */
[data-testid="stAppViewContainer"] {
    background-image: url("app/static/bg1.png");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
    background-repeat: no-repeat;
}
[data-testid="stHeader"] { background: transparent; }
[data-testid="stSidebar"] { background: rgba(14, 17, 23, 0.9); }

/* Cards */
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
h1 { font-family: 'Tusker Grotesk', sans-serif !important; font-weight: 800 !important; }
.flag-code-home { display: flex; align-items: center; gap: 10px; }
.flag-code-away { display: flex; align-items: center; justify-content: flex-end; gap: 10px; }
.team-code  { font-family: 'Tusker Grotesk', sans-serif; font-size: 1.75rem; font-weight: 800; color: #e0e0e0; letter-spacing: 1px; }
.vs-block   { text-align: center; }
.score-big  { font-family: 'Tusker Grotesk', sans-serif; font-size: 1.75rem; font-weight: 800; color: #e0e0e0;
              letter-spacing: 2px; margin-bottom: 2px; }
</style>
""", unsafe_allow_html=True)

supabase  = get_client()
positions = build_position_map(supabase)
all_preds = pred_all(supabase)

st.divider()

if not all_preds:
    st.info("No predictions generated yet.")
    st.stop()

IST = pytz.timezone("Asia/Kolkata")

# ── Group by IST date ─────────────────────────────────────────────────────────
grouped = {}
for p in all_preds:
    fixture = p.get('fixture')
    if not fixture:
        continue
    try:
        dt = datetime.fromisoformat(fixture['kickoff_ist']).astimezone(IST)
        date_key = dt.date()
    except:
        continue
    grouped.setdefault(date_key, []).append(p)

# ── Render card ───────────────────────────────────────────────────────────────
def render_card(p, positions):
    fixture    = p['fixture']
    home       = fixture['home']
    away       = fixture['away']
    home_flag  = flag(home['team_code'])
    away_flag  = flag(away['team_code'])
    home_pos   = positions.get(home['team_id'], home['group_name'])
    away_pos   = positions.get(away['team_id'], away['group_name'])
    pred_score = f"{p['pred_home_goals']} – {p['pred_away_goals']}"
    confidence = f"{p['model_confidence']*100:.1f}%"

    result = fixture.get('results')
    if result:
        correct      = result['outcome'] == p['predicted_outcome']
        color        = "#4caf7d" if correct else "#f57c7c"
        icon         = "✓" if correct else "✗"
        actual_score = f"{result['home_goals']} – {result['away_goals']}"
        top          = f'<div class="score-big" style="color:{color}">{actual_score} {icon}</div>'
        bottom       = f'<div class="sub-text">Pred: {pred_score} · Conf: {confidence}</div>'
    else:
        top    = f'<div class="score-big" style="color:#e0e0e0">? – ?</div>'
        bottom = f'<div class="sub-text">Pred: {pred_score} · Conf: {confidence}</div>'

    st.markdown(f"""
    <div class="match-card">
      <div class="teams-row">
        <div>
          <div class="flag-code-home">
            <img src="{home_flag}" width="40" style="border-radius:2px; vertical-align:middle">
            <span class="team-code">{home['team_code']}</span>
            <span class="team-meta">{home_pos}</span>
          </div>
        </div>
        <div class="vs-block">
          {top}
          {bottom}
        </div>
        <div>
          <div class="flag-code-away">
            <span class="team-meta">{away_pos}</span>
            <span class="team-code">{away['team_code']}</span>
            <img src="{away_flag}" width="40" style="border-radius:2px; vertical-align:middle">
          </div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

# ── Render by date ────────────────────────────────────────────────────────────
for date_key in sorted(grouped.keys(), reverse=True):
    preds_on_day = grouped[date_key]

    completed = [p for p in preds_on_day if p['fixture'].get('status') == 'completed']
    correct   = [p for p in completed if p['fixture'].get('results') and
                 p['fixture']['results']['outcome'] == p['predicted_outcome']]

    date_str  = date_key.strftime("%A, %d %B %Y").upper()
    acc_color = "#4caf7d" if completed and len(correct) == len(completed) \
                else "#f5884c" if completed else "#888"
    acc_html  = f'<span class="accuracy-badge" style="background:{acc_color}22; color:{acc_color}">{len(correct)}/{len(completed)} correct</span>' \
                if completed else ''

    #st.markdown(f'<div class="date-header">{date_str}{acc_html}</div>', unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center; color:#888; font-family:Inter,sans-serif; font-weight: 900; font-size:0.9rem'>{date_str}{acc_html}</p>", unsafe_allow_html=True)


    for p in preds_on_day:
        render_card(p, positions)