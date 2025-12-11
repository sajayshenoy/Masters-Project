import berserk
import os
import pandas as pd
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(env_path)
API_KEY = os.getenv("lichess_api_key")
session = berserk.TokenSession(API_KEY) if API_KEY else None
client = berserk.Client(session=session)

print("Dirs of client.users:", dir(client.users))

csv_path = "data/lichess_titled_players.csv"
if os.path.exists(csv_path):
    print(f"CSV size: {os.path.getsize(csv_path)} bytes")
    try:
        df = pd.read_csv(csv_path)
        print(f"CSV rows: {len(df)}")
        print("Columns:", df.columns.tolist())
    except Exception as e:
        print(f"Error reading CSV: {e}")
else:
    print("CSV not found.")
