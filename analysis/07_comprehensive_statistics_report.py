"""
Comprehensive Statistics Report for Progress Report
====================================================

This script generates all statistics and p-values needed for the new progress report,
including regression p-values, effect sizes, and comprehensive comparisons.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from sklearn.linear_model import LinearRegression
from scipy.stats import f_oneway
import warnings
warnings.filterwarnings('ignore')

print("=" * 100)
print("COMPREHENSIVE STATISTICS REPORT - ALL RESEARCH QUESTIONS")
print("=" * 100)

# ============================================================================
# PART 1: RQ1 - GENDER BEHAVIORAL DIFFERENCES (EXPANDED LICHESS DATASET)
# ============================================================================

print("\n" + "=" * 100)
print("RQ1: DO PLAYERS BEHAVE DIFFERENTLY AGAINST FEMALE OPPONENTS?")
print("=" * 100)

# Load expanded dataset
df_rq1 = pd.read_csv('data/rq1_analysis_expanded.csv')

# Create aggressiveness estimate
def is_aggressive_eco(eco_code):
    """Classify opening as aggressive based on ECO code"""
    if pd.isna(eco_code) or eco_code == 'Unknown':
        return False
    eco = str(eco_code).strip()
    aggressive_patterns = ['B', 'C', 'D3', 'D4', 'D5']
    for pattern in aggressive_patterns:
        if eco.startswith(pattern):
            return True
    return False

df_rq1['IsAggressive_Est'] = df_rq1['ECO'].apply(is_aggressive_eco)

# Filter to main analysis groups
df_rq1_analysis = df_rq1[df_rq1['Pairing'].isin([
    'Male vs Female (Confirmed)',
    'Male vs Male (Confirmed)'
])].copy()

# Create binary indicator
df_rq1_analysis['Is_MvF'] = (df_rq1_analysis['Pairing'] == 'Male vs Female (Confirmed)').astype(int)

df_mvf = df_rq1_analysis[df_rq1_analysis['Is_MvF'] == 1]
df_mvm = df_rq1_analysis[df_rq1_analysis['Is_MvF'] == 0]

print(f"\nDataset Information:")
print(f"  Total games analyzed: {len(df_rq1_analysis):,}")
print(f"  Male vs Female (Confirmed): {len(df_mvf):,} ({len(df_mvf)/len(df_rq1_analysis)*100:.1f}%)")
print(f"  Male vs Male (Confirmed): {len(df_mvm):,} ({len(df_mvm)/len(df_rq1_analysis)*100:.1f}%)")
print(f"  Perceived Female games: 0 (gender inference was too conservative)")

# ------- METRIC 1: RESIGNATION TIME -------
print("\n" + "-" * 100)
print("METRIC 1: RESIGNATION TIME (Game Length in Plies)")
print("-" * 100)

mvf_mean = df_mvf['PlyCount'].mean()
mvf_std = df_mvf['PlyCount'].std()
mvf_median = df_mvf['PlyCount'].median()
mvf_n = len(df_mvf)

mvm_mean = df_mvm['PlyCount'].mean()
mvm_std = df_mvm['PlyCount'].std()
mvm_median = df_mvm['PlyCount'].median()
mvm_n = len(df_mvm)

print(f"\nMale vs Female (n={mvf_n:,}):")
print(f"  Mean: {mvf_mean:.2f} plies (SD={mvf_std:.2f})")
print(f"  Median: {mvf_median:.0f} plies")

print(f"\nMale vs Male (n={mvm_n:,}):")
print(f"  Mean: {mvm_mean:.2f} plies (SD={mvm_std:.2f})")
print(f"  Median: {mvm_median:.0f} plies")

print(f"\nDifference: {mvf_mean - mvm_mean:.2f} plies (MvF vs MvM)")
print(f"Effect size (Cohen's d): {(mvf_mean - mvm_mean) / np.sqrt((mvf_std**2 + mvm_std**2)/2):.4f}")

# T-test (independent samples)
t_stat, t_pval = stats.ttest_ind(df_mvf['PlyCount'], df_mvm['PlyCount'])
print(f"\nIndependent t-test:")
print(f"  t = {t_stat:.4f}")
print(f"  p-value = {t_pval:.6f}")
print(f"  Significance: {'✓ YES (p < 0.05)' if t_pval < 0.05 else '✗ NO (p >= 0.05)'}")

# ------- METRIC 2: OPENING AGGRESSIVENESS -------
print("\n" + "-" * 100)
print("METRIC 2: OPENING AGGRESSIVENESS (Strategic Choices)")
print("-" * 100)

mvf_agg = df_mvf['IsAggressive_Est'].sum()
mvf_agg_pct = mvf_agg / len(df_mvf) * 100

mvm_agg = df_mvm['IsAggressive_Est'].sum()
mvm_agg_pct = mvm_agg / len(df_mvm) * 100

print(f"\nMale vs Female (n={mvf_n:,}):")
print(f"  Aggressive openings: {mvf_agg:,} / {mvf_n:,} ({mvf_agg_pct:.1f}%)")

print(f"\nMale vs Male (n={mvm_n:,}):")
print(f"  Aggressive openings: {mvm_agg:,} / {mvm_n:,} ({mvm_agg_pct:.1f}%)")

print(f"\nDifference: {mvf_agg_pct - mvm_agg_pct:.2f} percentage points")

# Chi-square test
chi2, chi2_pval, dof, expected = stats.chi2_contingency([
    [mvf_agg, mvf_n - mvf_agg],
    [mvm_agg, mvm_n - mvm_agg]
])

print(f"\nChi-square test:")
print(f"  χ² = {chi2:.4f}")
print(f"  df = {dof}")
print(f"  p-value = {chi2_pval:.6f}")
print(f"  Significance: {'✓ YES (p < 0.05)' if chi2_pval < 0.05 else '✗ NO (p >= 0.05)'}")

# ------- REGRESSION ANALYSIS -------
print("\n" + "-" * 100)
print("REGRESSION ANALYSIS: Predicting Game Length (PlyCount)")
print("-" * 100)

# Prepare data for regression
y = df_rq1_analysis['PlyCount'].values

# Model 1: Gender only
X1 = df_rq1_analysis['Is_MvF'].values.reshape(-1, 1)
model1 = LinearRegression()
model1.fit(X1, y)
r2_1 = model1.score(X1, y)

# Get p-value for model1
n = len(y)
residuals_1 = y - model1.predict(X1)
mse_1 = np.sum(residuals_1**2) / (n - 2)
var_x = np.var(X1, ddof=1)
se_coef_1 = np.sqrt(mse_1 / (n * var_x))
t_coef_1 = model1.coef_[0] / se_coef_1
p_coef_1 = 2 * (1 - stats.t.cdf(np.abs(t_coef_1), n - 2))

print(f"\nModel 1: Gender Only")
print(f"  Equation: PlyCount = Intercept + Gender_Coef * IsMvF")
print(f"  Gender coefficient: {model1.coef_[0]:.4f}")
print(f"  Intercept: {model1.intercept_:.4f}")
print(f"  R² = {r2_1:.6f}")
print(f"  p-value (gender coef): {p_coef_1:.6f}")

# Model 2: Gender + Rating Difference
df_rq1_analysis['RatingDiff_std'] = (df_rq1_analysis['RatingDiff'] - df_rq1_analysis['RatingDiff'].mean()) / df_rq1_analysis['RatingDiff'].std()
X2 = np.column_stack([
    df_rq1_analysis['Is_MvF'],
    df_rq1_analysis['RatingDiff_std']
])
model2 = LinearRegression()
model2.fit(X2, y)
r2_2 = model2.score(X2, y)

residuals_2 = y - model2.predict(X2)
mse_2 = np.sum(residuals_2**2) / (n - 3)
# Compute standard errors for Model 2
X2_with_const = np.column_stack([np.ones(len(X2)), X2])
var_covar = mse_2 * np.linalg.inv(X2_with_const.T @ X2_with_const)
se_coef_2 = np.sqrt(np.diag(var_covar)[1:])
t_coef_2 = model2.coef_ / se_coef_2
p_coef_2 = 2 * (1 - stats.t.cdf(np.abs(t_coef_2), n - 3))

print(f"\nModel 2: Gender + Rating Difference")
print(f"  Equation: PlyCount = Intercept + Gender_Coef * IsMvF + RatingDiff_Coef * RatingDiff")
print(f"  Gender coefficient: {model2.coef_[0]:.4f}")
print(f"  RatingDiff coefficient: {model2.coef_[1]:.4f}")
print(f"  Intercept: {model2.intercept_:.4f}")
print(f"  R² = {r2_2:.6f}")
print(f"  p-value (gender): {p_coef_2[0]:.6f}")
print(f"  p-value (rating): {p_coef_2[1]:.6f}")

# Model 3: Gender + Rating + Aggressiveness
X3 = np.column_stack([
    df_rq1_analysis['Is_MvF'],
    df_rq1_analysis['RatingDiff_std'],
    df_rq1_analysis['IsAggressive_Est'].astype(int)
])
model3 = LinearRegression()
model3.fit(X3, y)
r2_3 = model3.score(X3, y)

residuals_3 = y - model3.predict(X3)
mse_3 = np.sum(residuals_3**2) / (n - 4)
X3_with_const = np.column_stack([np.ones(len(X3)), X3])
var_covar_3 = mse_3 * np.linalg.inv(X3_with_const.T @ X3_with_const)
se_coef_3 = np.sqrt(np.diag(var_covar_3)[1:])
t_coef_3 = model3.coef_ / se_coef_3
p_coef_3 = 2 * (1 - stats.t.cdf(np.abs(t_coef_3), n - 4))

print(f"\nModel 3: Gender + Rating + Aggressiveness (FULL MODEL)")
print(f"  Equation: PlyCount = Intercept + Gender_Coef*IsMvF + Rating_Coef*RatingDiff + Agg_Coef*IsAggressive")
print(f"  Gender coefficient: {model3.coef_[0]:.4f}")
print(f"  RatingDiff coefficient: {model3.coef_[1]:.4f}")
print(f"  Aggressiveness coefficient: {model3.coef_[2]:.4f}")
print(f"  Intercept: {model3.intercept_:.4f}")
print(f"  R² = {r2_3:.6f}")
print(f"  p-value (gender): {p_coef_3[0]:.6f}")
print(f"  p-value (rating): {p_coef_3[1]:.6f}")
print(f"  p-value (agg): {p_coef_3[2]:.6f}")

# ============================================================================
# PART 2: RQ2 - OPENING REPERTOIRE ADAPTATION
# ============================================================================

print("\n" + "=" * 100)
print("RQ2: DO PLAYERS ADAPT OPENING REPERTOIRE WITH OPPONENT RATING?")
print("=" * 100)

# Load RQ2 dataset
df_rq2 = pd.read_csv('analysis/rq2_players_with_metrics.csv')

# Rename columns for consistency
df_rq2.rename(columns={'AvgRating': 'Rating', 'Player_Sex': 'Gender'}, inplace=True)

print(f"\nDataset Information:")
print(f"  Total players analyzed: {len(df_rq2):,}")
print(f"  Male players: {(df_rq2['Gender'] == 'M').sum():,}")
print(f"  Female players: {(df_rq2['Gender'] == 'F').sum():,}")
print(f"  Data source: Lichess Elite Database (2013-2020)")

# ------- METRIC 1: OPENING DIVERSITY vs RATING -------
print("\n" + "-" * 100)
print("METRIC 1: OPENING DIVERSITY (Shannon Entropy) vs RATING")
print("-" * 100)

df_male = df_rq2[df_rq2['Gender'] == 'M']
df_female = df_rq2[df_rq2['Gender'] == 'F']

# Remove NaN values
df_male_clean = df_male[df_male['OpeningDiversity'].notna()]
df_female_clean = df_female[df_female['OpeningDiversity'].notna()]

# Correlation for males
corr_male, p_corr_male = stats.pearsonr(df_male_clean['Rating'], df_male_clean['OpeningDiversity'])
print(f"\nMale players (n={len(df_male_clean):,}):")
print(f"  Pearson r (Rating vs Diversity): {corr_male:.4f}")
print(f"  p-value: {p_corr_male:.6f}")
print(f"  Significance: {'✓ YES (p < 0.05)' if p_corr_male < 0.05 else '✗ NO (p >= 0.05)'}")
print(f"  Interpretation: Stronger males have {'BROADER' if corr_male > 0 else 'NARROWER'} repertoires")

# Correlation for females
if len(df_female_clean) > 2:
    corr_female, p_corr_female = stats.pearsonr(df_female_clean['Rating'], df_female_clean['OpeningDiversity'])
    print(f"\nFemale players (n={len(df_female_clean):,}):")
    print(f"  Pearson r (Rating vs Diversity): {corr_female:.4f}")
    print(f"  p-value: {p_corr_female:.6f}")
    print(f"  Significance: {'✓ YES (p < 0.05)' if p_corr_female < 0.05 else '✗ NO (p >= 0.05)'}")
    print(f"  Interpretation: Stronger females have {'BROADER' if corr_female > 0 else 'NARROWER'} repertoires")

# ------- METRIC 2: OPENING AGGRESSIVENESS vs RATING -------
print("\n" + "-" * 100)
print("METRIC 2: OPENING AGGRESSIVENESS vs RATING")
print("-" * 100)

# Correlation for males
corr_agg_male, p_agg_male = stats.pearsonr(df_male_clean['Rating'], df_male_clean['Aggressiveness'])
print(f"\nMale players (n={len(df_male_clean):,}):")
print(f"  Pearson r (Rating vs Aggressiveness): {corr_agg_male:.4f}")
print(f"  p-value: {p_agg_male:.6f}")
print(f"  Significance: {'✓ YES (p < 0.05)' if p_agg_male < 0.05 else '✗ NO (p >= 0.05)'}")

if len(df_female_clean) > 2:
    corr_agg_female, p_agg_female = stats.pearsonr(df_female_clean['Rating'], df_female_clean['Aggressiveness'])
    print(f"\nFemale players (n={len(df_female_clean):,}):")
    print(f"  Pearson r (Rating vs Aggressiveness): {corr_agg_female:.4f}")
    print(f"  p-value: {p_agg_female:.6f}")
    print(f"  Significance: {'✓ YES (p < 0.05)' if p_agg_female < 0.05 else '✗ NO (p >= 0.05)'}")

# ------- GENDER DIFFERENCES in REPERTOIRE METRICS -------
print("\n" + "-" * 100)
print("GENDER DIFFERENCES IN REPERTOIRE METRICS")
print("-" * 100)

div_male_mean = df_male_clean['OpeningDiversity'].mean()
div_female_mean = df_female_clean['OpeningDiversity'].mean()
agg_male_mean = df_male_clean['Aggressiveness'].mean()
agg_female_mean = df_female_clean['Aggressiveness'].mean()

print(f"\nOpen Diversity (Shannon Entropy):")
print(f"  Male mean: {div_male_mean:.4f}")
print(f"  Female mean: {div_female_mean:.4f}")
print(f"  Difference: {div_male_mean - div_female_mean:.4f}")

# T-test for diversity
t_div, p_div = stats.ttest_ind(df_male_clean['OpeningDiversity'], df_female_clean['OpeningDiversity'])
print(f"  t-test: t={t_div:.4f}, p={p_div:.6f}")
print(f"  Significance: {'✓ YES (p < 0.05)' if p_div < 0.05 else '✗ NO (p >= 0.05)'}")

print(f"\nOpening Aggressiveness:")
print(f"  Male mean: {agg_male_mean:.4f}")
print(f"  Female mean: {agg_female_mean:.4f}")
print(f"  Difference: {agg_male_mean - agg_female_mean:.4f}")

# T-test for aggressiveness
t_agg, p_agg = stats.ttest_ind(df_male_clean['Aggressiveness'], df_female_clean['Aggressiveness'])
print(f"  t-test: t={t_agg:.4f}, p={p_agg:.6f}")
print(f"  Significance: {'✓ YES (p < 0.05)' if p_agg < 0.05 else '✗ NO (p >= 0.05)'}")

# ============================================================================
# SUMMARY TABLE
# ============================================================================

print("\n" + "=" * 100)
print("SUMMARY TABLE: ALL STATISTICS FOR PROGRESS REPORT")
print("=" * 100)

summary_data = {
    'Research Question': [
        'RQ1: Resignation Time',
        'RQ1: Aggressiveness',
        'RQ1: Gender Effect (Model 3)',
        'RQ2: Diversity-Rating (M)',
        'RQ2: Diversity-Rating (F)',
        'RQ2: Aggressiveness-Rating (M)',
        'RQ2: Aggressiveness-Rating (F)',
    ],
    'Metric': [
        'plies',
        'percentage points',
        'coefficient',
        'correlation',
        'correlation',
        'correlation',
        'correlation',
    ],
    'Value': [
        f'{mvf_mean - mvm_mean:.2f}',
        f'{mvf_agg_pct - mvm_agg_pct:.2f}',
        f'{model3.coef_[0]:.4f}',
        f'{corr_male:.4f}',
        f'{corr_female:.4f}' if len(df_female_clean) > 2 else 'N/A',
        f'{corr_agg_male:.4f}',
        f'{corr_agg_female:.4f}' if len(df_female_clean) > 2 else 'N/A',
    ],
    'P-value': [
        f'{t_pval:.6f}',
        f'{chi2_pval:.6f}',
        f'{p_coef_3[0]:.6f}',
        f'{p_corr_male:.6f}',
        f'{p_corr_female:.6f}' if len(df_female_clean) > 2 else 'N/A',
        f'{p_agg_male:.6f}',
        f'{p_agg_female:.6f}' if len(df_female_clean) > 2 else 'N/A',
    ],
    'Significant (p<0.05)': [
        '✓ YES' if t_pval < 0.05 else '✗ NO',
        '✓ YES' if chi2_pval < 0.05 else '✗ NO',
        '✓ YES' if p_coef_3[0] < 0.05 else '✗ NO',
        '✓ YES' if p_corr_male < 0.05 else '✗ NO',
        '✓ YES' if p_corr_female < 0.05 else '✗ NO' if len(df_female_clean) > 2 else 'N/A',
        '✓ YES' if p_agg_male < 0.05 else '✗ NO',
        '✓ YES' if p_agg_female < 0.05 else '✗ NO' if len(df_female_clean) > 2 else 'N/A',
    ]
}

df_summary = pd.DataFrame(summary_data)
print(df_summary.to_string(index=False))

# Save summary
df_summary.to_csv('analysis/comprehensive_statistics_summary.csv', index=False)
print(f"\n✓ Summary saved to: analysis/comprehensive_statistics_summary.csv")

print("\n" + "=" * 100)
print("ANALYSIS COMPLETE")
print("=" * 100)
