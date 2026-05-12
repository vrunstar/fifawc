import streamlit as st
import streamlit.components.v1 as components
import requests
import base64
from db import (get_client, fixtures_by_stage, standings_all, res_by_match)
import streamlit.components.v1 as components
from utils.styles import inject_styles
inject_styles()

st.set_page_config(page_title="Knockouts", page_icon="static/logo.png", layout="wide")
st.logo("static/logo.png")

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
<h1>KNOCKOUT BRACKETS</h1>
""", height=80)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
@font-face {
    font-family: 'Tusker Grotesk';
    src: url('app/static/fonts/TuskerGrotesk-8700Bold.woff2') format('woff2');
    font-weight: 800;
    font-display: swap;
}

[data-testid="stAppViewContainer"] {
    background-image: url("app/static/bg.png");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
    background-repeat: no-repeat;
}
[data-testid="stHeader"] { background: transparent !important; backdrop-filter: blur(10px); }
[data-testid="stHeader"] * { font-family: 'Inter', sans-serif !important; }
</style>
""", unsafe_allow_html=True)

st.divider()
# ── Data ──────────────────────────────────────────────────────────────────────
supabase     = get_client()
r32_fixtures = fixtures_by_stage(supabase, 'R32')
r16_fixtures = fixtures_by_stage(supabase, 'R16')
qf_fixtures  = fixtures_by_stage(supabase, 'QF')
sf_fixtures  = fixtures_by_stage(supabase, 'SF')
f_fixtures   = fixtures_by_stage(supabase, 'Final')
tp_fixtures  = fixtures_by_stage(supabase, '3RD')

# Build position map
all_standings = standings_all(supabase)
groups = {}
for row in all_standings:
    g = row['group_name']
    groups.setdefault(g, []).append(row)
pos_map = {}
for g, rows in groups.items():
    sorted_rows = sorted(rows, key=lambda x: (-x['points'], -x['gd'], -x['gf']))
    for i, row in enumerate(sorted_rows, 1):
        pos_map[f"{i}{g}"] = row['team']

def flag(team_code: str) -> str:
    return f"app/static/flags/{team_code}.png"

def resolve(label):
    if not label:
        return None, label
    if label in pos_map:
        team = pos_map[label]
        return team, team['team_code']
    if label.startswith('W'):
        match_no = int(label[1:])
        all_ko = r32_fixtures + r16_fixtures + qf_fixtures + sf_fixtures
        for f in all_ko:
            if f['match_no'] == match_no:
                result = res_by_match(supabase, f['match_id'])
                if result and f['home'] and f['away']:
                    winner = f['home'] if result['outcome'] == 'H' else f['away']
                    return winner, winner['team_code']
    if label.startswith('L'):
        match_no = int(label[1:])
        for f in sf_fixtures:
            if f['match_no'] == match_no:
                result = res_by_match(supabase, f['match_id'])
                if result and f['home'] and f['away']:
                    loser = f['away'] if result['outcome'] == 'H' else f['home']
                    return loser, loser['team_code']
    return None, label

def make_match_data(fixture):
    h_team, h_code = resolve(fixture['home_label'])
    a_team, a_code = resolve(fixture['away_label'])
    result = res_by_match(supabase, fixture['match_id'])
    date = fixture['kickoff_ist'][:10] if fixture.get('kickoff_ist') else ''
    try:
        from datetime import datetime
        dt = datetime.fromisoformat(fixture['kickoff_ist'])
        date = dt.strftime('%b %d')
    except:
        pass
    return {
        'home_code': h_code,
        'away_code': a_code,
        'home_flag': f"app/static/flags/{h_code}.png" if h_team else '',
        'away_flag': f"app/static/flags/{a_code}.png" if a_team else '',
        'home_goals': result['home_goals'] if result else None,
        'away_goals': result['away_goals'] if result else None,
        'home_win': result['outcome'] == 'H' if result else None,
        'date': date,
        'match_no': fixture['match_no'],
    }

# Build match data
r32 = [make_match_data(f) for f in sorted(r32_fixtures, key=lambda x: x['match_no'])]
r16 = [make_match_data(f) for f in sorted(r16_fixtures, key=lambda x: x['match_no'])]
qf  = [make_match_data(f) for f in sorted(qf_fixtures,  key=lambda x: x['match_no'])]
sf  = [make_match_data(f) for f in sorted(sf_fixtures,  key=lambda x: x['match_no'])]
fin = [make_match_data(f) for f in sorted(f_fixtures,   key=lambda x: x['match_no'])]
tp  = [make_match_data(f) for f in sorted(tp_fixtures,  key=lambda x: x['match_no'])]

def match_html(m):
    def team_row(code, flag, goals, is_winner):
        is_placeholder = not flag and (
            code.startswith(('1','2','3','W','L')) or code == 'TBD'
        )
        if is_placeholder:
            return f'''<div class="team tbd">
                <span class="shield">⬡</span>
                <span class="team-code">{code}</span>
            </div>'''
        flag_html = f'<img src="{flag}" width="20" style="border-radius:1px">' if flag else '<span class="shield">⬡</span>'
        win_cls = 'winner' if is_winner else ('loser' if is_winner is False else '')
        score = f'<span class="score">{goals}</span>' if goals is not None else ''
        return f'''<div class="team {win_cls}">
            {flag_html}
            <span class="team-code">{code}</span>
            {score}
        </div>'''

    h_winner = m['home_win']
    a_winner = False if m['home_win'] else (True if m['home_win'] is False else None)

    return f'''<div class="match">
        {team_row(m['home_code'], m['home_flag'], m['home_goals'], h_winner)}
        {team_row(m['away_code'], m['away_flag'], m['away_goals'], a_winner)}
    </div>'''

# Left side R32: matches 0-7, Right side: matches 8-15
left_r32  = r32[:8]
right_r32 = r32[8:]
left_r16  = r16[:4]
right_r16 = r16[4:]
left_qf   = qf[:2]
right_qf  = qf[2:]
left_sf   = sf[:1]
right_sf  = sf[1:]
final_m   = fin[0] if fin else None
tp_m      = tp[0] if tp else None

html = f"""
<!DOCTYPE html>
<html>
<head>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
  @font-face {{
    font-family: 'Tusker Grotesk';
    src: url('/app/static/fonts/TuskerGrotesk-8700Bold.woff2') format('woff2');
    font-weight: 900;
    font-display: swap;
  }}

  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ background: transparent; padding: 20px 10px; overflow-x: auto; }}

  .bracket {{
    display: flex;
    flex-direction: row;
    align-items: center;
    justify-content: center;
    gap: 0;
    min-width: 1400px;
  }}

  .col {{
    display: flex;
    flex-direction: column;
    justify-content: space-around;
    align-items: center;
    flex: 1;
  }}

  .match {{
    background: #1a1d27;
    border: 1.5px solid #2d3148;
    border-radius: 6px;
    overflow: hidden;
    width: 130px;
    margin: 8px 0;
  }}

  .team {{
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 7px;
    padding: 8px 10px;
    border-bottom: 1px solid #2d3148;
    min-height: 34px;
  }}
  .team:last-of-type {{ border-bottom: none; }}

  .team-code {{
    font-family: 'Tusker Grotesk', sans-serif;
    font-weight: 900;
    font-size: 0.95rem;
    color: #e0e0e0;
    letter-spacing: 0.5px;
    flex: 1;
  }}
  .team.winner .team-code {{ color: #4caf7d; }}
  .team.loser  .team-code {{ color: #3a3f55; }}
  .team.tbd    .team-code {{
    font-family: 'Inter', sans-serif;
    font-weight: 400;
    font-size: 0.72rem;
    color: #e0e0e0;
  }}

  .score {{
    font-family: 'Tusker Grotesk', sans-serif;
    font-weight: 700;
    font-size: 0.85rem;
    color: inherit;
  }}

  .shield {{ color: #2d3148; font-size: 1rem; }}

  .trophy-col {{
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 20px;
    padding: 0 10px;
    min-width: 160px;
  }}

  .trophy {{ font-size: 3rem; }}
  .champion-label {{
    font-family: 'Inter', sans-serif;
    font-size: 0.65rem;
    color: #555;
    text-transform: uppercase;
    letter-spacing: 2px;
  }}
</style>
</head>
<body>
<div class="bracket">

  <!-- LEFT R32 -->
  <div class="col" style="gap: 4px">
    {''.join(match_html(m) for m in left_r32)}
  </div>

  <!-- LEFT R16 -->
  <div class="col" style="gap: 60px">
    {''.join(match_html(m) for m in left_r16)}
  </div>

  <!-- LEFT QF -->
  <div class="col" style="gap: 180px">
    {''.join(match_html(m) for m in left_qf)}
  </div>

  <!-- LEFT SF -->
  <div class="col" style="gap: 400px">
    {''.join(match_html(m) for m in left_sf)}
  </div>

  <!-- CENTER -->
  <div class="trophy-col">
        <img src="/app/static/trophy.png" width="80" style="margin-bottom:16px">
        {match_html(final_m) if final_m else ''}
        <div style="height:30px"></div>
        {match_html(tp_m) if tp_m else ''}
    </div>

  <!-- RIGHT SF -->
  <div class="col" style="gap: 400px">
    {''.join(match_html(m) for m in right_sf)}
  </div>

  <!-- RIGHT QF -->
  <div class="col" style="gap: 180px">
    {''.join(match_html(m) for m in right_qf)}
  </div>

  <!-- RIGHT R16 -->
  <div class="col" style="gap: 60px">
    {''.join(match_html(m) for m in right_r16)}
  </div>

  <!-- RIGHT R32 -->
  <div class="col" style="gap: 4px">
    {''.join(match_html(m) for m in right_r32)}
  </div>

</div>
</body>
</html>
"""

components.html(html, height=1100, scrolling=True)