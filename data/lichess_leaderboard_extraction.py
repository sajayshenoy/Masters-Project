import berserk
import pandas as pd
import os
import time
from dotenv import load_dotenv

# Load API key
env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(env_path)
if not os.getenv("lichess_api_key"):
    load_dotenv() # Try default

API_KEY = os.getenv("lichess_api_key")
session = berserk.TokenSession(API_KEY) if API_KEY else None
client = berserk.Client(session=session)

def get_leaderboard_players():
    # Lichess perf types
    perfs = [
        "bullet", "blitz", "rapid", "classical", 
        "ultrabullet", "crazyhouse", "chess960", 
        "kingOfTheHill", "threeCheck", "antichess", 
        "atomic", "horde", "racingKings"
    ]
    
    unique_users = {}
    
    print(f"Starting leaderboard extraction. API Key present: {bool(API_KEY)}", flush=True)

    for perf in perfs:
        print(f"Fetching top 200 for {perf}...", flush=True)
        try:
            # count=200 is usually the max for public leaderboard API
            leaderboard = client.users.get_leaderboard(perf, count=200)
            
            for user in leaderboard:
                username = user.get('username')
                if username not in unique_users:
                    # Filter for titled players ONLY
                    title = user.get('title')
                    if title:
                        unique_users[username] = {
                            'id': user.get('id'),
                            'username': username,
                            'title': title,
                            'online': user.get('online'),
                            'patron': user.get('patron'),
                            # Capture rating for the specific perf we found them in
                            f'rating_{perf}': user.get('perfs', {}).get(perf, {}).get('rating') 
                        }
                    # If user exists, maybe update with this perf's rating?
                    # For simplicity, just capturing the first occurrence's data + title
        except Exception as e:
            print(f"Error fetching {perf}: {e}", flush=True)
        
        time.sleep(1) # Be nice to API

    print(f"Found {len(unique_users)} unique titled players across all leaderboards.", flush=True)
    return pd.DataFrame(unique_users.values())

if __name__ == "__main__":
    df = get_leaderboard_players()
    if not df.empty:
        output_file = os.path.join("data", "lichess_titled_players.csv")
        df.to_csv(output_file, index=False)
        print(f"Saved to {output_file}", flush=True)
    else:
        print("No titled players found.", flush=True)
