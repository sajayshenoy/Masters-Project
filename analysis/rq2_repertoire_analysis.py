import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns

def classify_aggressiveness(eco):
    """
    Simple heuristic for opening aggressiveness based on ECO Volume.
    A: Flank/Irregular (Mixed)
    B: Semi-Open (Sicilians etc) -> Generally Aggressive
    C: Open Games (e4 e5) -> Mixed, but often Sharp
    D: Closed Games (d4 d5) -> Generally Solid
    E: Indian Defenses -> Hypermodern/Sharp
    """
    if not isinstance(eco, str): return "Unknown"
    
    # Simple classifier for the MVP
    if eco.startswith('B') or eco.startswith('E'):
        return "Aggressive"
    elif eco.startswith('D'):
        return "Solid"
    else:
        return "Neutral" # A and C are context dependent

def analyze_repertoire():
    # --- PATH FIX ---
    # Get the directory where this script is located (analysis)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Go up one level to Project Root
    project_root = os.path.dirname(script_dir) 
    # Build path to data folder
    data_dir = os.path.join(project_root, "data")
    
    input_file = os.path.join(data_dir, "detailed_games_sample.csv")
    plots_dir = os.path.join(script_dir, "plots")
    os.makedirs(plots_dir, exist_ok=True)
    # ----------------
    
    if not os.path.exists(input_file):
        print(f"Error: Data file not found at {input_file}")
        print("Make sure you have run 'fetch_detailed_games.py' successfully first!")
        return

    print(f"Loading games from {input_file}...")
    try:
        df = pd.read_csv(input_file)
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return
    
    if df.empty:
        print("Dataset is empty.")
        return

    # Apply Classification
    df['style'] = df['eco'].apply(classify_aggressiveness)
    
    # --- RQ2.1: Opening Style Preference ---
    print("\n--- Opening Style Distribution by Gender ---")
    
    # Group by Gender and Style
    style_dist = df.groupby(['player_sex', 'style']).size().unstack(fill_value=0)
    
    # Normalize to get percentages
    style_dist_pct = style_dist.div(style_dist.sum(axis=1), axis=0)
    print(style_dist_pct)
    
    # Plot
    plt.figure(figsize=(8, 6))
    style_dist_pct.plot(kind='bar', stacked=True, colormap='viridis')
    plt.title("Opening Style Preference by Gender")
    plt.ylabel("Percentage of Games")
    plt.xlabel("Player Gender")
    plt.xticks(rotation=0)
    plt.legend(title='Opening Style', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    
    output_plot = os.path.join(plots_dir, "rq2_style_preference.png")
    plt.savefig(output_plot)
    plt.close()
    print(f"Saved plot to {output_plot}")

if __name__ == "__main__":
    analyze_repertoire()