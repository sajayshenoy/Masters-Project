# -*- coding: utf-8 -*-
"""Generate clean, report-ready figures for the revised master's report."""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)          # repo root (parent of figures/)
OUT = HERE                            # write figures next to this script
os.makedirs(OUT, exist_ok=True)

plt.rcParams.update({
    "figure.dpi": 200, "savefig.dpi": 200,
    "font.size": 11, "axes.titlesize": 12, "axes.titleweight": "bold",
    "axes.labelsize": 11, "axes.grid": True, "grid.alpha": 0.25,
    "axes.spines.top": False, "axes.spines.right": False,
    "legend.frameon": False, "figure.autolayout": False,
})
C_MVM = "#3b6ea5"   # male baseline
C_CONF = "#c0392b"  # confirmed female
C_PERC = "#e08e0b"  # perceived female
C_F = "#c0392b"     # female (RQ2)
C_M = "#3b6ea5"     # male (RQ2)

def ci95(a):
    a = np.asarray(a, float); a = a[~np.isnan(a)]
    if len(a) < 2: return np.nan
    return 1.96 * a.std(ddof=1) / np.sqrt(len(a))

# ============================== LOAD RQ1 ==============================
df = pd.read_csv(os.path.join(REPO, "data", "rq1_analysis_expanded.csv"))
def is_aggr(e):
    if pd.isna(e) or e == "Unknown": return False
    e = str(e).strip()
    return any(e.startswith(p) for p in ["B", "C", "D3", "D4", "D5"])
df["Agg"] = df["ECO"].apply(is_aggr)
df = df[df["Pairing"].isin(["Male vs Female (Confirmed)",
                            "Male vs Perceived Female (Inferred)",
                            "Male vs Male (Confirmed)"])].copy()
df = df.dropna(subset=["PlyCount", "RatingDiff"])
mvm = df[df["Pairing"] == "Male vs Male (Confirmed)"]
conf = df[df["Pairing"] == "Male vs Female (Confirmed)"]
perc = df[df["Pairing"] == "Male vs Perceived Female (Inferred)"]
ftar = pd.concat([conf, perc])  # female-target (all)

# ---------- FIG 1: RQ1 overview (2x2) ----------
fig, ax = plt.subplots(2, 2, figsize=(11, 8.2))

# (a) mean game length by context with 95% CI
groups = [("Male vs Male", mvm, C_MVM), ("Male vs Female\n(confirmed)", conf, C_CONF),
          ("Male vs Perceived\nFemale", perc, C_PERC)]
means = [g[1]["PlyCount"].mean() for g in groups]
errs = [ci95(g[1]["PlyCount"]) for g in groups]
cols = [g[2] for g in groups]
labels = [g[0] for g in groups]
bars = ax[0, 0].bar(labels, means, yerr=errs, capsize=5, color=cols, alpha=0.85,
                    edgecolor="black", linewidth=0.8)
for b, m, e, g in zip(bars, means, errs, groups):
    ax[0, 0].text(b.get_x() + b.get_width() / 2, m + e + 2.0,
                  f"{m:.1f}\nn = {len(g[1]):,}",
                  ha="center", va="bottom", fontsize=9)
ax[0, 0].set_ylabel("Mean game length (plies)")
ax[0, 0].set_title("(a) Game length by opponent context")
ax[0, 0].set_ylim(0, max(m + e for m, e in zip(means, errs)) * 1.28)

# (b) aggressive opening rate by context
agg_rates = [g[1]["Agg"].mean() * 100 for g in groups]
bars = ax[0, 1].bar(labels, agg_rates, color=cols, alpha=0.85, edgecolor="black", linewidth=0.8)
for b, v in zip(bars, agg_rates):
    ax[0, 1].text(b.get_x() + b.get_width() / 2, v + 0.4, f"{v:.1f}%", ha="center", va="bottom", fontsize=9)
ax[0, 1].set_ylabel("Aggressive openings (%)")
ax[0, 1].set_title("(b) Opening aggressiveness by context")
ax[0, 1].set_ylim(0, max(agg_rates) * 1.18)

# (c) distribution female-target (all) vs male baseline
bins = np.linspace(0, 220, 56)
ax[1, 0].hist(mvm["PlyCount"], bins=bins, density=True, color=C_MVM, alpha=0.55, label=f"Male vs Male (n={len(mvm):,})")
ax[1, 0].hist(ftar["PlyCount"], bins=bins, density=True, color=C_CONF, alpha=0.45, label=f"Female-target, all (n={len(ftar):,})")
ax[1, 0].axvline(mvm["PlyCount"].mean(), color=C_MVM, ls="--", lw=1.5)
ax[1, 0].axvline(ftar["PlyCount"].mean(), color=C_CONF, ls="--", lw=1.5)
ax[1, 0].set_xlabel("Game length (plies)"); ax[1, 0].set_ylabel("Density")
ax[1, 0].set_title("(c) Game-length distribution"); ax[1, 0].legend(fontsize=9)

# (d) mean ply vs SIGNED rating diff bins -> shows symmetric / zero-centered pattern
edges = np.array([-600, -300, -200, -125, -75, -25, 25, 75, 125, 200, 300, 600])
cent = 0.5 * (edges[:-1] + edges[1:])
m_ply, m_err = [], []
for lo, hi in zip(edges[:-1], edges[1:]):
    s = df[(df["RatingDiff"] >= lo) & (df["RatingDiff"] < hi)]["PlyCount"]
    m_ply.append(s.mean()); m_err.append(ci95(s))
ax[1, 1].errorbar(cent, m_ply, yerr=m_err, marker="o", color="#444", capsize=3, lw=1.5)
ax[1, 1].axvline(0, color=C_CONF, ls=":", lw=1.5)
ax[1, 1].set_xlabel("Signed rating difference (White - Black)")
ax[1, 1].set_ylabel("Mean game length (plies)")
ax[1, 1].set_title("(d) Effect is centered on zero, not linear")
fig.suptitle("RQ1: Opponent gender, opening style, and game length (expanded sample, n = 25,554)",
             fontsize=13, fontweight="bold", y=0.99)
fig.tight_layout(rect=[0, 0, 1, 0.975])
fig.savefig(os.path.join(OUT, "fig1_rq1_overview.png"), bbox_inches="tight")
plt.close(fig)

# ---------- FIG 2: RQ1 rating control (1x2): boxplot + |rating diff| ----------
fig, ax = plt.subplots(1, 2, figsize=(11, 4.4))
# boxplot game length by context
data_box = [mvm["PlyCount"], conf["PlyCount"], perc["PlyCount"]]
bp = ax[0].boxplot(data_box, patch_artist=True, showfliers=False,
                   medianprops=dict(color="black"),
                   labels=["Male vs\nMale", "Male vs Female\n(confirmed)", "Male vs\nPerceived F"])
for patch, c in zip(bp["boxes"], [C_MVM, C_CONF, C_PERC]):
    patch.set_facecolor(c); patch.set_alpha(0.7)
ax[0].set_ylabel("Game length (plies)")
ax[0].set_title("(a) Game length by opponent context")

# mean ply vs ABSOLUTE rating diff + linear fit
df["AbsDiff"] = df["RatingDiff"].abs()
aedges = np.array([0, 40, 80, 120, 160, 220, 300, 420, 650])
acent, aply, aerr = [], [], []
for lo, hi in zip(aedges[:-1], aedges[1:]):
    s = df[(df["AbsDiff"] >= lo) & (df["AbsDiff"] < hi)]["PlyCount"]
    if len(s) > 10:
        acent.append((lo + hi) / 2); aply.append(s.mean()); aerr.append(ci95(s))
acent, aply, aerr = map(np.array, (acent, aply, aerr))
ax[1].errorbar(acent, aply, yerr=aerr, marker="o", color=C_CONF, capsize=3, lw=1.5, label="Binned mean (95% CI)")
# linear fit on raw data
b, a = np.polyfit(df["AbsDiff"], df["PlyCount"], 1)
xs = np.linspace(0, acent.max() + 30, 50)
ax[1].plot(xs, a + b * xs, color="#222", ls="--", lw=1.6,
           label=f"OLS fit: slope = {b:.4f} plies/point")
ax[1].set_xlabel("Absolute rating difference |White - Black|")
ax[1].set_ylabel("Mean game length (plies)")
ax[1].set_title("(b) Larger mismatch -> shorter games")
ax[1].legend(fontsize=9, loc="upper right")
fig.suptitle("RQ1: Why absolute rating difference is the right control",
             fontsize=12.5, fontweight="bold", y=1.02)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "fig2_rq1_rating_control.png"), bbox_inches="tight")
plt.close(fig)

# ============================== LOAD RQ2 ==============================
d2 = pd.read_csv(os.path.join(REPO, "analysis", "rq2_players_with_metrics.csv"))
d2 = d2.dropna(subset=["AvgRating", "GamesCount", "OpeningDiversity", "Aggressiveness", "Player_Sex"])
male = d2[d2["Player_Sex"] == "M"]; female = d2[d2["Player_Sex"] == "F"]
d2["LogGames"] = np.log1p(d2["GamesCount"])

# ---------- FIG 3: RQ2 overview (1x3) ----------
fig, ax = plt.subplots(1, 3, figsize=(13, 4.3))
# rating distribution by gender
ax[0].hist(male["AvgRating"], bins=30, density=True, color=C_M, alpha=0.55, label=f"Male (n={len(male)})")
ax[0].hist(female["AvgRating"], bins=15, density=True, color=C_F, alpha=0.55, label=f"Female (n={len(female)})")
ax[0].set_xlabel("Average rating"); ax[0].set_ylabel("Density")
ax[0].set_title("(a) Rating by gender"); ax[0].legend(fontsize=9)
# diversity by gender (box)
bp = ax[1].boxplot([male["OpeningDiversity"], female["OpeningDiversity"]],
                   patch_artist=True, showfliers=False, labels=["Male", "Female"],
                   medianprops=dict(color="black"))
for patch, c in zip(bp["boxes"], [C_M, C_F]):
    patch.set_facecolor(c); patch.set_alpha(0.7)
ax[1].set_ylabel("Opening diversity (Shannon entropy)")
ax[1].set_title("(b) Diversity by gender")
# aggressiveness by gender (box)
bp = ax[2].boxplot([male["Aggressiveness"], female["Aggressiveness"]],
                   patch_artist=True, showfliers=False, labels=["Male", "Female"],
                   medianprops=dict(color="black"))
for patch, c in zip(bp["boxes"], [C_M, C_F]):
    patch.set_facecolor(c); patch.set_alpha(0.7)
ax[2].set_ylabel("Aggressiveness (share of games)")
ax[2].set_title("(c) Aggressiveness by gender")
fig.suptitle("RQ2: Opening style by gender (player level, n = 729)",
             fontsize=12.5, fontweight="bold", y=1.02)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "fig3_rq2_overview.png"), bbox_inches="tight")
plt.close(fig)

# ---------- FIG 4: RQ2 diversity drivers (1x2): vs rating, vs log games ----------
fig, ax = plt.subplots(1, 2, figsize=(11, 4.4))
# diversity vs rating with per-gender fits
for g, c, lab in [(male, C_M, "Male"), (female, C_F, "Female")]:
    ax[0].scatter(g["AvgRating"], g["OpeningDiversity"], s=18, color=c, alpha=0.45, label=lab)
    if len(g) > 2:
        bb, aa = np.polyfit(g["AvgRating"], g["OpeningDiversity"], 1)
        xs = np.linspace(g["AvgRating"].min(), g["AvgRating"].max(), 40)
        ax[0].plot(xs, aa + bb * xs, color=c, lw=2)
rM = male["AvgRating"].corr(male["OpeningDiversity"]); rF = female["AvgRating"].corr(female["OpeningDiversity"])
ax[0].set_xlabel("Average rating"); ax[0].set_ylabel("Opening diversity (Shannon)")
ax[0].set_title(f"(a) Diversity vs rating\n(r_M = {rM:.2f}, r_F = {rF:.2f})")
ax[0].legend(fontsize=9)
# diversity vs log games (dominant predictor)
ax[1].scatter(d2["LogGames"], d2["OpeningDiversity"], s=16, color="#5a4fa0", alpha=0.4)
bb, aa = np.polyfit(d2["LogGames"], d2["OpeningDiversity"], 1)
xs = np.linspace(d2["LogGames"].min(), d2["LogGames"].max(), 40)
ax[1].plot(xs, aa + bb * xs, color="#222", lw=2, ls="--", label=f"slope = {bb:.3f}")
ax[1].set_xlabel("log(1 + games played)"); ax[1].set_ylabel("Opening diversity (Shannon)")
ax[1].set_title("(b) Diversity vs activity\n(dominant driver, p < 1e-80)")
ax[1].legend(fontsize=9)
fig.suptitle("RQ2: Opening diversity scales with activity and rating",
             fontsize=12.5, fontweight="bold", y=1.02)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "fig4_rq2_diversity_drivers.png"), bbox_inches="tight")
plt.close(fig)

print("OK - figures written to", OUT)
for f in sorted(os.listdir(OUT)):
    print("  ", f, os.path.getsize(os.path.join(OUT, f)), "bytes")
