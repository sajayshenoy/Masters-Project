import berserk
import pandas as pd
import os
import requests
import math
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(env_path)
API_KEY = os.getenv("lichess_api_key")

def enrich_lichess_users():
    input_file = os.path.join("data", "lichess_titled_players.csv")
    output_file = os.path.join("data", "lichess_unified_stats.csv")
    
    if not os.path.exists(input_file):
        print("Input file not found.")
        return

    df = pd.read_csv(input_file)
    print(f"Loaded Lichess CSV with {len(df)} rows.", flush=True)
    
    # Prefer username as it is always present (key in extraction dict)
    # id might be missing from some sources (like streamed tournament results)
    if 'username' in df.columns:
        users = df['username'].dropna().astype(str).tolist()
    elif 'id' in df.columns:
         users = df['id'].dropna().astype(str).tolist()
    else:
        print("Error: Neither 'username' nor 'id' column found.")
        return
    
    users = list(set(users))
    print(f"Enriching data for {len(users)} unique users...", flush=True)

    enriched_data = []
    chunk_size = 300
    headers = {'Authorization': f'Bearer {API_KEY}'} if API_KEY else {}

    total_chunks = math.ceil(len(users) / chunk_size)

    for i in range(0, len(users), chunk_size):
        chunk = users[i:i + chunk_size]
        print(f"Fetching chunk {i // chunk_size + 1}/{total_chunks}...", flush=True)
        
        try:
            # Use requests directly for bulk fetch (POST body = comma separated IDs)
            resp = requests.post('https://lichess.org/api/users', data=','.join(chunk), headers=headers)
            
            if resp.status_code != 200:
                print(f"  Error fetching chunk: {resp.status_code} - {resp.text}", flush=True)
                continue

            users_data = resp.json()
            
            for u in users_data:
                profile = u.get('profile', {})
                perfs = u.get('perfs', {})
                
                # correct name field is 'realName' usually, fallback to first/last if ever present
                # Use realName if present, else try constructing.
                real_name = profile.get('realName')
                if not real_name:
                     real_name = f"{profile.get('firstName', '')} {profile.get('lastName', '')}".strip()
                
                user_info = {
                    'username': u.get('username'),
                    'id': u.get('id'),
                    'title': u.get('title'),
                    'name': real_name if real_name else None,
                    'country': profile.get('country') or profile.get('flag'), # sometimes flag is used
                    'bio': profile.get('bio'),
                    # FIDE/USCF if linked
                    'fide_rating': profile.get('fideRating'),
                    'uscf_rating': profile.get('uscfRating'),
                    'ecf_rating': profile.get('ecfRating'),
                    
                    # Lichess Ratings
                    'blitz_rating': perfs.get('blitz', {}).get('rating'),
                    'blitz_prog': perfs.get('blitz', {}).get('prog'),
                    'blitz_games': perfs.get('blitz', {}).get('games'),
                    
                    'rapid_rating': perfs.get('rapid', {}).get('rating'),
                    'rapid_prog': perfs.get('rapid', {}).get('prog'),
                    'rapid_games': perfs.get('rapid', {}).get('games'),
                    
                    'bullet_rating': perfs.get('bullet', {}).get('rating'),
                    'classical_rating': perfs.get('classical', {}).get('rating'),
                    
                    'url': u.get('url'),
                    'verified': u.get('verified')
                }
                enriched_data.append(user_info)

        except Exception as e:
            print(f"  Exception in chunk: {e}", flush=True)

    if enriched_data:
        new_df = pd.DataFrame(enriched_data)
        new_df.to_csv(output_file, index=False)
        print(f"Saved enriched data to {output_file} ({len(new_df)} records)", flush=True)
    else:
        print("No data enriched.", flush=True)

if __name__ == "__main__":
    enrich_lichess_users()
