import os
import pandas as pd
import matplotlib.pyplot as plt

BASE_DIR = "."
PLOTS_DIR = os.path.join(BASE_DIR, "plots")
os.makedirs(PLOTS_DIR, exist_ok=True)

RT_PATH = "resignation_threshold_v1.csv"
TILT_PATH = "tilt_player_v1.csv"
DATA_PATH = "../../data/detailed_games_sample.csv"


def savefig(name: str):
    path = os.path.join(PLOTS_DIR, name)
    plt.tight_layout()
    plt.savefig(path, dpi=200)
    plt.close()
    print("Saved:", path)


def main():
    rt = pd.read_csv(RT_PATH)
    tilt = pd.read_csv(TILT_PATH)

    # 1) Histogram: Resignation Threshold
    plt.figure()
    plt.hist(rt["resignation_threshold"], bins=15)
    plt.xlabel("Resignation Threshold (median moves)")
    plt.ylabel("Number of players")
    plt.title("Distribution of Resignation Threshold (v1)")
    savefig("rt_hist.png")

    # 2) Histogram: Tilt ACPL median
    plt.figure()
    plt.hist(tilt["tilt_acpl_median"].dropna(), bins=15)
    plt.xlabel("Tilt (median ΔACPL)  [post - baseline]")
    plt.ylabel("Number of players")
    plt.title("Distribution of Tilt (ACPL) (v1)")
    savefig("tilt_acpl_hist.png")

    # 3) Scatter: RT vs Tilt
    merged = rt.merge(tilt, on="player_username", how="inner")
    plt.figure()
    plt.scatter(merged["resignation_threshold"], merged["tilt_acpl_median"])
    plt.axhline(0)
    plt.xlabel("Resignation Threshold (median moves)")
    plt.ylabel("Tilt (median ΔACPL)")
    plt.title("Resignation Threshold vs Tilt (v1)")
    savefig("rt_vs_tilt_scatter.png")

    # Optional: add sex labels (boxplots)
    df = pd.read_csv(DATA_PATH)
    sex_map = df[["player_username", "player_sex"]].drop_duplicates()
    merged_sex = merged.merge(sex_map, on="player_username", how="left")

    # 4) Boxplot: RT by sex
    rt_m = merged_sex.loc[merged_sex["player_sex"] == "M", "resignation_threshold"].dropna()
    rt_f = merged_sex.loc[merged_sex["player_sex"] == "F", "resignation_threshold"].dropna()
    if len(rt_m) > 0 and len(rt_f) > 0:
        plt.figure()
        plt.boxplot([rt_m, rt_f], labels=["M", "F"])
        plt.ylabel("Resignation Threshold (median moves)")
        plt.title("Resignation Threshold by Sex (v1)")
        savefig("rt_by_sex_box.png")

    # 5) Boxplot: Tilt by sex
    t_m = merged_sex.loc[merged_sex["player_sex"] == "M", "tilt_acpl_median"].dropna()
    t_f = merged_sex.loc[merged_sex["player_sex"] == "F", "tilt_acpl_median"].dropna()
    if len(t_m) > 0 and len(t_f) > 0:
        plt.figure()
        plt.boxplot([t_m, t_f], labels=["M", "F"])
        plt.ylabel("Tilt (median ΔACPL)")
        plt.title("Tilt (ACPL) by Sex (v1)")
        savefig("tilt_by_sex_box.png")


if __name__ == "__main__":
    main()
