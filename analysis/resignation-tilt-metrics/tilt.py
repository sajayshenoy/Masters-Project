import pandas as pd
import numpy as np

DATA_PATH = "../../data/detailed_games_sample.csv"

K_POST = 3                 # number of games after trigger
MIN_TRIGGERS = 2           # later you can raise to 5/10

def compute_tilt_events(df: pd.DataFrame) -> pd.DataFrame:
    # Basic cleanup
    df = df.copy()
    df["timestamp"] = pd.to_numeric(df["timestamp"], errors="coerce")
    df["acpl"] = pd.to_numeric(df["acpl"], errors="coerce")
    df["total_moves"] = pd.to_numeric(df["total_moves"], errors="coerce")
    df["won"] = df["won"].astype(bool)

    # Order games by player and time
    df = df.sort_values(["player_username", "timestamp"])

    # Trigger = resignation loss
    df["is_trigger"] = (df["status"] == "resign") & (~df["won"])

    events = []

    for player, g in df.groupby("player_username", sort=False):
        g = g.reset_index(drop=True)

        # Baseline metrics for the player
        baseline_acpl = g["acpl"].mean(skipna=True)
        baseline_winrate = g["won"].mean()
        baseline_moves = g["total_moves"].mean(skipna=True)

        trigger_idx = g.index[g["is_trigger"]].tolist()
        for idx in trigger_idx:
            post = g.iloc[idx+1: idx+1+K_POST].copy()
            if len(post) == 0:
                continue

            events.append({
                "player_username": player,
                "trigger_game_id": g.loc[idx, "game_id"],
                "trigger_timestamp": g.loc[idx, "timestamp"],
                "trigger_opponent_rating": g.loc[idx, "opponent_rating"],
                "trigger_moves": g.loc[idx, "total_moves"],
                "post_n": len(post),

                "baseline_acpl": baseline_acpl,
                "baseline_winrate": baseline_winrate,
                "baseline_moves": baseline_moves,

                "post_acpl": post["acpl"].mean(skipna=True),
                "post_winrate": post["won"].mean(),
                "post_moves": post["total_moves"].mean(skipna=True),
            })

    ev = pd.DataFrame(events)
    if ev.empty:
        return ev

    # Tilt deltas (post - baseline)
    ev["tilt_acpl"] = ev["post_acpl"] - ev["baseline_acpl"]
    ev["tilt_winrate"] = ev["post_winrate"] - ev["baseline_winrate"]
    ev["tilt_moves"] = ev["post_moves"] - ev["baseline_moves"]

    return ev


def aggregate_player_tilt(events: pd.DataFrame) -> pd.DataFrame:
    if events.empty:
        return events

    agg = (
        events
        .groupby("player_username")
        .agg(
            n_triggers=("trigger_game_id", "count"),
            tilt_acpl_median=("tilt_acpl", "median"),
            tilt_acpl_mean=("tilt_acpl", "mean"),
            tilt_winrate_median=("tilt_winrate", "median"),
            tilt_winrate_mean=("tilt_winrate", "mean"),
            tilt_moves_median=("tilt_moves", "median"),
        )
        .reset_index()
    )

    # optional filter flag
    agg["enough_triggers"] = agg["n_triggers"] >= MIN_TRIGGERS
    return agg


def main():
    df = pd.read_csv(DATA_PATH)

    events = compute_tilt_events(df)
    print("Tilt events:", events.shape)

    events_out = "tilt_events_v1.csv"
    events.to_csv(events_out, index=False)
    print("Saved:", events_out)

    players = aggregate_player_tilt(events)
    print("Player tilt:", players.shape)

    players_out = "tilt_player_v1.csv"
    players.to_csv(players_out, index=False)
    print("Saved:", players_out)

    # Quick sanity summary
    if not players.empty:
        print("\nTilt ACPL summary (player-level):")
        print(players["tilt_acpl_median"].describe())

        print("\nPlayers with enough triggers:", players["enough_triggers"].sum())


if __name__ == "__main__":
    main()
