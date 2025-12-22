import pandas as pd

# Load data
df = pd.read_csv("../../data/detailed_games_sample.csv")

print("Dataset shape:", df.shape)
print("\nColumns:")
print(df.columns.tolist())

#Check resignation signal
print("\nGame status counts:")
print(df["status"].value_counts())

resign_rate = (df["status"] == "resign").mean()
print(f"\nResignation rate: {resign_rate:.2%}")

#Inspect resignation timing (core proxy)
resign_games = df[df["status"] == "resign"]
print("\nResignation games count:", len(resign_games))
print("\nTotal moves (resignation games) summary:")
print(resign_games["total_moves"].describe())

#Check per-player sample sizes
resign_counts = resign_games.groupby("player_username").size()

print("\nPlayers with resignation games:")
print(resign_counts.describe())

print("\nTop players by resignation count:")
print(resign_counts.sort_values(ascending=False).head(10))

#ACPL sanity check (for Tilt)
print("\nACPL summary (all games):")
print(df["acpl"].describe())

print("\nMissing ACPL values:", df["acpl"].isna().sum())

#Time ordering check (Tilt prerequisite)
print("\nTimestamp summary:")
print(df["timestamp"].describe())

# Check per-player ordering
sample_player = df["player_username"].iloc[0]
sample_games = df[df["player_username"] == sample_player].sort_values("timestamp")
print(f"\nSample games for player: {sample_player}")
print(sample_games[["timestamp", "status", "won", "total_moves"]].head())





