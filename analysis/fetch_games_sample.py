import pandas as pd
import requests
import berserk
import os
import time
import io
import chess.pgn

def fetch_openings_sample():
    # 1. Load Players
    input_file = os.path.join("data", "unified_chess_players.csv")
    print("Loading player data...", flush=True)
    # Specify dtypes to avoid mixed type warnings and improve loading speed
    dtype_spec = {
        'fide_id': str,
        'rating_fide': float,
        'chesscom_rating_blitz': float,
        'lichess_rating_blitz': float
    }
    df = pd.read_csv(input_file, low_memory=False, dtype=dtype_spec)
    
    # Filter for players with Lichess username and Known Gender
    df_sample = df.dropna(subset=['lichess_username', 'sex']).copy()
    
    # Sample 100 Men and 100 Women to stay within rate limits but get decent data
    # Selecting active players (e.g. high blitza rating or recently active if we had that data)
    # Let's simple sample random 100 of each
    
    start_time = time.time()
    
    sampled_players = []
    
    for sex in ['M', 'F']:
        sub = df_sample[df_sample['sex'] == sex]
        if len(sub) > 100:
            sample = sub.sample(100, random_state=42)
        else:
            sample = sub
        sampled_players.extend(sample.to_dict('records'))
        
    print(f"Selected {len(sampled_players)} players for opening analysis.", flush=True)

    # 2. Fetch Games
    games_data = []
    
    # Using requests for PGN export (berserk export_by_player returns generator of JSON usually, PGN is easier for chess lib)
    # Lichess endpoint: https://lichess.org/api/games/user/{username}?max=30&perfType=blitz&opening=true
    
    count = 0
    
    session = requests.Session()
    
    for p in sampled_players:
        username = p['lichess_username']
        sex = p['sex']
        
        # Rate limiting: Lichess is generous but let's be polite
        url = f"https://lichess.org/api/games/user/{username}"
        params = {
            'max': 30,
            'perfType': 'blitz',
            'opening': 'true',
            'pgnInJson': 'true' # or just PGN
        }
        # Actually standard PGN export is easiest
        # GET /api/games/user/{username}
        # headers Accept: application/x-chess-pgn
        
        try:
            resp = session.get(url, params=params, timeout=10)
            if resp.status_code == 200:
                pgn_text = resp.text
                
                # Parse PGN
                pgn_io = io.StringIO(pgn_text)
                
                while True:
                    game = chess.pgn.read_game(pgn_io)
                    if game is None:
                        break
                    
                    eco = game.headers.get("ECO", "?")
                    opening = game.headers.get("Opening", "?")
                    white = game.headers.get("White", "?")
                    black = game.headers.get("Black", "?")
                    
                    # Identify color of titled player
                    color = 'White' if white.lower() == username.lower() else 'Black'
                    
                    games_data.append({
                        'username': username,
                        'sex': sex,
                        'color': color,
                        'eco': eco,
                        'opening': opening
                    })
            else:
                print(f"Error {username}: {resp.status_code}", flush=True)

        except Exception as e:
            print(f"Exception {username}: {e}", flush=True)
            
        count += 1
        if count % 20 == 0:
             print(f"Fetched {count}/{len(sampled_players)}...", flush=True)
        
        time.sleep(0.5) # throttle

    print(f"Fetched {len(games_data)} games.", flush=True)
    
    # 3. Save
    out_df = pd.DataFrame(games_data)
    out_file = os.path.join("data", "openings_sample.csv")
    out_df.to_csv(out_file, index=False)
    print(f"Saved openings data to {out_file}", flush=True)

if __name__ == "__main__":
    fetch_openings_sample()
