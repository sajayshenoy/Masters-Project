import berserk
import os
from dotenv import load_dotenv

# Path to .env (parent/data handling)
env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(env_path)
if not os.getenv("lichess_api_key"):
    load_dotenv()

api_key = os.getenv("lichess_api_key")
session = berserk.TokenSession(api_key) if api_key else None
client = berserk.Client(session=session)

team_id = 'lichess-titled-players'

try:
    print(f"Checking team: {team_id}...", flush=True)
    team = client.teams.get(team_id)
    print(f"Team found: {team.get('name')}", flush=True)
    print(f"Members count: {team.get('nbMembers')}", flush=True)
except Exception as e:
    print(f"Error fetching team {team_id}: {e}", flush=True)

# Also check 'titled-players'
team_id_2 = 'titled-players'
try:
    print(f"Checking team: {team_id_2}...", flush=True)
    team = client.teams.get(team_id_2)
    print(f"Team found: {team.get('name')}", flush=True)
    print(f"Members count: {team.get('nbMembers')}", flush=True)
except Exception as e:
    print(f"Error fetching team {team_id_2}: {e}", flush=True)
