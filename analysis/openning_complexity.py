import sys

import pandas as pd

from analysis.game_complexity import game_complexity_from_moves


def add_complexity_column(
    input_csv,
    output_csv,
    depth=18,
    top_n=3,
    start_move=10
):
    df = pd.read_csv(input_csv).head(50)

    complexities = []

    for idx, row in df.iterrows():
        print(f"Analyzing game {idx + 1}/{len(df)}")

        c = game_complexity_from_moves(
            row["moves"],
            depth=depth,
            top_n=top_n,
            start_move=start_move
        )
        complexities.append(c)

        print("oppening",df["eco"][idx],"For game",idx,"mean complexity per move:",c)

    df["complexity"] = complexities
    df.to_csv(output_csv, index=False)

if __name__ == "__main__":

    input_csv = "./../data/detailed_games_sample.csv"
    add_complexity_column(
        input_csv,
        "games_with_complexity.csv"
    )
