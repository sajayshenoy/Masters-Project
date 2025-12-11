import pandas as pd
import requests
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

def get_chesscom_data(usernames, output_file):
    print(f"Starting enrichment for {len(usernames)} players...", flush=True)
    
    session = requests.Session()
    # Good practice headers
    session.headers.update({
        'User-Agent': 'MastersProjectResearch/1.0 (sajayshenoy@example.com)'
    })
    
    enriched_data = []
    
    # Process in batches to save progress?
    # Or just write at the end.
    
    # Helper function for a single user
    def fetch_user(username):
        try:
            # 1. Profile
            url_profile = f"https://api.chess.com/pub/player/{username}"
            resp = session.get(url_profile, timeout=10)
            
            if resp.status_code == 429: # Rate limit
                time.sleep(2)
                resp = session.get(url_profile, timeout=10)
            
            if resp.status_code != 200:
                return None
            
            profile = resp.json()
            
            # 2. Stats
            url_stats = f"https://api.chess.com/pub/player/{username}/stats"
            resp_stats = session.get(url_stats, timeout=10)
            stats = {}
            if resp_stats.status_code == 200:
                stats = resp_stats.json()
            
            # Extract basic country code from url
            # e.g. https://api.chess.com/pub/country/US -> US
            country_code = None
            if profile.get('country'):
                country_code = profile.get('country').split('/')[-1]

            return {
                'username': username,
                'player_id': profile.get('player_id'),
                'name': profile.get('name'),
                'title': profile.get('title'),
                'followers': profile.get('followers'),
                'country': country_code,
                'location': profile.get('location'),
                'status': profile.get('status'),
                
                # Ratings
                'rapid_rating': stats.get('chess_rapid', {}).get('last', {}).get('rating'),
                'blitz_rating': stats.get('chess_blitz', {}).get('last', {}).get('rating'),
                'bullet_rating': stats.get('chess_bullet', {}).get('last', {}).get('rating'),
                'fide_rating': stats.get('fide'), # Sometimes present
                'puzzle_rating': stats.get('tactics', {}).get('highest', {}).get('rating'),
            }
        except Exception as e:
            # print(f"Error {username}: {e}", flush=True)
            return None

    # Use ThreadPool
    # Max 3-5 workers to be safe with Chess.com
    max_workers = 5
    count = 0
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_user = {executor.submit(fetch_user, user): user for user in usernames}
        
        for future in as_completed(future_to_user):
            res = future.result()
            if res:
                enriched_data.append(res)
            
            count += 1
            if count % 100 == 0:
                print(f"Processed {count}/{len(usernames)}...", flush=True)
                
    # Save
    df = pd.DataFrame(enriched_data)
    df.to_csv(output_file, index=False)
    print(f"Saved {len(df)} enriched records to {output_file}", flush=True)

if __name__ == "__main__":
    input_file = os.path.join("data", "chesscom_titled_players.csv")
    output_file = os.path.join("data", "chesscom_unified_stats.csv")
    
    if os.path.exists(input_file):
        df = pd.read_csv(input_file)
        if 'username' in df.columns:
            users = df['username'].tolist()
            get_chesscom_data(users, output_file)
        else:
             print("Column 'username' not found in input.")
    else:
        print("Input file not found.")
