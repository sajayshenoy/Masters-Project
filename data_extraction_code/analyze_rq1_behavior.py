import pandas as pd
import numpy as np
import os

def analyze_gender_behavior(data_path, output_path):
    print("Loading game data for RQ1...")
    try:
        df = pd.read_csv(data_path)
    except FileNotFoundError:
        print(f"Error: File not found at {data_path}")
        return

    # Filter for games where Black's sex is known (we analyze White's behavior vs Black)
    # And specifically where we know the opponent is Female vs Male
    
    # Check column names - we have White_Sex and Black_Sex
    # We want to see how White behaves when Black is F vs M
    
    df_valid = df.dropna(subset=['White_Unified_Name', 'Black_Sex', 'PlyCount'])
    df_valid['PlyCount'] = pd.to_numeric(df_valid['PlyCount'], errors='coerce')
    
    # Calculate Rating Diff
    # WhiteElo - BlackElo
    df_valid['WhiteElo'] = pd.to_numeric(df_valid['WhiteElo'], errors='coerce')
    df_valid['BlackElo'] = pd.to_numeric(df_valid['BlackElo'], errors='coerce')
    df_valid['RatingDiff'] = df_valid['WhiteElo'] - df_valid['BlackElo']
    
    # Now dropna on RatingDiff
    df_valid = df_valid.dropna(subset=['RatingDiff', 'PlyCount'])


    # Filter for games lost by White (Resignation behavior is most relevant in losses)
    # Result 0-1 means White Lost
    df_losses = df_valid[df_valid['Result'] == '0-1'].copy()
    
    print(f"Analyzing {len(df_losses)} games where White lost...")

    # Group by Opponent Gender
    stats = df_losses.groupby('Black_Sex')['PlyCount'].describe()
    print("Resignation Ply Count stats by Opponent Gender:")
    print(stats)
    
    # Aggressiveness vs Gender
    # Define aggressive openings
    aggressive_keywords = ['Gambit', 'Attack', 'Sicilian', 'King\'s Indian']
    def is_aggressive(op):
        if not isinstance(op, str): return False
        return any(k in op for k in aggressive_keywords)
        
    df_valid['IsAggressive'] = df_valid['Opening'].apply(is_aggressive)
    
    agg_stats = df_valid.groupby('Black_Sex')['IsAggressive'].mean()
    print("\nOpening Aggressiveness by Opponent Gender:")
    print(agg_stats)
    
    # Save detailed results for plotting
    # We want to save row-level data for the plots: RatingDiff, PlyCount, OpponentSex
    output_df = df_losses[['White_Unified_Name', 'Black_Sex', 'PlyCount', 'RatingDiff', 'Opening']].copy()
    output_df['IsAggressive'] = output_df['Opening'].apply(is_aggressive)
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    output_df.to_csv(output_path, index=False)
    print(f"Saved processed RQ1 data to {output_path}")

if __name__ == "__main__":
    analyze_gender_behavior(
        data_path=os.path.join('data', 'elite_games_processed.csv'),
        output_path=os.path.join('data', 'rq1_behavior_analysis.csv')
    )
