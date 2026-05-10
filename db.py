import os
from datetime import datetime, date
import pytz
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

def get_client() -> Client:
    url = os.environ["SUPABASE_URL"]
    key = os.environ["SUPABASE_SERVICE_KEY"]
    return create_client(url, key)

def get_ist() -> date:
    return datetime.now(pytz.timezone("Asia/Kolkata")).date()

# ---------------------------------------------------------------------
# TEAMS QUERY
# ---------------------------------------------------------------------

def teams_all(supabase: Client) -> list[dict]:
    res = supabase.table("teams").select("*").execute()
    return res.data

def team_by_id(supabase:Client, team_id: int) -> dict:
    res = supabase.table("teams").select("*").eq("team_id", team_id).single().execute()
    return res.data

# ---------------------------------------------------------------------
# FIXTURES QUERY
# ---------------------------------------------------------------------

def fixtures_today(supabase: Client) -> list[dict]:
    today = str(get_ist())
    res = (supabase.table("fixtures")
           .select("*, home:teams!home_id(*), away:teams!away_id(*)")
           .eq("matchday_ist", "2026-06-12")
           .order("kickoff_ist")
           .execute())
    return res.data

def fixtures_group(supabase: Client) -> list[dict]:
    res = (supabase.table("fixtures")
           .select("*, home:teams!home_id(*), away:teams!away_id(*)")
           .eq("stage", "group")
           .order("kickoff_ist")
           .execute())
    return res.data

def fixtures_by_stage(supabase: Client, stage: str) -> list[dict]:
    res = (supabase.table("fixtures")
           .select("*, home:teams!home_id(*), away:teams!away_id(*)")
           .eq("stage", stage)
           .order("kickoff_ist")
           .execute())
    return res.data

def fixtures_by_id(supabase: Client, match_id: int) -> dict:
    res = (supabase.table("fixtures")
           .select("*, home:teams!home_id(*), away:teams!away_id(*)")
           .eq("match_id", match_id)
           .single()
           .execute())
    return res.data
# ---------------------------------------------------------------------
# PREDICTIONS QUERY
# ---------------------------------------------------------------------

def pred_by_match(supabase: Client, match_id: int) -> dict | None:
    res = (supabase.table("prediction")
           .select("*")
           .eq("match_id", match_id)
           .execute()
           )
    return res.data[0] if res.data else None

def pred_today(supabase: Client) -> list[dict]:
    today = str(get_ist())
    res = (supabase.table("prediction")
           .select("*, fixture:fixtures!match_id(*, home:teams!home_id(*), away:teams!away_id(*))")
           .eq("fixture.matchday_ist", today)
           .order("generated_at", desc=True)
           .execute()
           )
    return [r for r in res.data if r.get("fixture")]

def pred_all(supabase: Client) -> list[dict]:
    res = (supabase.table("prediction")
           .select("*, fixture:fixtures!match_id(*, home:teams!home_id(*), away:teams!away_id(*))")
           .order("generated_at", desc=True)
           .execute()
           )
    return res.data

def pred_updated(supabase: Client, pred: dict) -> list[dict]:
    res = (supabase.table("prediction")
           .upsert(pred, on_conflict="match_id")
           .execute()
           )
    return res.data

# ---------------------------------------------------------------------
# RESULTS QUERY
# ---------------------------------------------------------------------

def res_by_match(supabase:Client, match_id: int) -> dict | None:
    res = (supabase.table("results")
           .select("*")
           .eq("match_id", match_id)
           .execute()
           )
    return res.data[0] if res.data else None

def res_all(supabase: Client) -> list[dict]:
    res = (supabase.table("results")
           .select("*, fixture:fixtures!match_id(*, home:teams!home_id(*), away:teams!away_id(*))")
           .order("updated_at", desc=True)
           .execute()
           )
    return res.data

def res_upsert(supabase: Client, result: dict) -> dict:
    res = (supabase.table("results")
           .upsert(result, on_conflict="match_id")
           .execute()
           )
    return res.data

# ---------------------------------------------------------------------
# STANDINGS QUERY
# ---------------------------------------------------------------------

def standings_by_group(supabase: Client, group_name: str) -> list[dict]:
    res = (supabase.table("standings")
           .select("*, team:teams!team_id(name, team_code, fifa_rank)")
           .eq("group_name", group_name)
           .order("points, gd", desc=True)
           .execute()
           )
    return res.data

def standings_all(supabase: Client) -> list[dict]:
    res = (supabase.table("standings")
           .select("*, team:teams!team_id(name, team_code, fifa_rank)")
           .order("group_name, points, gd", desc=True)
           .execute()
           )
    return res.data

def standings_update(supabase: Client, team_id: int, updates: dict) -> dict:
    res = (supabase.table("standings")
           .update(updates)
           .eq("team_id", team_id)
           .execute())
    return res.data

# ---------------------------------------------------------------------
# UPDATE AFTER RESULTS
# ---------------------------------------------------------------------

def update_after_res(supabase: Client, match_id: int, home_goals: int, away_goals: int) -> None:
    fixtures = fixtures_by_id(supabase, match_id)
    home = fixtures["home"]
    away = fixtures["away"]

    if home_goals > away_goals:
        outcome = "H"
        home_actual, away_actual = 1.0, 0.0
    elif home_goals == away_goals:
        outcome = "D"
        home_actual, away_actual = 0.5, 0.5
    else:
        outcome = "A"
        home_actual, away_actual = 0.0, 1.0

    k =  40
    home_elo = home["elo_rating"]
    away_elo = away["elo_rating"]

    

    expected_home = 1 / (1 + 10 ** ((away_elo - home_elo) / 400))
    expected_away = 1 - expected_home

    print(f"home_elo={home_elo}, away_elo={away_elo}")
    print(f"expected_home={expected_home}, expected_away={expected_away}")
    print(f"home_actual={home_actual}, away_actual={away_actual}")

    new_home_elo = round(home_elo + k * (home_actual - expected_home), 2)
    new_away_elo = round(away_elo + k * (away_actual - expected_away), 2)

    supabase.table("teams").update({"elo_rating":new_home_elo}).eq("team_id", home["team_id"]).execute()
    supabase.table("teams").update({"elo_rating":new_away_elo}).eq("team_id", away["team_id"]).execute()

    def get_standing(team_id):
        return supabase.table("standings").select("*").eq("team_id", team_id).single().execute().data
    
    home_standing = get_standing(home["team_id"])
    away_standing = get_standing(away["team_id"])

    home_updates = {
        "played" : home_standing["played"] + 1,
        "won" : home_standing["won"] + (1 if outcome == "H" else 0),
        "drawn" : home_standing["drawn"] + (1 if outcome == "D" else 0),
        "lost" : home_standing["lost"] + (1 if outcome == "A" else 0),
        "gf" : home_standing["gf"] + home_goals,
        "ga" : home_standing["ga"] + away_goals,
    }
    away_updates = {
        "played" : away_standing["played"] + 1,
        "won" : away_standing["won"] + (1 if outcome == "A" else 0),
        "drawn" : away_standing["drawn"] + (1 if outcome == "D" else 0),
        "lost" : away_standing["lost"] + (1 if outcome == "H" else 0),
        "gf" : away_standing["gf"] + away_goals,
        "ga" : away_standing["ga"] + home_goals,
    }

    supabase.table("standings").update(home_updates).eq("team_id", home["team_id"]).execute()
    supabase.table("standings").update(away_updates).eq("team_id", away["team_id"]).execute()

    res_upsert (supabase, {
        "match_id" : match_id,
        "home_goals" : home_goals,
        "away_goals" : away_goals,
        "outcome" : outcome
    })

    supabase.table("fixtures").update({"status" : "completed"}).eq("match_id", match_id).execute()

    print(f"✓ Match {match_id} updated — {home['name']} {home_goals}-{away_goals} {away['name']}\nELO: {home['name']} {home_elo}→{new_home_elo}, {away['name']} {away_elo}→{new_away_elo}")

# ---------------------------------------------------------------------
# AUTHENTICATION
# ---------------------------------------------------------------------

def login(supabase: Client, email: str, passwd: str):
    try:
        res = supabase.auth.sign_in_with_password({"email" : email, "password" : passwd})
        return res.user
    except Exception:
        return None

def logout(supabase: Client) -> None:
    supabase.auth.sign_out()