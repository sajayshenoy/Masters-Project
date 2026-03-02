"""
Comprehensive Lichess Elite Game Extraction
=============================================
Parse ALL 79 PGN files to extract:
- Game metadata (white, black, elos, result)
- Move sequences & ply counts
- Opening ECO codes
- Player genders (confirmed + inferred)

Creates three gender pairing categories:
1. Male vs Female (confirmed gender)
2. Male vs Perceived Female (inferred/unconfirmed)
3. Male vs Male (confirmed)

Output: Large dataset for RQ1 analysis across all available games
"""

import pandas as pd
import glob
import re
import numpy as np
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')

try:
    import gender_guesser.detector as gender_detector
    detector = gender_detector.Detector(case_sensitive=False)
except Exception:
    detector = None

print("=" * 80)
print("COMPREHENSIVE LICHESS ELITE GAME EXTRACTION")
print("=" * 80)

# Load gender data
print("\nLoading player gender mappings...")
df_players = pd.read_csv('data/unified_chess_players_with_inferred_gender.csv')

def extract_first_token(name_or_username):
    if pd.isna(name_or_username):
        return None
    text = str(name_or_username).strip()
    if not text:
        return None

    if ',' in text:
        after_comma = text.split(',', 1)[1].strip()
        tokens = re.findall(r'[A-Za-z]+', after_comma)
    else:
        tokens = re.findall(r'[A-Za-z]+', text)

    if not tokens:
        return None

    token = tokens[0].lower()
    return token if len(token) >= 2 else None

# Create gender lookups from UNIFIED dataset
# Match both FIDE names and Lichess usernames
gender_confirmed = {}  # From FIDE (sex = M or F)
gender_inferred = {}   # From algorithm (any classification)

male_first_names = set()
female_first_names = set()

for idx, row in df_players.iterrows():
    sex = row['sex']

    first_name = extract_first_token(row.get('name'))
    if first_name and sex == 'M':
        male_first_names.add(first_name)
    if first_name and sex == 'F':
        female_first_names.add(first_name)
    
    # Map by FIDE name (primary matching)
    if pd.notna(row['name']):
        name_lower = str(row['name']).strip().lower()
        if sex in ['M', 'F']:
            gender_confirmed[name_lower] = sex
        if sex in ['M', 'F', 'unknown']:
            gender_inferred[name_lower] = sex
    
    # Map by Lichess username (secondary matching for Lichess games)
    if pd.notna(row['lichess_username']):
        lichess_lower = str(row['lichess_username']).strip().lower()
        if sex in ['M', 'F']:
            gender_confirmed[lichess_lower] = sex
        if sex in ['M', 'F', 'unknown']:
            gender_inferred[lichess_lower] = sex

print(f"Confirmed gender mappings: {len(gender_confirmed)} players")
print(f"Inferred gender mappings: {len(gender_inferred)} players")

exclusive_female_names = female_first_names - male_first_names
exclusive_male_names = male_first_names - female_first_names

print(f"Exclusive female first-name priors: {len(exclusive_female_names)}")
print(f"Exclusive male first-name priors: {len(exclusive_male_names)}")

def infer_gender_from_username(username):
    token = extract_first_token(username)
    if not token:
        return None

    if token in exclusive_female_names:
        return 'F'
    if token in exclusive_male_names:
        return 'M'

    if detector:
        pred = detector.get_gender(token)
        if pred in ['female', 'mostly_female']:
            return 'F'
        if pred in ['male', 'mostly_male']:
            return 'M'

    return None

# ============= PARSE ALL PGN FILES =============
print("\n" + "=" * 80)
print("PARSING ALL LICHESS ELITE PGN FILES")
print("=" * 80)

pgn_dir = "data/Lichess Elite Database/"
pgn_files = sorted(glob.glob(f"{pgn_dir}*.pgn"))

print(f"\nFound {len(pgn_files)} PGN files")

all_games = []
games_by_source = defaultdict(int)
gender_coverage = {'both': 0, 'white_only': 0, 'black_only': 0, 'neither': 0}
total_games_with_headers = 0

for pgn_idx, pgn_file in enumerate(pgn_files):
    filename = pgn_file.split('\\')[-1]
    
    try:
        with open(pgn_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Split by game records
        games = re.split(r'\n\n\[Event', content)
        
        for game_id, game_text in enumerate(games):
            if not game_text.strip():
                continue
            
            # Re-add [Event for parsing
            if game_id > 0:
                game_text = '[Event' + game_text
            
            # Extract PGN headers
            white_match = re.search(r'\[White\s+"([^"]+)"\]', game_text)
            black_match = re.search(r'\[Black\s+"([^"]+)"\]', game_text)
            elo_white = re.search(r'\[WhiteElo\s+"?(\d+)"?\]', game_text)
            elo_black = re.search(r'\[BlackElo\s+"?(\d+)"?\]', game_text)
            result = re.search(r'\[Result\s+"([^"]+)"\]', game_text)
            eco = re.search(r'\[ECO\s+"([^"]+)"\]', game_text)
            opening_name = re.search(r'\[Opening\s+"([^"]+)"\]', game_text)
            date_match = re.search(r'\[UTCDate\s+"([^"]+)"\]', game_text)
            
            if not (white_match and black_match and elo_white and elo_black):
                continue

            total_games_with_headers += 1
            
            white_name = white_match.group(1).strip()
            black_name = black_match.group(1).strip()
            white_elo = int(elo_white.group(1))
            black_elo = int(elo_black.group(1))
            
            # Extract move text (everything after last ']')
            moves_match = re.search(r'\]([^\]]*?)(\s+[0-1]/2|\s*$)', game_text, re.DOTALL)
            movetext = moves_match.group(1).strip() if moves_match else ""
            
            # Count plies (rough: each token is approximately one ply)
            # More accurate would be to parse full notation but this is close
            move_tokens = movetext.split()
            ply_count = len([m for m in move_tokens if m and not m[0].isdigit()])
            
            # Get gender info
            white_name_lower = white_name.lower()
            black_name_lower = black_name.lower()
            
            # Try to find gender in confirmed data (FIDE or Lichess match)
            white_sex = gender_confirmed.get(white_name_lower)
            black_sex = gender_confirmed.get(black_name_lower)
            
            white_source = 'confirmed' if white_sex else 'unknown'
            black_source = 'confirmed' if black_sex else 'unknown'
            
            # If not found in confirmed, try inferred
            if not white_sex and white_name_lower in gender_inferred:
                inferred_sex = gender_inferred[white_name_lower]
                if inferred_sex in ['M', 'F']:  # Only use if actually inferred, not 'unknown'
                    white_sex = inferred_sex
                    white_source = 'inferred'

            # If still not found, infer from username tokens
            if not white_sex:
                inferred_from_username = infer_gender_from_username(white_name)
                if inferred_from_username in ['M', 'F']:
                    white_sex = inferred_from_username
                    white_source = 'inferred'
            
            if not black_sex and black_name_lower in gender_inferred:
                inferred_sex = gender_inferred[black_name_lower]
                if inferred_sex in ['M', 'F']:  # Only use if actually inferred, not 'unknown'
                    black_sex = inferred_sex
                    black_source = 'inferred'

            # If still not found, infer from username tokens
            if not black_sex:
                inferred_from_username = infer_gender_from_username(black_name)
                if inferred_from_username in ['M', 'F']:
                    black_sex = inferred_from_username
                    black_source = 'inferred'
            
            # Track gender coverage
            if white_sex and black_sex:
                gender_coverage['both'] += 1
            elif white_sex and not black_sex:
                gender_coverage['white_only'] += 1
            elif black_sex and not white_sex:
                gender_coverage['black_only'] += 1
            else:
                gender_coverage['neither'] += 1
            
            # Only store games where at least ONE player has gender info
            if white_sex or black_sex:
                all_games.append({
                    'White': white_name,
                    'Black': black_name,
                    'White_Elo': white_elo,
                    'Black_Elo': black_elo,
                    'White_Sex': white_sex if white_sex else 'unknown',
                    'White_Sex_Source': white_source,
                    'Black_Sex': black_sex if black_sex else 'unknown',
                    'Black_Sex_Source': black_source,
                    'Result': result.group(1) if result else '?',
                    'ECO': eco.group(1) if eco else 'Unknown',
                    'Opening': opening_name.group(1) if opening_name else 'Unknown',
                    'Date': date_match.group(1) if date_match else 'Unknown',
                    'PlyCount': ply_count,
                    'RatingDiff': white_elo - black_elo,
                    'File': filename
                })
        
        games_by_source[filename] = len(all_games)
        
        if (pgn_idx + 1) % 20 == 0:
            print(f"  Processed {pgn_idx + 1}/{len(pgn_files)} files... ({len(all_games):,} games with gender info)")
    
    except Exception as e:
        if pgn_idx < 5:
            print(f"  Error in {filename}: {str(e)[:60]}")

print(f"\n✓ Parsing complete!")
print(f"  Total games extracted: {len(all_games):,}")

# ============= GENDER COVERAGE ANALYSIS =============
print("\n" + "=" * 80)
print("GENDER INFORMATION COVERAGE")
print("=" * 80)

for category, count in gender_coverage.items():
    pct = count / total_games_with_headers * 100 if total_games_with_headers else 0
    print(f"  {category:15s}: {count:>7,} ({pct:>5.1f}%)")

# ============= CREATE DATAFRAME =============
print("\n" + "=" * 80)
print("CREATING ANALYSIS DATASET")
print("=" * 80)

df = pd.DataFrame(all_games)

print(f"\nDataset shape: {df.shape}")
print(f"Columns: {df.columns.tolist()}")

# ============= CREATE GENDER PAIRING CATEGORIES =============
print("\n" + "=" * 80)
print("GENDER PAIRING CATEGORIES")
print("=" * 80)

def assign_pairing(white_sex, white_source, black_sex, black_source):
    """
    Assign pairing category:
    1. Male vs Female (both confirmed)
    2. Male vs Perceived Female (at least one inferred)
    3. Male vs Male (both confirmed)
    4. Other (not analyzable)
    """
    
    # Only consider M and F, not 'unknown'
    if white_sex == 'unknown' or black_sex == 'unknown':
        return 'Other'
    
    # Must have white = M for our main comparisons
    if white_sex != 'M':
        return 'Other'
    
    if black_sex == 'F':
        if white_source == 'confirmed' and black_source == 'confirmed':
            return 'Male vs Female (Confirmed)'
        else:
            return 'Male vs Perceived Female (Inferred)'
    elif black_sex == 'M':
        if white_source == 'confirmed' and black_source == 'confirmed':
            return 'Male vs Male (Confirmed)'
        else:
            return 'Male vs Male (Mixed)'
    else:
        return 'Other'

df['Pairing'] = df.apply(
    lambda row: assign_pairing(
        row['White_Sex'], row['White_Sex_Source'],
        row['Black_Sex'], row['Black_Sex_Source']
    ),
    axis=1
)

pairing_dist = df['Pairing'].value_counts().sort_values(ascending=False)

print(f"\nGames by gender pairing:")
for pairing, count in pairing_dist.items():
    print(f"  {pairing:40s}: {count:>7,} ({count/len(df)*100:>5.1f}%)")

# ============= FOCUS ON KEY PAIRINGS =============
print("\n" + "=" * 80)
print("MAIN ANALYSIS GROUPS")
print("=" * 80)

# Extract the three main comparison groups
df_mvf = df[df['Pairing'] == 'Male vs Female (Confirmed)'].copy()
df_mvpf = df[df['Pairing'] == 'Male vs Perceived Female (Inferred)'].copy()
df_mvm = df[df['Pairing'] == 'Male vs Male (Confirmed)'].copy()

print(f"\n1. Male vs Female (Confirmed):     {len(df_mvf):>7,} games")
print(f"2. Male vs Perceived Female:       {len(df_mvpf):>7,} games")
print(f"3. Male vs Male (Confirmed):       {len(df_mvm):>7,} games")
print(f"\nTotal for RQ1 analysis:            {len(df_mvf) + len(df_mvpf) + len(df_mvm):>7,} games")

# ============= STATISTICS BY PAIRING =============
print("\n" + "=" * 80)
print("SUMMARY STATISTICS BY PAIRING")
print("=" * 80)

for pairing_name, df_pairing in [
    ('Male vs Female (Confirmed)', df_mvf),
    ('Male vs Perceived Female', df_mvpf),
    ('Male vs Male (Confirmed)', df_mvm)
]:
    if len(df_pairing) > 0:
        print(f"\n{pairing_name}:")
        print(f"  Games: {len(df_pairing):,}")
        print(f"  Ply Count - Mean: {df_pairing['PlyCount'].mean():.1f}, Median: {df_pairing['PlyCount'].median():.0f}, Std: {df_pairing['PlyCount'].std():.1f}")
        print(f"  Rating Diff - Mean: {df_pairing['RatingDiff'].mean():.1f}, Std: {df_pairing['RatingDiff'].std():.1f}")
        print(f"  White Elo - Mean: {df_pairing['White_Elo'].mean():.0f}")
        print(f"  Date range: {df_pairing['Date'].min()} to {df_pairing['Date'].max()}")

# ============= SAVE DATASETS =============
print("\n" + "=" * 80)
print("SAVING DATASETS")
print("=" * 80)

# Save full dataset
df.to_csv('data/lichess_elite_all_games_with_gender.csv', index=False)
print(f"✓ Full dataset: {len(df):,} games")
print(f"  → data/lichess_elite_all_games_with_gender.csv")

# Save RQ1 analysis dataset (main three groups)
df_rq1 = pd.concat([df_mvf, df_mvpf, df_mvm], ignore_index=True)
df_rq1.to_csv('data/rq1_analysis_expanded.csv', index=False)
print(f"\n✓ RQ1 analysis dataset: {len(df_rq1):,} games")
print(f"  → data/rq1_analysis_expanded.csv")

# Save each pairing separately for reference
df_mvf.to_csv('analysis/games_male_vs_female_confirmed.csv', index=False)
df_mvpf.to_csv('analysis/games_male_vs_perceived_female.csv', index=False)
df_mvm.to_csv('analysis/games_male_vs_male_confirmed.csv', index=False)

print(f"\n✓ Individual pairing files saved:")
print(f"  → games_male_vs_female_confirmed.csv")
print(f"  → games_male_vs_perceived_female.csv") 
print(f"  → games_male_vs_male_confirmed.csv")

# ============= COMPARISON WITH ORIGINAL =============
print("\n" + "=" * 80)
print("SAMPLE SIZE EXPANSION")
print("=" * 80)

# Load original RQ1 data
df_original = pd.read_csv('data/rq1_behavior_analysis.csv')

print(f"\nOriginal RQ1 dataset: {len(df_original):,} games")
print(f"New RQ1 dataset:      {len(df_rq1):,} games")
print(f"Expansion factor:     {len(df_rq1) / len(df_original):.1f}x")

# Count female games in original
female_original = (df_original['Black_Sex'] == 'F').sum()
female_new_mvf = len(df_mvf)
female_new_mvpf = len(df_mvpf)

print(f"\nFemale opponent games:")
print(f"  Original (Female only):           {female_original:>7,}")
print(f"  New (Confirmed Female):           {female_new_mvf:>7,}")
print(f"  New (Perceived Female):           {female_new_mvpf:>7,}")
print(f"  New (Combined):                   {female_new_mvf + female_new_mvpf:>7,}")
print(f"  Increase:                         {(female_new_mvf + female_new_mvpf) / female_original:.1f}x if all combined")

print("\n" + "=" * 80)
print("✓ EXTRACTION COMPLETE")
print("=" * 80)
print("\nNext: Run enhanced RQ1 analysis on rq1_analysis_expanded.csv")
print("Comparisons to make:")
print("  1. Male vs Female (Confirmed)")
print("  2. Male vs Perceived Female (Inferred)")
print("  3. Male vs Male (Confirmed)")
print("  4. All three groups combined")
