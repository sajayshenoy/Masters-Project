import pandas as pd
import os
import re

def normalize_name(name):
    if not isinstance(name, str):
        return None
    # Remove accents/special chars if needed? For now just lower and strip.
    # Simple unidecode might be better but let's stick to standard lib if possible or simple string manip.
    name = name.lower().strip()
    return name

def normalize_fide_name(fide_name):
    # FIDE format: "Last, First" -> "First Last"
    if not isinstance(fide_name, str):
        return None
    if ',' in fide_name:
        parts = fide_name.split(',', 1)
        # "Smith, John" -> parts=['Smith', ' John'] -> "john smith"
        return f"{parts[1].strip().lower()} {parts[0].strip().lower()}"
    return fide_name.lower().strip()

def unify_data():
    fide_path = "data/fide_titled_players.csv"
    chesscom_path = "data/chesscom_unified_stats.csv"
    lichess_path = "data/lichess_unified_stats.csv"
    output_path = "data/unified_chess_players.csv"

    print("Loading datasets...", flush=True)
    df_fide = pd.read_csv(fide_path)
    df_cc = pd.read_csv(chesscom_path)
    df_li = pd.read_csv(lichess_path)

    # Master dictionary: Key = Normalized Name (First Last)
    # Value = aggregated info
    # We also maintain a mapping of FIDE ID -> Data to ensure uniqueness for FIDE players.
    
    players = {}
    
    # 1. Process FIDE (The Base)
    print(f"Processing {len(df_fide)} FIDE records...", flush=True)
    for _, row in df_fide.iterrows():
        norm_name = normalize_fide_name(row['Name'])
        if not norm_name: continue
        
        player_entry = {
            'name': row['Name'], # Keep original FIDE name format? Or normalize? Let's keep original "Last, First" for FIDE col
            'normalized_name': norm_name,
            'fide_id': row['ID'],
            'federation': row['Fed'],
            'sex': row['Sex'],
            'title_fide': row['Title'],
            'rating_fide': row['Rating'],
            
            # Platform placeholders
            'chesscom_username': None,
            'chesscom_title': None,
            'chesscom_rating_blitz': None,
            'chesscom_rating_rapid': None,
            'chesscom_rating_bullet': None,
            
            'lichess_username': None,
            'lichess_title': None,
            'lichess_rating_blitz': None,
            'lichess_rating_rapid': None,
            'lichess_rating_bullet': None,
        }
        players[norm_name] = player_entry

    print(f"  Initialized {len(players)} FIDE profiles.", flush=True)

    # 2. Merge Chess.com
    print(f"Merging {len(df_cc)} Chess.com records...", flush=True)
    cc_matched = 0
    cc_new = 0
    for _, row in df_cc.iterrows():
        raw_name = row['name']
        norm_name = normalize_name(raw_name)
        
        # If no name in profile, skip matching (can't verify identity)
        # Unless we match by FIDE ID? Chess.com data doesn't have FIDE ID column usually, strict name match only.
        if not norm_name:
            # We can still add them if we want a complete list, but we can't link to FIDE.
            # User wants "comprehensive list", so we should include them as platform-only.
            pass
        
        entry = None
        if norm_name and norm_name in players:
            entry = players[norm_name]
            cc_matched += 1
        else:
            # New player (e.g. NM or name mismatch)
            entry = {
                'name': row['name'] if isinstance(row['name'], str) else row['username'], # Fallback to username for name
                'normalized_name': norm_name if norm_name else row['username'],
                'fide_id': None,
                'federation': row['country'], # Use CC country
                'sex': None,
                'title_fide': None, # We don't know
                'rating_fide': row['fide_rating'] if pd.notna(row['fide_rating']) else None,
                
                'chesscom_username': None, # will fill below
                # ... defaults
                'lichess_username': None,
                'lichess_title': None,
                'lichess_rating_blitz': None,
                'lichess_rating_rapid': None,
                'lichess_rating_bullet': None,
            }
            # Add to players map
            key = norm_name if norm_name else row['username']
            players[key] = entry
            cc_new += 1
        
        # Update Chess.com fields
        entry['chesscom_username'] = row['username']
        entry['chesscom_title'] = row['title']
        entry['chesscom_rating_blitz'] = row['blitz_rating']
        entry['chesscom_rating_rapid'] = row['rapid_rating']
        entry['chesscom_rating_bullet'] = row['bullet_rating']

    print(f"  Matched {cc_matched} to FIDE, Added {cc_new} new/unmatched from Chess.com.", flush=True)

    # 3. Merge Lichess
    print(f"Merging {len(df_li)} Lichess records...", flush=True)
    li_matched = 0
    li_new = 0
    for _, row in df_li.iterrows():
        raw_name = row['name']
        norm_name = normalize_name(raw_name)
        
        entry = None
        if norm_name and norm_name in players:
            entry = players[norm_name]
            li_matched += 1
        else:
            # Unique Lichess player
            entry = {
                'name': row['name'] if isinstance(row['name'], str) else row['username'],
                'normalized_name': norm_name if norm_name else row['username'],
                'fide_id': None,
                'federation': row['country'],
                'sex': None,
                'title_fide': None,
                'rating_fide': row['fide_rating'] if pd.notna(row['fide_rating']) else None,
                
                'chesscom_username': None,
                'chesscom_title': None,
                'chesscom_rating_blitz': None,
                'chesscom_rating_rapid': None,
                'chesscom_rating_bullet': None,
                
                'lichess_username': None,
                # ...
            }
            key = norm_name if norm_name else row['username']
            players[key] = entry
            li_new += 1
            
        # Update Lichess fields
        entry['lichess_username'] = row['username']
        entry['lichess_title'] = row['title']
        entry['lichess_rating_blitz'] = row['blitz_rating']
        entry['lichess_rating_rapid'] = row['rapid_rating']
        entry['lichess_rating_bullet'] = row['bullet_rating']

    print(f"  Matched {li_matched} to existing, Added {li_new} new from Lichess.", flush=True)

    # 4. Export
    final_df = pd.DataFrame(players.values())
    
    # Reorder columns for readability
    cols = [
        'name', 'federation', 'sex', 'title_fide', 'fide_id', 'rating_fide',
        'chesscom_username', 'chesscom_title', 'chesscom_rating_blitz', 'chesscom_rating_rapid', 'chesscom_rating_bullet',
        'lichess_username', 'lichess_title', 'lichess_rating_blitz', 'lichess_rating_rapid', 'lichess_rating_bullet'
    ]
    # Ensure all cols exist
    for c in cols:
        if c not in final_df.columns:
            final_df[c] = None
            
    final_df = final_df[cols]
    final_df.to_csv(output_path, index=False)
    print(f"Successfully created unified dataset with {len(final_df)} unique players at {output_path}", flush=True)

if __name__ == "__main__":
    unify_data()
