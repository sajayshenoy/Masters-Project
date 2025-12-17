import pandas as pd
import requests
import os
import time
import json

def fetch_detailed_games():
    """
    Fetches detailed game data including PGN moves, clocks, and available analysis.
    Focuses on Lichess first as they provide analysis (acpl) and clock data more easily.
    """
    # --- PATH FIX ---
    # Get the directory where this script is located (data_extraction_code)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Go up one level to Project Root (Masters-Project)
    project_root = os.path.dirname(script_dir)
    # Build path to data folder
    data_dir = os.path.join(project_root, "data")
    
    input_file = os.path.join(data_dir, "unified_chess_players.csv")
    out_file = os.path.join(data_dir, "detailed_games_sample.csv")
    # ----------------
    
    if not os.path.exists(input_file):
        print(f"Error: Could not find input file at: {input_file}")
        return

    print(f"Loading players from: {input_file}")
    df = pd.read_csv(input_file, low_memory=False)
    
    # Filter: Players with known gender and Lichess ID
    # Sampling: 50 active men and 50 active women for the pilot (expand later)
    df_sample = df.dropna(subset=['lichess_username', 'sex']).copy()
    
    target_players = []
    for sex in ['M', 'F']:
        # Prefer players with higher game counts if available, or just random
        subset = df_sample[df_sample['sex'] == sex]
        if len(subset) > 50:
            target_players.extend(subset.sample(50, random_state=42).to_dict('records'))
        else:
            target_players.extend(subset.to_dict('records'))

    detailed_games = []
    
    session = requests.Session()
    headers = {'Accept': 'application/x-ndjson'} # Lichess specific for streaming
    
    print(f"Fetching games for {len(target_players)} players...", flush=True)
    
    for i, player in enumerate(target_players):
        username = player['lichess_username']
        sex = player['sex']
        
        # Fetch last 20 Blitz games with analysis (evals=true) and clocks (clocks=true)
        url = f"https://lichess.org/api/games/user/{username}"
        params = {
            'max': 20,
            'perfType': 'blitz',
            'evals': 'true', 
            'clocks': 'true',
            'opening': 'true',
            'pgnInJson': 'true' 
        }
        
        try:
            # Lichess streaming response
            resp = session.get(url, params=params, headers=headers, timeout=15)
            
            # NDJSON parsing
            for line in resp.iter_lines():
                if not line: continue
                try:
                    game_json = json.loads(line)
                except json.JSONDecodeError:
                    continue
                
                # Extract Metrics
                
                # 1. Basic Metadata
                game_id = game_json.get('id')
                white = game_json.get('players', {}).get('white', {})
                black = game_json.get('players', {}).get('black', {})
                
                is_white = (white.get('user', {}).get('name', '').lower() == username.lower())
                opponent = black if is_white else white
                
                # 2. Decision Quality (ACPL)
                # Lichess provides 'analysis' field if available
                my_analysis = white.get('analysis') if is_white else black.get('analysis')
                acpl = my_analysis.get('acpl') if my_analysis else None
                
                # 3. Resignation / Termination
                status = game_json.get('status') # e.g., 'resign', 'mate', 'outoftime'
                winner = game_json.get('winner') # 'white' or 'black'
                won = (winner == 'white' and is_white) or (winner == 'black' and not is_white)
                
                # 4. Opening
                opening = game_json.get('opening', {})
                eco = opening.get('eco')
                opening_name = opening.get('name')
                
                # 5. Time Allocation
                # Simplified: Total moves
                move_list = game_json.get('moves', '').split()
                total_moves = len(move_list) // 2 # Approx full moves
                
                detailed_games.append({
                    'player_username': username,
                    'player_sex': sex,
                    'game_id': game_id,
                    'opponent_rating': opponent.get('rating'),
                    'opponent_id': opponent.get('user', {}).get('name'), 
                    'is_white': is_white,
                    'won': won,
                    'status': status,
                    'total_moves': total_moves,
                    'acpl': acpl, # Key for RQ1 Decision Quality
                    'eco': eco,
                    'opening_name': opening_name,
                    'timestamp': game_json.get('createdAt'),
                    'moves':game_json.get('moves')
                })
                
        except Exception as e:
            print(f"Error fetching {username}: {e}")
            
        time.sleep(1) # Polite delay
        if i % 10 == 0:
            print(f"Processed {i}/{len(target_players)} players...", flush=True)

    # Save
    if detailed_games:
        df_games = pd.DataFrame(detailed_games)
        df_games.to_csv(out_file, index=False)
        print(f"Saved {len(df_games)} detailed game records to {out_file}")
    else:
        print("No games extracted. Check API connection or player list.")

if __name__ == "__main__":
    fetch_detailed_games()