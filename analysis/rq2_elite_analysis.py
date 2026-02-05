import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import numpy as np

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, 'data', 'elite_games_processed.csv')
OUTPUT_DIR = os.path.join(BASE_DIR, 'analysis', 'plots')
SUMMARY_PATH = os.path.join(BASE_DIR, 'analysis', 'rq2_elite_summary.txt')

def ensure_dirs():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

def load_data():
    print("Loading processed Elite Database games...")
    if not os.path.exists(DATA_PATH):
        print(f"Error: {DATA_PATH} not found. Please run process_elite_database.py first.")
        return None
    
    # Read CSV
    df = pd.read_csv(DATA_PATH, low_memory=False)
    print(f"Loaded {len(df)} games.")
    return df

def analyze_openings(df):
    analysis_results = []
    
    # 1. Opening Diversity per Gender
    # We look at games where the player of that gender played White or Black?
    # Usually opening choice is dictated by White, but Black chooses the defense.
    # Let's pivot to a player-centric view.
    
    # Create a long-format dataframe for players
    # Columns: PlayerName, Sex, ECO, Opening, Color
    
    white_players = df[['White_Unified_Name', 'White_Sex', 'ECO', 'Opening']].rename(
        columns={'White_Unified_Name': 'Player', 'White_Sex': 'Sex'}
    )
    white_players['Color'] = 'White'
    
    black_players = df[['Black_Unified_Name', 'Black_Sex', 'ECO', 'Opening']].rename(
        columns={'Black_Unified_Name': 'Player', 'Black_Sex': 'Sex'}
    )
    black_players['Color'] = 'Black'
    
    # Concatenate and filter for Titled players (where Sex is known)
    all_moves = pd.concat([white_players, black_players])
    all_moves = all_moves.dropna(subset=['Sex'])
    
    print(f"Total player-game records for analysis: {len(all_moves)}")
    
    # Filter out invalid ECOs
    all_moves = all_moves[all_moves['ECO'] != '?']
    all_moves = all_moves[all_moves['ECO'].notna()]
    
    # Group by Gender
    gender_groups = all_moves.groupby('Sex')
    
    # Diversity Metrics
    diversity_stats = []
    
    plt.figure(figsize=(10, 6))
    
    for sex in ['M', 'F']:
        if sex not in gender_groups.groups:
            continue
            
        group = gender_groups.get_group(sex)
        unique_openings = group['ECO'].nunique()
        total_games = len(group)
        
        # Calculate entropy of opening distribution
        opening_counts = group['ECO'].value_counts()
        probs = opening_counts / total_games
        entropy = -np.sum(probs * np.log2(probs))
        
        diversity_stats.append(f"Gender: {sex}")
        diversity_stats.append(f"  Total Games: {total_games}")
        diversity_stats.append(f"  Unique ECOs: {unique_openings}")
        diversity_stats.append(f"  Shannon Entropy: {entropy:.4f}")
        diversity_stats.append(f"  Top 5 Openings: {', '.join(opening_counts.head(5).index)}")
        diversity_stats.append("-" * 30)
        
        # Plot Top 10 Openings
        top_10 = opening_counts.head(10)
        
        # Determine strict Opening Names (take most common name for each ECO)
        # This is a bit expensive, simplified: just use ECO for plot
        
    # Comparative Plot: Top 10 ECOs for Women vs Men (Side by Side)
    # We need to normalize by total games to compare frequencies
    
    men_data = all_moves[all_moves['Sex'] == 'M']['ECO'].value_counts(normalize=True).head(10)
    women_data = all_moves[all_moves['Sex'] == 'F']['ECO'].value_counts(normalize=True).head(10)
    
    # Combine distinct top keys
    all_top_ecos = list(set(men_data.index) | set(women_data.index))
    
    # Re-fetch counts for these specific ECOs to compare
    men_counts = all_moves[all_moves['Sex'] == 'M']['ECO'].value_counts(normalize=True)
    women_counts = all_moves[all_moves['Sex'] == 'F']['ECO'].value_counts(normalize=True)
    
    plot_data = []
    for eco in all_top_ecos:
        # Get simplified name if possible (using first occurrence)
        # name = all_moves[all_moves['ECO'] == eco]['Opening'].iloc[0]
        # simplified_name = name.split(':')[0].split(',')[0] # Heuristic
        
        plot_data.append({
            'ECO': eco,
            'Frequency': men_counts.get(eco, 0) * 100,
            'Gender': 'Men'
        })
        plot_data.append({
            'ECO': eco,
            'Frequency': women_counts.get(eco, 0) * 100,
            'Gender': 'Women'
        })
        
    plot_df = pd.DataFrame(plot_data)
    
    # Sort by overall frequency
    # plot_df.sort_values('Frequency', ascending=False, inplace=True) 
    
    plt.figure(figsize=(12, 8))
    sns.barplot(data=plot_df, x='ECO', y='Frequency', hue='Gender')
    plt.title('Top Opening Choices (ECO) by Gender Frequency')
    plt.ylabel('Percentage of Games Used (%)')
    plt.xlabel('ECO Code')
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'rq2_elite_top_openings_comparison.png'))
    plt.close()
    
    return "\n".join(diversity_stats)

def main():
    ensure_dirs()
    df = load_data()
    if df is None:
        return

    summary = analyze_openings(df)
    
    print(summary)
    with open(SUMMARY_PATH, 'w') as f:
        f.write(summary)
    print(f"Analysis complete. Summary saved to {SUMMARY_PATH}")

if __name__ == "__main__":
    main()
