"""
Enhanced Sample Collection for RQ1
===================================
Extract additional games from all Lichess Elite PGN files to:
1. Increase female opponent sample size
2. Create matched samples (rating bins) for more rigorous RQ1 analysis
3. Preserve strategic comparability

Process:
- Parse all 79 PGN files for games with female players
- Extract game metadata + player info
- Merge with unified player gender data
- Create stratified matched samples by rating
"""

import pandas as pd
import glob
import re
import numpy as np
from io import StringIO
import warnings
warnings.filterwarnings('ignore')

print("=" * 70)
print("ENHANCED SAMPLE COLLECTION FOR RQ1")
print("=" * 70)

# Load player gender mapping
df_players = pd.read_csv('data/unified_chess_players_with_inferred_gender.csv')
player_gender_map = dict(zip(df_players['name'], df_players['sex']))

# Also create lowercase/variant mappings for Lichess usernames
lichess_name_map = {}
for idx, row in df_players.iterrows():
    if pd.notna(row['lichess_username']):
        lichess_name_map[row['lichess_username'].lower()] = row['sex']

print(f"\nPlayer gender map loaded: {len(player_gender_map)} players from unified dataset")
print(f"Lichess username mappings: {len(lichess_name_map)} users")

# ============= PARSE PGN FILES =============
print("\n" + "=" * 70)
print("PARSING LICHESS ELITE PGN FILES")
print("=" * 70)

pgn_dir = "data/Lichess Elite Database/"
pgn_files = sorted(glob.glob(f"{pgn_dir}*.pgn"))

print(f"\nFound {len(pgn_files)} PGN files")

all_games = []
games_with_female = 0
parse_errors = 0

for pgn_idx, pgn_file in enumerate(pgn_files):
    filename = pgn_file.split('\\')[-1]
    
    try:
        with open(pgn_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Split by game records (look for [Event) marker
        games = re.split(r'\n\n\[Event', content)
        
        for game_id, game_text in enumerate(games):
            if not game_text.strip():
                continue
            
            # Re-add [Event for all but first
            if game_id > 0:
                game_text = '[Event' + game_text
            
            # Extract PGN headers
            white_match = re.search(r'\[White\s+"([^"]+)"\]', game_text)
            black_match = re.search(r'\[Black\s+"([^"]+)"\]', game_text)
            elo_white = re.search(r'\[WhiteElo\s+"?(\d+)"?\]', game_text)
            elo_black = re.search(r'\[BlackElo\s+"?(\d+)"?\]', game_text)
            result = re.search(r'\[Result\s+"([^"]+)"\]', game_text)
            site = re.search(r'\[Site\s+"([^"]+)"\]', game_text)
            moves = re.search(r'\](.*?)$', game_text.replace('\n', ' '), re.DOTALL)
            
            if not (white_match and black_match and elo_white and elo_black):
                continue
            
            white_name = white_match.group(1).strip()
            black_name = black_match.group(1).strip()
            white_elo = int(elo_white.group(1))
            black_elo = int(elo_black.group(1))
            
            # Extract move count (ply count) from moves
            movetext = moves.group(1).strip() if moves else ""
            ply_count = len(movetext.split())  # Rough count; official would require full parsing
            
            # Get gender for white player
            white_sex = None
            if white_name in player_gender_map:
                white_sex = player_gender_map[white_name]
            elif white_name.lower() in lichess_name_map:
                white_sex = lichess_name_map[white_name.lower()]
            
            # Get gender for black player
            black_sex = None
            if black_name in player_gender_map:
                black_sex = player_gender_map[black_name]
            elif black_name.lower() in lichess_name_map:
                black_sex = lichess_name_map[black_name.lower()]
            
            # Only store games where at least one player has gender info
            # and at least one is female
            if (white_sex or black_sex) and (white_sex == 'F' or black_sex == 'F'):
                games_with_female += 1
                
                all_games.append({
                    'White': white_name,
                    'Black': black_name,
                    'White_Elo': white_elo,
                    'Black_Elo': black_elo,
                    'White_Sex': white_sex if white_sex else 'unknown',
                    'Black_Sex': black_sex if black_sex else 'unknown',
                    'Result': result.group(1) if result else None,
                    'Site': site.group(1) if site else pgn_file,
                    'PlyCount': ply_count,
                    'RatingDiff': white_elo - black_elo,
                    'Pairing': f"{white_sex if white_sex else '?'} vs {black_sex if black_sex else '?'}"
                })
        
        if (pgn_idx + 1) % 20 == 0:
            print(f"  Processed {pgn_idx + 1}/{len(pgn_files)} files... ({games_with_female} games with females so far)")
    
    except Exception as e:
        parse_errors += 1
        if pgn_idx < 5:  # Print first few errors only
            print(f"  Error in {filename}: {str(e)[:80]}")

print(f"\n✓ Parsing complete!")
print(f"  Total games found with female players: {games_with_female:,}")
print(f"  Parse errors: {parse_errors}")

# ============= CREATE DATAFRAME =============
print("\n" + "=" * 70)
print("EXTRACTED GAMES SUMMARY")
print("=" * 70)

df_extracted = pd.DataFrame(all_games)

print(f"\nTotal games extracted: {len(df_extracted):,}")

pairing_dist = df_extracted['Pairing'].value_counts()
print(f"\nDistribution by gender pairing:")
for pairing, count in pairing_dist.items():
    print(f"  {pairing:20s}: {count:>6,} ({count/len(df_extracted)*100:>5.1f}%)")

# ============= MERGE WITH EXISTING DATA =============
print("\n" + "=" * 70)
print("MERGING WITH EXISTING RQ1 DATA")
print("=" * 70)

# Load existing RQ1 games
df_existing = pd.read_csv('data/rq1_behavior_analysis.csv')
print(f"\nExisting RQ1 games: {len(df_existing):,}")

# Check for gender mapping in existing data
print(f"Existing columns: {df_existing.columns.tolist()}")

# Filter extracted to match existing structure
# Existing has: White_Unified_Name, Black_Sex, PlyCount, RatingDiff, Opening, IsAggressive
# We need to match this format

# For now, extract key columns that match
df_extracted_subset = df_extracted[[
    'White', 'Black_Sex', 'PlyCount', 'RatingDiff', 'White_Elo'
]].copy()

df_extracted_subset.columns = ['White_Unified_Name', 'Black_Sex', 'PlyCount', 'RatingDiff', 'White_Elo']

# Filter to games where we have clear gender info
df_extracted_subset = df_extracted_subset[
    (df_extracted_subset['Black_Sex'].isin(['M', 'F'])) & 
    (df_extracted_subset['White_Unified_Name'].notna())
].copy()

# Drop duplicates (same player, very similar stats)
df_extracted_subset = df_extracted_subset.drop_duplicates(
    subset=['White_Unified_Name', 'Black_Sex', 'White_Elo', 'RatingDiff'],
    keep='first'
)

print(f"\nExtracted subset after filtering: {len(df_extracted_subset):,} games")

# Add missing opening column (mark as 'Unknown' for now)
df_extracted_subset['Opening'] = 'Unknown'
df_extracted_subset['IsAggressive'] = False  # Default; would need ECO parsing

# ============= CREATE MATCHED SAMPLES =============
print("\n" + "=" * 70)
print("CREATING MATCHED SAMPLES (RATING BINS)")
print("=" * 70)

# Combine existing + new
df_all_games = pd.concat([df_existing, df_extracted_subset], ignore_index=True)

# Remove duplicates
df_all_games = df_all_games.drop_duplicates(
    subset=['White_Unified_Name', 'Black_Sex'],
    keep='first'
)

print(f"\nTotal combined games: {len(df_all_games):,}")

pairing_counts = df_all_games['Black_Sex'].value_counts()
print(f"\nGames by opponent gender:")
print(f"  Male opponents: {pairing_counts.get('M', 0):>6,}")
print(f"  Female opponents: {pairing_counts.get('F', 0):>6,}")

# Create rating bins for matching
df_all_games['RatingBin'] = pd.cut(
    df_all_games['RatingDiff'],
    bins=[-np.inf, -100, -50, 0, 50, 100, np.inf],
    labels=['<-100', '-100:-50', '-50:0', '0:50', '50:100', '>100']
)

print(f"\nRating difference distribution:")
print(df_all_games['RatingBin'].value_counts().sort_index())

# For RQ1 focus: extract Male vs Female and Male vs Male in matched bins
df_mvf = df_all_games[df_all_games['Black_Sex'] == 'F'].copy()
df_mvm = df_all_games[df_all_games['Black_Sex'] == 'M'].copy()

print(f"\n" + "=" * 70)
print("MATCHED SAMPLE CREATION")
print("=" * 70)

print(f"\nMale vs Female games: {len(df_mvf):,}")
print(f"Male vs Male games: {len(df_mvm):,}")

# Create matched pairs by rating bin
matched_samples = []

for bin_label in ['<-100', '-100:-50', '-50:0', '0:50', '50:100', '>100']:
    mvf_bin = df_mvf[df_mvf['RatingBin'] == bin_label]
    mvm_bin = df_mvm[df_mvm['RatingBin'] == bin_label]
    
    # Take equal or up to max available
    n_match = min(len(mvf_bin), len(mvm_bin))
    
    if n_match > 0:
        matched_samples.append(mvf_bin.sample(n=n_match, random_state=42))
        matched_samples.append(mvm_bin.sample(n=n_match, random_state=42))
        
        print(f"  Bin {bin_label:12s}: {n_match:>4} MvF + {n_match:>4} MvM pairs")

df_matched = pd.concat(matched_samples, ignore_index=True)

print(f"\nTotal in matched sample: {len(df_matched):,}")
print(f"  MvF: {(df_matched['Black_Sex'] == 'F').sum():,}")
print(f"  MvM: {(df_matched['Black_Sex'] == 'M').sum():,}")

# ============= SAVE OUTPUTS =============
print("\n" + "=" * 70)
print("SAVING ENHANCED DATASETS")
print("=" * 70)

# Save all extracted games
df_extracted_subset.to_csv('analysis/extracted_games_from_pgn.csv', index=False)
print(f"✓ Saved: extracted_games_from_pgn.csv ({len(df_extracted_subset):,} games)")

# Save combined dataset
df_all_games.to_csv('data/rq1_behavior_analysis_expanded.csv', index=False)
print(f"✓ Saved: rq1_behavior_analysis_expanded.csv ({len(df_all_games):,} games)")

# Save matched sample
df_matched.to_csv('analysis/rq1_matched_sample_by_rating.csv', index=False)
print(f"✓ Saved: rq1_matched_sample_by_rating.csv ({len(df_matched):,} games)")

# ============= GENERATE COMPARISON STATS =============
print("\n" + "=" * 70)
print("SAMPLE SIZE COMPARISON")
print("=" * 70)

comparison = pd.DataFrame({
    'Dataset': ['Original RQ1', 'Expanded (New PGNs)', 'Combined', 'Matched Sample'],
    'Total_Games': [
        len(df_existing),
        len(df_extracted_subset),
        len(df_all_games),
        len(df_matched)
    ],
    'Female_Opp_Games': [
        (df_existing['Black_Sex'] == 'F').sum(),
        (df_extracted_subset['Black_Sex'] == 'F').sum(),
        (df_all_games['Black_Sex'] == 'F').sum(),
        (df_matched['Black_Sex'] == 'F').sum()
    ]
})

# Calculate percentages
for col in ['Total_Games', 'Female_Opp_Games']:
    comparison[f'{col}_Inc'] = (
        (comparison[col] / comparison.loc[0, col] - 1) * 100
    ).round(1)

comparison.to_csv('analysis/sample_expansion_summary.csv', index=False)

print("\n" + comparison.to_string(index=False))

# ============= VISUALIZATION =============
print("\n" + "=" * 70)
print("SUMMARY STATISTICS")
print("=" * 70)

print("\nMatched Sample Statistics (by rating bin):")
matched_by_bin = df_matched.groupby('RatingBin').agg({
    'Black_Sex': 'value_counts',
    'PlyCount': 'mean',
    'RatingDiff': 'mean'
})

print(f"\n✓ Extraction and matching complete!")
print(f"\nKey Achievements:")
print(f"  • Extracted {len(df_extracted_subset):,} new games from 79 PGN files")
print(f"  • Increased female opponent games by {((df_all_games[df_all_games['Black_Sex']=='F'].shape[0] / df_existing[df_existing['Black_Sex']=='F'].shape[0] - 1) * 100):.1f}%")
print(f"  • Created matched sample: {len(df_matched):,} games ({(df_matched['Black_Sex']=='F').sum():,} MvF, {(df_matched['Black_Sex']=='M').sum():,} MvM)")
print(f"\nNext Steps:")
print(f"  1. Run RQ1 analysis on matched_sample for bias-controlled comparison")
print(f"  2. Add opening ECO codes to extracted games (currently 'Unknown')")
print(f"  3. Parse moves to calculate precise ply counts and aggressiveness")
