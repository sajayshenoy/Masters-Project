import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os

def analyze_behavior():
    # --- PATH FIX ---
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    data_dir = os.path.join(project_root, "data")
    
    games_file = os.path.join(data_dir, "detailed_games_sample.csv")
    players_file = os.path.join(data_dir, "unified_chess_players.csv")
    plots_dir = os.path.join(script_dir, "plots")
    os.makedirs(plots_dir, exist_ok=True)
    # ----------------

    if not os.path.exists(games_file):
        print("Detailed game data not found. Run fetch_detailed_games.py first.")
        return

    df = pd.read_csv(games_file)
    
    # --- RQ1.1: Resignation Time ---
    lost_resign = df[(df['status'] == 'resign') & (df['won'] == False)]
    
    print("\n--- Resignation Behavior (Avg Moves before Resigning) ---")
    print(lost_resign.groupby('player_sex')['total_moves'].mean())
    
    plt.figure(figsize=(6,5))
    sns.boxplot(x='player_sex', y='total_moves', data=lost_resign)
    plt.title("Moves Played Before Resigning (Lost Games)")
    plt.savefig(os.path.join(plots_dir, "rq1_resignation_time.png"))
    plt.close()

    # --- RQ1.2: Decision Quality (ACPL) ---
    player_db = pd.read_csv(players_file)
    sex_map = dict(zip(player_db['lichess_username'].dropna(), player_db['sex'].dropna()))
    
    # Map opponent gender
    # Note: Ensure opponent_id is a string
    df['opponent_id'] = df['opponent_id'].astype(str)
    df['opponent_sex'] = df['opponent_id'].map(sex_map)
    
    df_known = df.dropna(subset=['opponent_sex', 'acpl'])
    
    print("\n--- Decision Quality (ACPL) vs Opponent Gender ---")
    print(df_known.groupby(['player_sex', 'opponent_sex'])['acpl'].mean())
    
    if not df_known.empty:
        plt.figure(figsize=(8,6))
        sns.barplot(x='player_sex', y='acpl', hue='opponent_sex', data=df_known)
        plt.title("Average Centipawn Loss vs Opponent Gender")
        plt.savefig(os.path.join(plots_dir, "rq1_decision_quality.png"))
        plt.close()
    else:
        print("Not enough data with known opponent gender for ACPL analysis.")

if __name__ == "__main__":
    analyze_behavior()