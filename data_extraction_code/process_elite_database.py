import os
import csv
import chess.pgn
import pandas as pd
import glob
from datetime import datetime

# Paths
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
ELITE_DB_DIR = os.path.join(DATA_DIR, 'Lichess Elite Database')
UNIFIED_CSV_PATH = os.path.join(DATA_DIR, 'unified_chess_players.csv')
OUTPUT_CSV_PATH = os.path.join(DATA_DIR, 'elite_games_processed.csv')

def load_titled_lichess_usernames():
    """
    Loads unified_chess_players.csv and returns a dictionary mapping 
    lichess_username (lowercase) -> {'name': ..., 'title': ..., 'sex': ...}
    """
    print(f"Loading titled players from {UNIFIED_CSV_PATH}...")
    df = pd.read_csv(UNIFIED_CSV_PATH, low_memory=False)
    
    # Filter for players with a Lichess username
    df_lichess = df.dropna(subset=['lichess_username']).copy()
    
    # Create dictionary
    players = {}
    for _, row in df_lichess.iterrows():
        username = str(row['lichess_username']).lower().strip()
        
        # Determine best title
        title = row['title_fide']
        if pd.isna(title):
            title = row['lichess_title']
            
        players[username] = {
            'name': row['name'],
            'title': title,
            'sex': row['sex'],
            'fide_id': row['fide_id']
        }
    
    print(f"Found {len(players)} titled players with Lichess accounts.")
    return players

def process_all_pgns(titled_players_map):
    """
    Iterates through all .pgn files in ELITE_DB_DIR, filters games, and writes to CSV.
    """
    if not os.path.exists(ELITE_DB_DIR):
        print(f"Error: Directory not found: {ELITE_DB_DIR}")
        return

    pgn_files = sorted(glob.glob(os.path.join(ELITE_DB_DIR, "*.pgn")))
    if not pgn_files:
        print(f"No .pgn files found in {ELITE_DB_DIR}")
        print(f"Directory contents: {os.listdir(ELITE_DB_DIR) if os.path.exists(ELITE_DB_DIR) else 'Dir not found'}")
        return

    print(f"Found {len(pgn_files)} PGN files to process.")
    
    processed_files = set()
    open_mode = 'w'
    
    if os.path.exists(OUTPUT_CSV_PATH):
        print(f"Output file found at {OUTPUT_CSV_PATH}. Checking for processed games...")
        try:
            df_existing = pd.read_csv(OUTPUT_CSV_PATH, usecols=['SourceFile'])
            if not df_existing.empty:
                processed_files = set(df_existing['SourceFile'].unique())
                print(f"Found {len(processed_files)} already processed PGN files. Resuming...")
                open_mode = 'a'
            else:
                print("Output file is empty. Starting fresh.")
        except Exception as e:
            print(f"Warning: Could not read existing file ({e}). Starting fresh.")

    with open(OUTPUT_CSV_PATH, open_mode, newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            'GameID', 'Event', 'Site', 'Date', 'Round', 
            'White', 'Black', 'Result', 'ECO', 'Opening',
            'Termination', 'TimeControl', 
            'WhiteElo', 'BlackElo', 'WhiteRatingDiff', 'BlackRatingDiff',
            'WhiteTitle', 'BlackTitle', 'White_Is_Titled', 'Black_Is_Titled',
            'White_Unified_Name', 'Black_Unified_Name',
            'White_Sex', 'Black_Sex',
            'SourceFile', 'PlyCount'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        if open_mode == 'w':
            writer.writeheader()
        
        total_games = 0
        total_matches = 0
        
        for pgn_path in pgn_files:
            base_name = os.path.basename(pgn_path)
            if base_name in processed_files:
                print(f"Skipping {base_name} (already processed).")
                continue

            print(f"Processing: {base_name}")
            file_game_count = 0
            file_match_count = 0
            
            with open(pgn_path, encoding='utf-8') as pgn_file:
                while True:
                    try:
                        game = chess.pgn.read_game(pgn_file)
                    except Exception as e:
                        print(f"Error reading game in {pgn_path}: {e}")
                        continue
                        
                    if game is None:
                        break
                    
                    file_game_count += 1
                    total_games += 1
                    
                    # Optional: Print progress every x games
                    if file_game_count % 10000 == 0:
                        print(f"  Processed {file_game_count} games in current file...")

                    headers = game.headers
                    white_user = headers.get('White', '').lower().strip()
                    black_user = headers.get('Black', '').lower().strip()
                    
                    white_info = titled_players_map.get(white_user)
                    black_info = titled_players_map.get(black_user)
                    
                    if white_info or black_info:
                        file_match_count += 1
                        total_matches += 1
                        
                        try:
                            ply_count = game.end().ply()
                        except:
                            ply_count = None

                        row = {
                            'GameID': headers.get('Site', '').split('/')[-1],
                            'Event': headers.get('Event', ''),
                            'Site': headers.get('Site', ''),
                            'Date': headers.get('Date', ''),
                            'Round': headers.get('Round', ''),
                            'White': headers.get('White', ''),
                            'Black': headers.get('Black', ''),
                            'Result': headers.get('Result', ''),
                            'ECO': headers.get('ECO', ''),
                            'Opening': headers.get('Opening', ''),
                            'Termination': headers.get('Termination', ''),
                            'TimeControl': headers.get('TimeControl', ''),
                            'WhiteElo': headers.get('WhiteElo', ''),
                            'BlackElo': headers.get('BlackElo', ''),
                            'WhiteRatingDiff': headers.get('WhiteRatingDiff', ''),
                            'BlackRatingDiff': headers.get('BlackRatingDiff', ''),
                            
                            'White_Is_Titled': bool(white_info),
                            'Black_Is_Titled': bool(black_info),
                            
                            'WhiteTitle': white_info['title'] if white_info else None,
                            'BlackTitle': black_info['title'] if black_info else None,
                            'White_Unified_Name': white_info['name'] if white_info else None,
                            'Black_Unified_Name': black_info['name'] if black_info else None,
                            'White_Sex': white_info['sex'] if white_info else None,
                            'Black_Sex': black_info['sex'] if black_info else None,
                            'SourceFile': os.path.basename(pgn_path),
                            'PlyCount': ply_count
                        }

                        writer.writerow(row)
            
            print(f"  Finished {os.path.basename(pgn_path)}: {file_game_count} games, {file_match_count} matches.")

    print(f"All done! Total games processed: {total_games}. Total matches found: {total_matches}. Output: {OUTPUT_CSV_PATH}")

def main():
    titled_map = load_titled_lichess_usernames()
    process_all_pgns(titled_map)

if __name__ == "__main__":
    main()
