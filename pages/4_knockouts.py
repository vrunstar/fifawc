import streamlit as st
import streamlit.components.v1 as components
import base64
from db import (get_client, fixtures_by_stage, standings_all, res_by_match)
from utils.styles import tusker_title

st.set_page_config(page_title="Knockouts", page_icon="static/logo.png", layout="wide")
st.logo("static/logo.png")

with open("static/fonts/TuskerGrotesk-8700Bold.woff2", "rb") as f:
    t800 = base64.b64encode(f.read()).decode()

with open("static/trophy.png", "rb") as f:
    trophy_b64 = base64.b64encode(f.read()).decode()

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
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

tusker_title("KNOCKOUT BRACKET")
st.divider()

supabase     = get_client()
r32_fixtures = fixtures_by_stage(supabase, 'R32')
r16_fixtures = fixtures_by_stage(supabase, 'R16')
qf_fixtures  = fixtures_by_stage(supabase, 'QF')
sf_fixtures  = fixtures_by_stage(supabase, 'SF')
f_fixtures   = fixtures_by_stage(supabase, 'Final')
tp_fixtures  = fixtures_by_stage(supabase, '3RD')

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

def resolve(label):
    if not label:
        return None, label
    if label in pos_map:
        team = pos_map[label]
        return team, team['team_code']
    if label.startswith('W'):
        match_no = int(label[1:])
        all_ko = r32_fixtures + r16_fixtures + qf_fixtures + sf_fixtures
        for fx in all_ko:
            if fx['match_no'] == match_no:
                result = res_by_match(supabase, fx['match_id'])
                if result and fx['home'] and fx['away']:
                    winner = fx['home'] if result['outcome'] == 'H' else fx['away']
                    return winner, winner['team_code']
    if label.startswith('L'):
        match_no = int(label[1:])
        for fx in sf_fixtures:
            if fx['match_no'] == match_no:
                result = res_by_match(supabase, fx['match_id'])
                if result and fx['home'] and fx['away']:
                    loser = fx['away'] if result['outcome'] == 'H' else fx['home']
                    return loser, loser['team_code']
    return None, label

def make_match_data(fixture):
    h_team, h_code = resolve(fixture['home_label'])
    a_team, a_code = resolve(fixture['away_label'])
    result = res_by_match(supabase, fixture['match_id'])
    try:
        from datetime import datetime
        dt = datetime.fromisoformat(fixture['kickoff_ist'])
        date = dt.strftime('%b %d')
    except:
        date = ''
    return {
        'home_code':  h_code,
        'away_code':  a_code,
        'home_flag':  f"app/static/flags/{h_code}.png" if h_team else '',
        'away_flag':  f"app/static/flags/{a_code}.png" if a_team else '',
        'home_goals': result['home_goals'] if result else None,
        'away_goals': result['away_goals'] if result else None,
        'home_win':   result['outcome'] == 'H' if result else None,
        'match_no':   fixture['match_no'],
    }

def match_html(m, is_final=False):
    def team_row(code, flag_src, goals, is_winner):
        is_placeholder = not flag_src
        flag_html = f'<img src="{flag_src}" width="20" style="border-radius:1px">' if flag_src else '<span class="shield">⬡</span>'
        win_cls   = 'winner' if is_winner else ('loser' if is_winner is False else '')
        tbd_cls   = 'tbd' if is_placeholder else ''
        score     = f'<span class="score">{goals}</span>' if goals is not None else ''
        gold      = ' style="color:#FFD700"' if is_final else ''
        return (
            f'<div class="team {win_cls} {tbd_cls}">'
            f'{flag_html}'
            f'<span class="team-code"{gold}>{code}</span>'
            f'{score}'
            f'</div>'
        )

    h_winner = m['home_win']
    a_winner = False if m['home_win'] else (True if m['home_win'] is False else None)
    final_cls = 'final-match' if is_final else ''

    return (
        f'<div class="match {final_cls}">'
        f'{team_row(m["home_code"], m["home_flag"], m["home_goals"], h_winner)}'
        f'{team_row(m["away_code"], m["away_flag"], m["away_goals"], a_winner)}'
        f'</div>'
    )

r32 = [make_match_data(f) for f in sorted(r32_fixtures, key=lambda x: x['match_no'])]
r16 = [make_match_data(f) for f in sorted(r16_fixtures, key=lambda x: x['match_no'])]
qf  = [make_match_data(f) for f in sorted(qf_fixtures,  key=lambda x: x['match_no'])]
sf  = [make_match_data(f) for f in sorted(sf_fixtures,  key=lambda x: x['match_no'])]
fin = [make_match_data(f) for f in sorted(f_fixtures,   key=lambda x: x['match_no'])]
tp  = [make_match_data(f) for f in sorted(tp_fixtures,  key=lambda x: x['match_no'])]

left_r32_html  = ''.join(match_html(m) for m in r32[:8])
right_r32_html = ''.join(match_html(m) for m in r32[8:])
left_r16_html  = ''.join(match_html(m) for m in r16[:4])
right_r16_html = ''.join(match_html(m) for m in r16[4:])
left_qf_html   = ''.join(match_html(m) for m in qf[:2])
right_qf_html  = ''.join(match_html(m) for m in qf[2:])
left_sf_html   = ''.join(match_html(m) for m in sf[:1])
right_sf_html  = ''.join(match_html(m) for m in sf[1:])
final_html     = match_html(fin[0], is_final=True) if fin else ''
tp_html        = match_html(tp[0]) if tp else ''

font_face = f"""
@font-face {{
    font-family: 'Tusker Grotesk';
    src: url('data:font/woff2;base64,{t800}') format('woff2');
    font-weight: 900;
    font-display: swap;
}}
"""

html = f"""<!DOCTYPE html>
<html>
<head>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
  {font_face}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ background: transparent; padding: 20px 10px; overflow-x: auto; }}
  .bracket {{ display: flex; flex-direction: row; align-items: center; justify-content: center; min-width: 1400px; }}
  .col {{ display: flex; flex-direction: column; justify-content: space-around; align-items: center; flex: 1; }}
  .match {{ background: #1a1d27; border: 1.5px solid #2d3148; border-radius: 6px; overflow: hidden; width: 130px; margin: 8px 0; }}
  .final-match {{ border-color: #FFD700; }}
  .team {{ display: flex; align-items: center; justify-content: center; gap: 7px; padding: 8px 10px; border-bottom: 1px solid #2d3148; min-height: 34px; }}
  .team:last-of-type {{ border-bottom: none; }}
  .team-code {{ font-family: 'Tusker Grotesk', sans-serif; font-weight: 900; font-size: 0.95rem; color: #e0e0e0; letter-spacing: 0.5px; flex: 1; }}
  .team.winner .team-code {{ color: #4caf7d; }}
  .team.loser  .team-code {{ color: #3a3f55; }}
  .team.tbd    .team-code {{ font-family: 'Inter', sans-serif !important; font-weight: 400; font-size: 0.78rem; color: #e0e0e0; }}
  .score {{ font-family: 'Inter', sans-serif; font-weight: 700; font-size: 0.85rem; color: inherit; }}
  .shield {{ color: #2d3148; font-size: 1rem; }}
  .trophy-col {{ display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 20px; padding: 0 10px; min-width: 160px; }}
</style>
</head>
<body>
<div class="bracket">
  <div class="col" style="gap:4px">{left_r32_html}</div>
  <div class="col" style="gap:60px">{left_r16_html}</div>
  <div class="col" style="gap:180px">{left_qf_html}</div>
  <div class="col" style="gap:400px">{left_sf_html}</div>
  <div class="trophy-col">
    <img src="data:image/png;base64,{trophy_b64}" width="80" style="margin-bottom:5px">
    {final_html}
    <div style="height:30px"></div>
    {tp_html}
  </div>
  <div class="col" style="gap:400px">{right_sf_html}</div>
  <div class="col" style="gap:180px">{right_qf_html}</div>
  <div class="col" style="gap:60px">{right_r16_html}</div>
  <div class="col" style="gap:4px">{right_r32_html}</div>
</div>
</body>
</html>"""

components.html(html, height=1100, scrolling=True)
