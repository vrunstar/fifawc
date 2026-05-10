import streamlit as st
import requests
import base64
from db import get_client, standings_all
import streamlit.components.v1 as components
from utils.styles import inject_styles
inject_styles()

st.set_page_config(page_title="Standings", page_icon="static/logo.png", layout="wide")
st.logo("static/logo.png")
@st.cache_data(ttl=86400)
def flag(team_code: str) -> str:
    return f"app/static/flags/{team_code}.png"

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
<h1>GROUP STANDINGS</h1>
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



[data-testid="stAppViewContainer"] {
    background-image: url("app/static/bg1.png");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
    background-repeat: no-repeat;
}
[data-testid="stHeader"] { background: transparent; }
[data-testid="stSidebar"] { background: rgba(14, 17, 23, 0.9); }

.group-card {
    background: #1a1d27;
    border: 2px solid #2d3148;
    border-radius: 15px;
    padding: 16px;
    margin-bottom: 16px;
}
.group-title {
    font-size: 1rem;
    font-weight: 800;
    color: #888;
    letter-spacing: 3px;
    text-transform: uppercase;
    font-family: 'Tusker Grotesk', sans-serif;
    text-align: center;
    margin-bottom: 12px;
    padding-bottom: 8px;
    border-bottom: 1px solid #2d3148;
}
.standing-row {
    display: grid;
    grid-template-columns: 24px 36px 1fr 32px 32px 32px 32px 32px 40px;
    align-items: center;
    gap: 6px;
    padding: 6px 0;
    border-bottom: 1px solid #1e2130;
    font-family: 'Inter', sans-serif;
    font-size: 0.85rem;
}
.standing-row:last-child { border-bottom: none; }
.standing-header {
    display: grid;
    grid-template-columns: 24px 36px 1fr 32px 32px 32px 32px 32px 40px;
    align-items: center;
    gap: 6px;
    padding: 0 0 6px 0;
    font-family: 'Inter', sans-serif;
    font-size: 0.7rem;
    color: #555;
    letter-spacing: 1px;
    border-bottom: 1px solid #2d3148;
    margin-bottom: 4px;
}
.team-name-cell { font-family: 'Tusker Grotesk', sans-serif; color: #e0e0e0; font-weight: 900; }
.stat-cell { font-family: 'Inter', sans-serif; text-align: center; color: #aaa; }
.pts-cell {font-family: 'Inter', sans-serif; text-align: center; color: #e0e0e0; font-weight: 700; }
</style>
""", unsafe_allow_html=True)


supabase = get_client()

@st.cache_data(ttl=60)
def get_standings(_supabase):
    return standings_all(_supabase)

all_standings = get_standings(supabase)
st.divider()

# ── organise & sort ──────────────────────────────────────────────────────────
groups: dict = {}
for row in all_standings:
    g = row['group_name']
    groups.setdefault(g, []).append(row)

for g in groups:
    groups[g] = sorted(
        groups[g],
        key=lambda x: (-x['points'], -x['gd'], -x['gf']),
    )

group_keys = sorted(groups.keys())
cols = st.columns(3)

# ── render each group card ───────────────────────────────────────────────────
for i, g in enumerate(group_keys):
    rows = groups[g]

    # Build every row's HTML first (no nested f-strings with format specs)
    rows_html_parts = []
    for pos, row in enumerate(rows, 1):
        team   = row['team']
        code   = team['team_code']
        flag = f"app/static/flags/{code}.png"
        name   = team['name']      # noqa: F841  (kept for future use)
        played = row['played']
        won    = row['won']
        drawn  = row['drawn']
        lost   = row['lost']
        gd     = row['gd']
        pts    = row['points']

        # Pre-format everything that needs special formatting
        pos_color = "#4caf7d" if pos <= 2 else "#888"
        gd_str    = ("+" + str(gd)) if gd > 0 else str(gd)
        flag_html = (
            '<img src="{src}" width="25" style="border-radius:1px;vertical-align:middle">'.format(src=flag)
            if flag else ''
        )

        row_html = (
            '<div class="standing-row">'
            '<span style="color:{pc};font-weight:700;font-size:0.85rem">{pos}</span>'
            '<span>{flag}</span>'
            '<span class="team-name-cell">{code}</span>'
            '<span class="stat-cell">{p}</span>'
            '<span class="stat-cell">{w}</span>'
            '<span class="stat-cell">{d}</span>'
            '<span class="stat-cell">{l}</span>'
            '<span class="stat-cell">{gd}</span>'
            '<span class="pts-cell">{pts}</span>'
            '</div>'
        ).format(
            pc=pos_color,
            pos=pos,
            flag=flag_html,
            code=code,
            p=played,
            w=won,
            d=drawn,
            l=lost,
            gd=gd_str,
            pts=pts,
        )
        rows_html_parts.append(row_html)

    rows_html = "".join(rows_html_parts)

    card_html = (
        '<div class="group-card">'
        '<div class="group-title">Group {g}</div>'
        '<div class="standing-header">'
        '<span></span><span></span><span></span>'
        '<span style="text-align:center">P</span>'
        '<span style="text-align:center">W</span>'
        '<span style="text-align:center">D</span>'
        '<span style="text-align:center">L</span>'
        '<span style="text-align:center">GD</span>'
        '<span style="text-align:center">Pts</span>'
        '</div>'
        '{rows}'
        '</div>'
    ).format(g=g, rows=rows_html)

    with cols[i % 3]:
        st.markdown(card_html, unsafe_allow_html=True)