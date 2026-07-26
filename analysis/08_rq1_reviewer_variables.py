"""
RQ1 extended model: reviewer-suggested variables
================================================
Adds three variables to the RQ1 game-length model, following the supervisor's review:

- FemaleWins:       1 when the confirmed or perceived female player wins the game.
- LowerRatedWinner: 1 when the game is won by the lower-rated player (an upset).
- sqrt(|RatingDiff|): the square root of the absolute rating difference, which lets the
                      rating-difference effect take a non-linear shape.

The model is fitted with statsmodels OLS so that standard errors, p-values, confidence
intervals, and diagnostics are reported. Run from the repository root:

    python analysis/08_rq1_reviewer_variables.py
"""

import numpy as np
import pandas as pd
import statsmodels.api as sm


def is_aggressive(eco):
    if pd.isna(eco) or eco == "Unknown":
        return False
    eco = str(eco).strip()
    return any(eco.startswith(p) for p in ["B", "C", "D3", "D4", "D5"])


def main():
    df = pd.read_csv("data/rq1_analysis_expanded.csv")
    df["Agg"] = df["ECO"].apply(is_aggressive).astype(int)

    pairings = [
        "Male vs Female (Confirmed)",
        "Male vs Perceived Female (Inferred)",
        "Male vs Male (Confirmed)",
    ]
    df = df[df["Pairing"].isin(pairings)].copy()
    df["conf"] = (df["Pairing"] == "Male vs Female (Confirmed)").astype(int)
    df["perc"] = (df["Pairing"] == "Male vs Perceived Female (Inferred)").astype(int)
    df = df.dropna(subset=["PlyCount", "RatingDiff", "White_Elo", "Black_Elo"])

    df["absdiff"] = df["RatingDiff"].abs()
    df["sqrt_absdiff"] = np.sqrt(df["absdiff"])

    result = df["Result"].astype(str).str.strip()
    white_win = result.eq("1-0")
    black_win = result.eq("0-1")

    female_is_white = df["White_Sex"].astype(str).str.upper().eq("F")
    female_is_black = df["Black_Sex"].astype(str).str.upper().eq("F")
    df["FemaleWins"] = (
        (female_is_white & white_win) | (female_is_black & black_win)
    ).astype(int)

    lower_rated_winner = (
        (white_win & (df["White_Elo"] < df["Black_Elo"]))
        | (black_win & (df["Black_Elo"] < df["White_Elo"]))
    )
    df["LowerRatedWinner"] = lower_rated_winner.astype(int)

    predictors = [
        "conf",
        "perc",
        "absdiff",
        "sqrt_absdiff",
        "Agg",
        "FemaleWins",
        "LowerRatedWinner",
    ]
    X = sm.add_constant(df[predictors], has_constant="add")
    model = sm.OLS(df["PlyCount"], X).fit()
    ci = model.conf_int(0.05)

    print("RQ1 extended model (outcome: PlyCount), n = %d" % int(model.nobs))
    print("R2 = %.5f   adj R2 = %.5f   F = %.2f   p(F) = %.2e"
          % (model.rsquared, model.rsquared_adj, model.fvalue, model.f_pvalue))
    rows = []
    for name in model.params.index:
        print("  %-16s coef = %10.4f   SE = %8.4f   p = %.3e   95%% CI = [%.4f, %.4f]"
              % (name, model.params[name], model.bse[name], model.pvalues[name],
                 ci.loc[name, 0], ci.loc[name, 1]))
        rows.append({
            "predictor": name,
            "coef": model.params[name],
            "std_err": model.bse[name],
            "p_value": model.pvalues[name],
            "ci_low": ci.loc[name, 0],
            "ci_high": ci.loc[name, 1],
        })

    out = pd.DataFrame(rows)
    out.to_csv("analysis/rq1_reviewer_variables_results.csv", index=False)
    print("\nSaved: analysis/rq1_reviewer_variables_results.csv")


if __name__ == "__main__":
    main()
