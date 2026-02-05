import pandas as pd
import numpy as np
import scipy.stats
import os

def calculate_entropy(series):
    """Calculates Shannon entropy of a series (e.g., ECO codes)."""
    counts = series.value_counts()
    if len(counts) == 0:
        return 0
    probabilities = counts / counts.sum()
    return scipy.stats.entropy(probabilities)

def is_aggressive(opening_name):
    """Simple heuristic for aggressiveness based on opening name."""
    if not isinstance(opening_name, str):
        return False
    aggressive_keywords = ['Gambit', 'Attack', 'Sicilian', 'King\'s Indian']
    return any(keyword in opening_name for keyword in aggressive_keywords)

def analyze_openings(data_path, output_path):
    print("Loading game data...")
    try:
        df = pd.read_csv(data_path)
    except FileNotFoundError:
        print(f"Error: File not found at {data_path}")
        return

    # Filter for valid users and ratings
    df = df.dropna(subset=['White_Unified_Name', 'WhiteElo'])
    df['WhiteElo'] = pd.to_numeric(df['WhiteElo'], errors='coerce')
    df = df.dropna(subset=['WhiteElo'])
    
    # We focus on White for opening repertoire consistency usually
    # Group by Player
    player_stats = []
    
    print("Grouping by player...")
    # To speed up, we can filter for players with min N games
    white_counts = df['White_Unified_Name'].value_counts()
    active_players = white_counts[white_counts >= 10].index # Min 10 games to measure repertoire
    
    df_active = df[df['White_Unified_Name'].isin(active_players)]
    
    print(f"Analyzing {len(active_players)} active players...")
    
    for player, group in df_active.groupby('White_Unified_Name'):
        # Rating (Avg)
        avg_rating = group['WhiteElo'].mean()
        
        # Diversity (Entropy of ECO)
        diversity = calculate_entropy(group['ECO'])
        
        # Aggressiveness (% of games with Aggressive keywords)
        agg_count = group['Opening'].apply(is_aggressive).sum()
        agg_ratio = agg_count / len(group)
        
        player_stats.append({
            'Player': player,
            'AvgRating': avg_rating,
            'GamesCount': len(group),
            'OpeningDiversity': diversity,
            'Aggressiveness': agg_ratio,
            'Platform': 'Lichess' # Since this is Lichess Elite DB
        })
    
    results_df = pd.DataFrame(player_stats)
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    results_df.to_csv(output_path, index=False)
    print(f"Analysis complete. Processed {len(results_df)} players. Saved to {output_path}")

if __name__ == "__main__":
    analyze_openings(
        data_path=os.path.join('data', 'elite_games_processed.csv'),
        output_path=os.path.join('data', 'rq2_opening_analysis.csv')
    )
