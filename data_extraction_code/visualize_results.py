import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Set style
sns.set(style="whitegrid")
OUTPUT_DIR = "results/plots"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def plot_rq1(data_path):
    print("Generating RQ1 Plots...")
    try:
        df = pd.read_csv(data_path)
    except FileNotFoundError:
        print(f"File not found: {data_path}")
        return

    # 1. Resignation Ply Count by Opponent Sex (Boxplot)
    plt.figure(figsize=(8, 6))
    sns.boxplot(x='Black_Sex', y='PlyCount', data=df, showfliers=False) # Hide outliers for cleaner view
    plt.title('Resignation Game Length (Ply Count) vs Opponent Gender')
    plt.xlabel('Opponent Gender')
    plt.ylabel('Ply Count (Game Length)')
    plt.savefig(f"{OUTPUT_DIR}/rq1_resignation_boxplot.png")
    plt.close()
    
    # 2. Aggressiveness Rate by Opponent Sex (Bar Chart)
    # Re-calculate means for plotting
    agg_means = df.groupby('Black_Sex')['IsAggressive'].mean().reset_index()
    
    plt.figure(figsize=(8, 6))
    sns.barplot(x='Black_Sex', y='IsAggressive', data=agg_means)
    plt.title('Opening Aggressiveness Frequency vs Opponent Gender')
    plt.xlabel('Opponent Gender')
    plt.ylabel('Aggressiveness Rate')
    plt.ylim(0, 0.6) # Scale 0-1ish
    plt.savefig(f"{OUTPUT_DIR}/rq1_aggressiveness_bar.png")
    plt.close()

    # 3. Resignation Ply vs Rating Diff (Scatter)
    # Downsample for scatter plot clarity if huge
    if len(df) > 10000:
        plot_df = df.sample(10000, random_state=42)
    else:
        plot_df = df
        
    plt.figure(figsize=(10, 6))
    sns.scatterplot(x='RatingDiff', y='PlyCount', hue='Black_Sex', alpha=0.3, data=plot_df)
    plt.title('Resignation Time vs Rating Difference')
    plt.xlabel('Rating Difference (White - Black)')
    plt.ylabel('Ply Count')
    plt.axvline(x=0, color='gray', linestyle='--')
    plt.savefig(f"{OUTPUT_DIR}/rq1_resignation_scatter.png")
    plt.close()
    print("RQ1 Plots saved.")

def plot_rq2(data_path):
    print("Generating RQ2 Plots...")
    try:
        df = pd.read_csv(data_path)
    except FileNotFoundError:
        print(f"File not found: {data_path}")
        return

    # 1. Opening Diversity vs Rating
    plt.figure(figsize=(10, 6))
    sns.regplot(x='AvgRating', y='OpeningDiversity', data=df, scatter_kws={'alpha':0.3}, line_kws={'color':'red'})
    plt.title('Opening Repertoire Diversity vs Rating')
    plt.xlabel('Average Rating')
    plt.ylabel('Opening Diversity (Entropy)')
    plt.savefig(f"{OUTPUT_DIR}/rq2_diversity_rating.png")
    plt.close()

    # 2. Aggressiveness vs Rating
    plt.figure(figsize=(10, 6))
    sns.regplot(x='AvgRating', y='Aggressiveness', data=df, scatter_kws={'alpha':0.3}, line_kws={'color':'red'})
    plt.title('Opening Aggressiveness vs Rating')
    plt.xlabel('Average Rating')
    plt.ylabel('Aggressiveness Rate')
    plt.savefig(f"{OUTPUT_DIR}/rq2_aggressiveness_rating.png")
    plt.close()
    
    print("RQ2 Plots saved.")

if __name__ == "__main__":
    plot_rq1('data/rq1_behavior_analysis.csv')
    plot_rq2('data/rq2_opening_analysis.csv')
