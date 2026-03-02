"""
Gender Inference and Distribution Analysis
==========================================
This script:
1. Analyzes current gender distribution in unified dataset
2. Infers gender for missing records using name-based classification
3. Stores augmented dataset with inferred gender
4. Generates comprehensive statistics
"""

import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# Import gender prediction library
try:
    import gender_guesser.detector as gender
    detector = gender.Detector()
except ImportError:
    print("Installing gender-guesser...")
    import subprocess
    subprocess.run(['pip', 'install', 'gender-guesser'], check=True)
    import gender_guesser.detector as gender
    detector = gender.Detector()

# Load unified dataset
print("=" * 60)
print("GENDER ANALYSIS - UNIFIED CHESS PLAYERS DATASET")
print("=" * 60)

df = pd.read_csv('data/unified_chess_players.csv')
print(f"\nTotal Players: {len(df):,}")

# ======================= CURRENT GENDER DISTRIBUTION =======================
print("\n" + "="*60)
print("1. CURRENT GENDER DISTRIBUTION (from FIDE)")
print("="*60)

gender_counts = df['sex'].value_counts(dropna=False)
gender_pct = df['sex'].value_counts(normalize=True, dropna=False) * 100

print(f"\nMale (M):              {gender_counts.get('M', 0):>6,} ({gender_pct.get('M', 0):>5.1f}%)")
print(f"Female (F):            {gender_counts.get('F', 0):>6,} ({gender_pct.get('F', 0):>5.1f}%)")
print(f"Unknown (NaN):         {gender_counts.get(np.nan, 0):>6,} ({gender_pct.get(np.nan, 0):>5.1f}%)")

# ======================= GENDER INFERENCE FOR MISSING DATA =======================
print("\n" + "="*60)
print("2. INFERRING GENDER FOR MISSING RECORDS")
print("="*60)

def infer_gender_from_name(name):
    """
    Infer gender using gender-guesser library
    Returns: 'M', 'F', or 'unknown' (for ambiguous/unclassifiable cases)
    """
    if pd.isna(name):
        return 'unknown'
    
    # Extract first name
    parts = str(name).strip().split()
    if len(parts) == 0:
        return 'unknown'
    
    first_name = parts[0]
    
    # Use gender-guesser library
    guess = detector.get_gender(first_name)
    
    # Map results: mostly_male, probably_male -> 'M', mostly_female, probably_female -> 'F'
    if guess in ['mostly_male', 'probably_male', 'andy']:
        return 'M'
    elif guess in ['mostly_female', 'probably_female']:
        return 'F'
    else:
        return 'unknown'

# Create a copy for augmented dataset
df_augmented = df.copy()

# Identify rows with missing gender
missing_gender_mask = df_augmented['sex'].isna()
missing_count = missing_gender_mask.sum()

print(f"\nProcessing {missing_count:,} records with missing gender...")

# Infer gender for missing records
inferred_genders = []
for idx, name in df_augmented.loc[missing_gender_mask, 'name'].items():
    inferred = infer_gender_from_name(name)
    inferred_genders.append((idx, inferred))
    
    if len(inferred_genders) % 1000 == 0:
        print(f"  Processed {len(inferred_genders):,} records...")

# Apply inferred values
for idx, inferred in inferred_genders:
    df_augmented.loc[idx, 'sex'] = inferred

print(f"Gender inference complete!")

# ======================= AUGMENTED GENDER DISTRIBUTION =======================
print("\n" + "="*60)
print("3. AUGMENTED GENDER DISTRIBUTION (with inferred data)")
print("="*60)

gender_counts_aug = df_augmented['sex'].value_counts()
gender_pct_aug = df_augmented['sex'].value_counts(normalize=True) * 100

print(f"\nMale (M):              {gender_counts_aug.get('M', 0):>6,} ({gender_pct_aug.get('M', 0):>5.1f}%)")
print(f"Female (F):            {gender_counts_aug.get('F', 0):>6,} ({gender_pct_aug.get('F', 0):>5.1f}%)")
print(f"Unknown:               {gender_counts_aug.get('unknown', 0):>6,} ({gender_pct_aug.get('unknown', 0):>5.1f}%)")

# ======================= GENDER SOURCE BREAKDOWN =======================
print("\n" + "="*60)
print("4. GENDER SOURCE BREAKDOWN")
print("="*60)

original_known = df['sex'].notna().sum()
inferred_count = (df['sex'].isna() & (df_augmented['sex'] != 'unknown')).sum()
still_unknown = (df_augmented['sex'] == 'unknown').sum()

print(f"\nFrom FIDE:             {original_known:>6,} ({original_known/len(df)*100:>5.1f}%)")
print(f"Inferred (Algorithm):  {inferred_count:>6,} ({inferred_count/len(df)*100:>5.1f}%)")
print(f"Still Unknown:         {still_unknown:>6,} ({still_unknown/len(df)*100:>5.1f}%)")

# ======================= BREAKDOWN BY PLATFORM =======================
print("\n" + "="*60)
print("5. GENDER DISTRIBUTION BY PLATFORM")
print("="*60)

# FIDE only
fide_only = df_augmented[df_augmented['fide_id'].notna()]
print(f"\nPlayers with FIDE IDs: {len(fide_only):,}")
if len(fide_only) > 0:
    print(f"  Male: {(fide_only['sex'] == 'M').sum():>6,} ({(fide_only['sex'] == 'M').sum()/len(fide_only)*100:>5.1f}%)")
    print(f"  Female: {(fide_only['sex'] == 'F').sum():>6,} ({(fide_only['sex'] == 'F').sum()/len(fide_only)*100:>5.1f}%)")

# Chess.com
chesscom = df_augmented[df_augmented['chesscom_username'].notna()]
print(f"\nChess.com: {len(chesscom):,}")
if len(chesscom) > 0:
    print(f"  Male: {(chesscom['sex'] == 'M').sum():>6,} ({(chesscom['sex'] == 'M').sum()/len(chesscom)*100:>5.1f}%)")
    print(f"  Female: {(chesscom['sex'] == 'F').sum():>6,} ({(chesscom['sex'] == 'F').sum()/len(chesscom)*100:>5.1f}%)")

# Lichess
lichess = df_augmented[df_augmented['lichess_username'].notna()]
print(f"\nLichess: {len(lichess):,}")
if len(lichess) > 0:
    print(f"  Male: {(lichess['sex'] == 'M').sum():>6,} ({(lichess['sex'] == 'M').sum()/len(lichess)*100:>5.1f}%)")
    print(f"  Female: {(lichess['sex'] == 'F').sum():>6,} ({(lichess['sex'] == 'F').sum()/len(lichess)*100:>5.1f}%)")

# ======================= SAVE AUGMENTED DATASET =======================
print("\n" + "="*60)
print("6. SAVING AUGMENTED DATASET")
print("="*60)

output_path = 'data/unified_chess_players_with_inferred_gender.csv'
df_augmented.to_csv(output_path, index=False)
print(f"\nSaved to: {output_path}")

# Save summary statistics
summary = {
    'total_players': len(df),
    'male_fide_only': gender_counts.get('M', 0),
    'female_fide_only': gender_counts.get('F', 0),
    'unknown_fide': missing_count,
    'male_after_inference': gender_counts_aug.get('M', 0),
    'female_after_inference': gender_counts_aug.get('F', 0),
    'still_unknown': still_unknown,
    'male_pct': gender_pct_aug.get('M', 0),
    'female_pct': gender_pct_aug.get('F', 0),
    'unknown_pct': gender_pct_aug.get('unknown', 0)
}

summary_df = pd.DataFrame([summary])
summary_df.to_csv('analysis/gender_distribution_summary.csv', index=False)
print(f"Summary saved to: analysis/gender_distribution_summary.csv")

print("\n" + "="*60)
print("ANALYSIS COMPLETE")
print("="*60)
print("\nNext Steps:")
print("- Review the augmented dataset")
print("- Run RQ1 and RQ2 analyses with gender categories")
print("- Compare: Male vs Female, Male vs Perceived Female, Male vs Male")
