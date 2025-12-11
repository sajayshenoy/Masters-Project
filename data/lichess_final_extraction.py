import berserk
import pandas as pd
import os
import time
from dotenv import load_dotenv

# Robust .env loading
env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(env_path)
if not os.getenv("lichess_api_key"):
    load_dotenv()

API_KEY = os.getenv("lichess_api_key")
session = berserk.TokenSession(API_KEY) if API_KEY else None
client = berserk.Client(session=session)

def get_unique_titled_players():
    unique_users = {}

    def add_user(user, source):
        # Handle different user object structures if necessary
        # User object from leaderboard vs team members might differ slightly
        username = user.get('username') or user.get('id')
        if not username: return

        if username not in unique_users:
            # Basic info
            user_data = {
                'id': user.get('id'),
                'username': username,
                'title': user.get('title'),
                'online': user.get('online'),
                'patron': user.get('patron'),
                'perfs': user.get('perfs'),
                'source': source
            }
            # Only add if they have a title (double check)
            if user_data['title']: 
                unique_users[username] = user_data
    
    # 1. Scraping Leaderboards
    print("\n--- Strategy 1: Scraping Leaderboards (Top 200) ---", flush=True)
    perfs = [
        "bullet", "blitz", "rapid", "classical", 
        "ultraBullet", "crazyhouse", "chess960", 
        "kingOfTheHill", "threeCheck", "antichess", 
        "atomic", "horde", "racingKings"
    ]

    for perf in perfs:
        print(f"  Fetching leaderboard for {perf}...", flush=True)
        try:
            leaderboard = client.users.get_leaderboard(perf, count=200)
            for user in leaderboard:
                add_user(user, f'leaderboard:{perf}')
        except Exception as e:
            print(f"  Error fetching {perf}: {e}", flush=True)
        time.sleep(1)

    # 2. Fetching recent Titled Arena participants
    # Generating IDs for Titled Arenas (LTA) and Titled 960 (960LTA) from 2018 to 2025.
    # Pattern: [mon][yy]lta (e.g. dec24lta) and maybe 960[mon][yy] (e.g. 960dec24 based on research)
    # Actually research said #960dec24, so ID might be '960dec24' or '960dec24lta'. 
    # We will try both '960[mon][yy]' and '960[mon][yy]lta' to be safe, skipping 404s.
    
    print("\n--- Strategy 2: Fetching Historic Titled Arena Participants (2018-2025) ---", flush=True)

    months = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
    years = range(18, 26) # 18 to 25
    
    arena_ids = []
    
    # Generate potential IDs
    for year in years:
        for month in months:
            # Standard: dec24lta
            arena_ids.append(f"{month}{year}lta")
            # 960: 960dec24 (guessing pattern based on '960dec24')
            arena_ids.append(f"960{month}{year}")
            # Try another variant just in case
            arena_ids.append(f"960{month}{year}lta")

    # Remove duplicates and future dates (simple check not needed, 404s handle it)
    print(f"Generated {len(arena_ids)} potential tournament IDs to scan...", flush=True)

    for i, arena_id in enumerate(arena_ids):
        # Progress every 10
        if i % 10 == 0:
             print(f"Scanning tournament {i}/{len(arena_ids)}...", flush=True)
            
        try:
            # client.tournaments.get_results returns a generator of participants
            # We wrap in list/loop. If tournament doesn't exist, it might raise exception immediately 
            # or return empty. stream_results might be better for bandwidth.
            # However, stream_results might fail if ID is invalid.
            results = client.tournaments.stream_results(arena_id)
            
            # Check if we get any data (generator doesn't start until iterated)
            count = 0
            found_any = False
            for user in results:
                found_any = True
                if user.get('title'): 
                     add_user(user, f'arena:{arena_id}')
                     count += 1
            
            if found_any:
                print(f"    Found {count} titled players in {arena_id}", flush=True)
            # else: 
            #    print(f"    No data/Invalid ID: {arena_id}", flush=True)

        except Exception as e:
            # Ignore 404s (invalid IDs) silently or concise
            # print(f"    Error {arena_id}: {e}", flush=True)
            pass


    for perf in perfs:
        print(f"  Fetching leaderboard for {perf}...", flush=True)
        try:
            leaderboard = client.users.get_leaderboard(perf, count=200)
            for user in leaderboard:
                add_user(user, f'leaderboard:{perf}')
        except Exception as e:
            print(f"  Error fetching {perf}: {e}", flush=True)
        time.sleep(1)

    total_titled = len(unique_users)
    print(f"\nTotal unique titled players found: {total_titled}", flush=True)
    
    return pd.DataFrame(unique_users.values())

if __name__ == "__main__":
    if API_KEY:
        print("Using API Key.", flush=True)
    else:
        print("WARNING: No API Key found. Rate limits will be strict.", flush=True)

    df = get_unique_titled_players()
    
    if not df.empty:
        output_file = os.path.join("data", "lichess_titled_players.csv")
        df.to_csv(output_file, index=False)
        print(f"Saved to {output_file}", flush=True)
    else:
        print("No titled players extracted.", flush=True)
