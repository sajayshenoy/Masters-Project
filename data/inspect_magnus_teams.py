import berserk
import os
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(env_path)
API_KEY = os.getenv("lichess_api_key")
session = berserk.TokenSession(API_KEY) if API_KEY else None
client = berserk.Client(session=session)

username = 'DrNykterstein' # Magnus Carlsen
print(f"Fetching teams for {username}...", flush=True)
try:
    teams = client.teams.teams_of_player(username)
    for team in teams:
        print(f"ID: {team.get('id')} | Name: {team.get('name')} | Members: {team.get('nbMembers')}", flush=True)
except Exception as e:
    print(f"Error: {e}", flush=True)
