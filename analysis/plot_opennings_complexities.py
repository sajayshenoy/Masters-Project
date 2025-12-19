# plot_game_complexity.py
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 1. Load CSV
games = "games_with_complexity.csv"  # adjust path if needed

df = pd.read_csv(games)

# Inspect
print("Loaded CSV:")
print(df.head())

# 2. Extract ECO prefix
df['eco_prefix'] = df['eco'].str[:3]

# Optional: filter only A0xx/B0xx/C0xx if desired
df = df[df['eco_prefix'].str[0].isin(['A','B','C','D','E'])]

# 3. Group by ECO prefix
eco_stats = df.groupby('eco_prefix').agg(
    avg_complexity=('complexity', 'mean'),
    num_games=('complexity', 'count')
).reset_index()

# Sort by avg_complexity descending
eco_stats = eco_stats.sort_values(by='avg_complexity', ascending=False)

print("\nAggregated ECO stats:")
print(eco_stats)

# 4. Plotting
plt.figure(figsize=(12,6))

# Barplot: average complexity
sns.barplot(
    x='eco_prefix',
    y='avg_complexity',
    data=eco_stats,
    palette="Blues_d"
)

# Overlay scatter for number of games
# Normalize marker size for visibility
max_bubble = 500
sizes = eco_stats['num_games'] / eco_stats['num_games'].max() * max_bubble

plt.scatter(
    x=range(len(eco_stats)),
    y=eco_stats['avg_complexity'],
    s=sizes,
    color='red',
    alpha=0.6,
    label='Number of games'
)

plt.xticks(rotation=45)
plt.xlabel("ECO Prefix")
plt.ylabel("Average Game Complexity (cp)")
plt.title("Average Game Complexity by ECO Prefix (bubble = number of games)")
plt.legend()
plt.tight_layout()

# Save plot if needed
# plt.savefig("eco_complexity_plot.png", dpi=300)

plt.show()
