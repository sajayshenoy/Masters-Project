import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

def analyze_openings():
    input_file = os.path.join("./../data", "openings_sample.csv")
    if not os.path.exists(input_file):
        print("Openings data not found at path",input_file)
        return

    df = pd.read_csv(input_file)
    print(f"Loaded {len(df)} games.")
    
    # Filter out games where ECO or Opening is missing or '?'
    df = df.dropna(subset=['eco', 'opening', 'sex'])
    df = df[df['eco'] != '?']
    
    summary_lines = []
    
    # 1. Opening Diversity
    # Calculate unique ECO codes per player, then average by gender
    diversity = df.groupby(['username', 'sex'])['eco'].nunique().reset_index()
    
    avg_diversity = diversity.groupby('sex')['eco'].mean()
    print("\n--- Opening Diversity (Avg Unique ECOs per 30 games) ---")
    print(avg_diversity)
    summary_lines.append("RQ2: Opening Repertoire Analysis\n================================")
    summary_lines.append("\n--- Opening Diversity (Avg Unique ECOs per 30 games) ---")
    summary_lines.append(avg_diversity.to_string())
    
    # Plot Diversity
    plots_dir = os.path.join("analysis", "plots")
    os.makedirs(plots_dir, exist_ok=True)
    
    plt.figure(figsize=(6, 5))
    sns.boxplot(x='sex', y='eco', data=diversity)
    plt.title("Opening Diversity (Unique ECOs)")
    plt.ylabel("Count of Unique Openings")
    plt.savefig(os.path.join(plots_dir, "opening_diversity.png"))
    plt.close()
    
    # 2. Most Popular Openings (Top 10)
    print("\n--- Top 10 Openings by Gender ---")
    summary_lines.append("\n\n--- Top 10 Openings by Gender ---")
    
    for sex in ['M', 'F']:
        sub = df[df['sex'] == sex]
        top_eco = sub['eco'].value_counts().head(10)
        
        header = f"\nGender {sex} Top Openings:"
        print(header)
        print(top_eco)
        summary_lines.append(header)
        summary_lines.append(top_eco.to_string())
        
        # Save plot for each
        plt.figure(figsize=(10, 6))
        # Fix: assign x to hue and set legend=False
        sns.barplot(x=top_eco.index, y=top_eco.values, hue=top_eco.index, palette="viridis", legend=False)
        plt.title(f"Top 10 Openings for {sex}")
        plt.xlabel("ECO Code")
        plt.ylabel("Frequency")
        plt.savefig(os.path.join(plots_dir, f"top_openings_{sex}.png"))
        plt.close()

    # Save summary
    with open(os.path.join("analysis", "rq2_summary.txt"), "w") as f:
        f.write("\n".join(summary_lines))
    print(f"\nSummary saved to analysis/rq2_summary.txt")

    # 3. Analyze White vs Black? 
    # The sample contains games played as both White and Black. 
    # The 'eco' is the game's opening, regardless of who played what.
    # But usually opening choice is dictated by White's first move and Black's response.
    # It's a shared opening, so measuring "what openings appear in their games" is valid for repertoire width.

if __name__ == "__main__":
    analyze_openings()
