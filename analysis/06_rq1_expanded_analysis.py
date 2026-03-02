"""
RQ1 Analysis - Expanded Dataset
================================
Analyze the expanded Lichess dataset with:
- 294 Male vs Female games (up from 184)
- 17,084 Male vs Male games

Compare with original results to assess robustness
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from sklearn.linear_model import LinearRegression
import warnings
warnings.filterwarnings('ignore')

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (16, 10)

print("=" * 80)
print("RQ1 ANALYSIS - EXPANDED LICHESS DATASET")
print("=" * 80)

# Load expanded dataset
df = pd.read_csv('data/rq1_analysis_expanded.csv')

# Create aggressiveness estimate for ALL data first
def is_aggressive_eco(eco_code):
    """Classify opening as aggressive based on ECO code"""
    if pd.isna(eco_code) or eco_code == 'Unknown':
        return False
    
    eco = str(eco_code).strip()
    
    # Aggressive openings (gambits, sharp lines, etc.)
    aggressive_patterns = ['B', 'C', 'D3', 'D4', 'D5']
    
    for pattern in aggressive_patterns:
        if eco.startswith(pattern):
            return True
    
    return False

df['IsAggressive_Est'] = df['ECO'].apply(is_aggressive_eco)

# Filter to main analysis groups (M vs F confirmed, M vs perceived F, M vs M)
df_analysis = df[df['Pairing'].isin([
    'Male vs Female (Confirmed)',
    'Male vs Perceived Female (Inferred)',
    'Male vs Male (Confirmed)'
])].copy()

print(f"\nGames in analysis: {len(df_analysis):,}")

# Count by pairing
pairing_counts = df_analysis['Pairing'].value_counts()
print(f"\nBreakdown:")
for pairing, count in pairing_counts.items():
    print(f"  {pairing}: {count:,} ({count/len(df_analysis)*100:.1f}%)")

# ============= RESIGNATION TIME ANALYSIS =============
print("\n" + "=" * 80)
print("RESIGNATION TIME ANALYSIS (Game Length in Plies)")
print("=" * 80)

df_mvf = df_analysis[df_analysis['Pairing'] == 'Male vs Female (Confirmed)']
df_mvpf = df_analysis[df_analysis['Pairing'] == 'Male vs Perceived Female (Inferred)']
df_mvm = df_analysis[df_analysis['Pairing'] == 'Male vs Male (Confirmed)']

df_mvf_all = pd.concat([df_mvf, df_mvpf], ignore_index=True)

mvf_mean = df_mvf_all['PlyCount'].mean()
mvf_std = df_mvf_all['PlyCount'].std()
mvf_median = df_mvf_all['PlyCount'].median()

mvm_mean = df_mvm['PlyCount'].mean()
mvm_std = df_mvm['PlyCount'].std()
mvm_median = df_mvm['PlyCount'].median()

print(f"\nMale vs Female (All: Confirmed + Perceived) (n={len(df_mvf_all):,}):")
print(f"  Mean: {mvf_mean:.2f} ({mvf_std:.2f} std)")
print(f"  Median: {mvf_median:.0f}")

print(f"\n  Confirmed subset n={len(df_mvf):,}, mean={df_mvf['PlyCount'].mean():.2f}")
print(f"  Perceived subset n={len(df_mvpf):,}, mean={df_mvpf['PlyCount'].mean() if len(df_mvpf) else np.nan:.2f}")

print(f"\nMale vs Male (n={len(df_mvm):,}):")
print(f"  Mean: {mvm_mean:.2f} ({mvm_std:.2f} std)")
print(f"  Median: {mvm_median:.0f}")

print(f"\nDifference: {mvf_mean - mvm_mean:.2f} plies")

# T-test (all female-target games vs male baseline)
t_stat, p_value = stats.ttest_ind(df_mvf_all['PlyCount'], df_mvm['PlyCount'])
print(f"T-test: t={t_stat:.4f}, p={p_value:.4f}")

if p_value < 0.05:
    print(f"✓ SIGNIFICANT difference in game length")
else:
    print(f"✗ NOT SIGNIFICANT")

# ============= AGGRESSIVENESS ANALYSIS =============
print("\n" + "=" * 80)
print("STRATEGIC CHOICES: OPENING AGGRESSIVENESS")
print("=" * 80)

# Calculate aggressiveness rates
mvf_aggr = (df_mvf_all['IsAggressive_Est'] == True).sum() / len(df_mvf_all) * 100
mvpf_aggr = (df_mvpf['IsAggressive_Est'] == True).sum() / len(df_mvpf) * 100 if len(df_mvpf) else np.nan
mvm_aggr = (df_mvm['IsAggressive_Est'] == True).sum() / len(df_mvm) * 100

print(f"\nMale vs Female (All) aggressive openings: {mvf_aggr:.1f}%")
if len(df_mvpf) > 0:
    print(f"Male vs Perceived Female aggressive openings: {mvpf_aggr:.1f}%")
print(f"Male vs Male aggressive openings: {mvm_aggr:.1f}%")
print(f"Difference: {mvm_aggr - mvf_aggr:.1f} percentage points")

# Chi-square test
contingency = pd.crosstab(
    df_analysis['Pairing'],
    df_analysis['IsAggressive_Est']
)
chi2, p_chi, dof, expected = stats.chi2_contingency(contingency)

print(f"\nChi-square: χ²={chi2:.4f}, p={p_chi:.4f}")
if p_chi < 0.05:
    print(f"✓ SIGNIFICANT difference in opening choices")
else:
    print(f"✗ NOT SIGNIFICANT")

# ============= REGRESSION ANALYSIS =============
print("\n" + "=" * 80)
print("REGRESSION MODELS")
print("=" * 80)

# Prepare data
df_reg = df_analysis.copy()
df_reg['Is_MvF_Confirmed'] = (df_reg['Pairing'] == 'Male vs Female (Confirmed)').astype(int)
df_reg['Is_MvF_Perceived'] = (df_reg['Pairing'] == 'Male vs Perceived Female (Inferred)').astype(int)
df_reg['Is_MvF'] = ((df_reg['Is_MvF_Confirmed'] == 1) | (df_reg['Is_MvF_Perceived'] == 1)).astype(int)
df_reg['Is_Aggressive'] = (df_reg['IsAggressive_Est'] == True).astype(int)

# Remove any NaN values
df_reg = df_reg.dropna(subset=['PlyCount', 'RatingDiff'])

X1 = df_reg[['Is_MvF']].values
y = df_reg['PlyCount'].values

model1 = LinearRegression()
model1.fit(X1, y)
r2_1 = model1.score(X1, y)

print(f"\nModel 1: Opponent Gender Effect")
print(f"  Coefficient (Is_MvF): {model1.coef_[0]:.4f}")
print(f"  Intercept: {model1.intercept_:.4f}")
print(f"  R²: {r2_1:.6f}")

X2 = df_reg[['Is_MvF', 'RatingDiff']].values
model2 = LinearRegression()
model2.fit(X2, y)
r2_2 = model2.score(X2, y)

print(f"\nModel 2: Gender + Rating Difference")
print(f"  Coefficient (Is_MvF): {model2.coef_[0]:.4f}")
print(f"  Coefficient (RatingDiff): {model2.coef_[1]:.6f}")
print(f"  R²: {r2_2:.6f}")

X3 = np.column_stack([
    df_reg['Is_MvF_Confirmed'],
    df_reg['Is_MvF_Perceived'],
    df_reg['RatingDiff'],
    df_reg['Is_Aggressive']
])
model3 = LinearRegression()
model3.fit(X3, y)
r2_3 = model3.score(X3, y)

print(f"\nModel 3: Gender + Rating + Aggressiveness")
print(f"  Coefficient (Is_MvF_Confirmed): {model3.coef_[0]:.4f}")
print(f"  Coefficient (Is_MvF_Perceived): {model3.coef_[1]:.4f}")
print(f"  Coefficient (RatingDiff): {model3.coef_[2]:.6f}")
print(f"  Coefficient (IsAggressive): {model3.coef_[3]:.4f}")
print(f"  R²: {r2_3:.6f}")

# ============= VISUALIZATIONS =============
print("\n" + "=" * 80)
print("GENERATING VISUALIZATIONS")
print("=" * 80)

fig, axes = plt.subplots(2, 3, figsize=(18, 12))

# 1. Box plot: Ply count by pairing
ax1 = axes[0, 0]
data_for_box = [df_mvm['PlyCount'].values, df_mvf['PlyCount'].values, df_mvpf['PlyCount'].values]
bp = ax1.boxplot(data_for_box, labels=['Male vs Male', 'Male vs Female\n(Confirmed)', 'Male vs Perceived\nFemale'], 
                 patch_artist=True, showmeans=True)
for patch, color in zip(bp['boxes'], ['#3498db', '#e74c3c', '#f39c12']):
    patch.set_facecolor(color)
    patch.set_alpha(0.7)
ax1.set_ylabel('Game Length (Plies)', fontsize=12, fontweight='bold')
ax1.set_title(f'RQ1: Resignation Times (Expanded Sample)\nMvM n={len(df_mvm):,}, MvF-conf n={len(df_mvf):,}, MvF-perc n={len(df_mvpf):,}', 
             fontsize=12, fontweight='bold')
ax1.grid(True, alpha=0.3, axis='y')

# 2. Bar plot: Aggressiveness
ax2 = axes[0, 1]
aggr_vals = [mvm_aggr, (df_mvf['IsAggressive_Est'] == True).mean() * 100 if len(df_mvf) else np.nan, mvpf_aggr]
bars = ax2.bar(['Male vs Male', 'Male vs Female\n(Confirmed)', 'Male vs Perceived\nFemale'], aggr_vals, 
              color=['#3498db', '#e74c3c', '#f39c12'], alpha=0.7, edgecolor='black', linewidth=1.5)
ax2.set_ylabel('Aggressive Openings %', fontsize=12, fontweight='bold')
ax2.set_title('Opening Aggressiveness by Pairing', fontsize=12, fontweight='bold')
ax2.set_ylim(0, np.nanmax(aggr_vals) * 1.2)
for bar, val in zip(bars, aggr_vals):
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, 
            f'{val:.1f}%', ha='center', fontsize=11, fontweight='bold')
ax2.grid(True, alpha=0.3, axis='y')

# 3. Distribution of ply counts
ax3 = axes[0, 2]
hist_data = [df_mvm['PlyCount'], df_mvf['PlyCount']]
hist_labels = ['Male vs Male', 'Male vs Female (Confirmed)']
hist_colors = ['#3498db', '#e74c3c']
if len(df_mvpf) > 0:
    hist_data.append(df_mvpf['PlyCount'])
    hist_labels.append('Male vs Perceived Female')
    hist_colors.append('#f39c12')
ax3.hist(hist_data, bins=50, 
    label=hist_labels,
    color=hist_colors, alpha=0.6, edgecolor='black')
ax3.set_xlabel('Game Length (Plies)', fontsize=12, fontweight='bold')
ax3.set_ylabel('Frequency', fontsize=12, fontweight='bold')
ax3.set_title('Distribution of Game Lengths', fontsize=12, fontweight='bold')
ax3.legend(fontsize=10)
ax3.grid(True, alpha=0.3, axis='y')

# 4. Rating difference vs ply count
ax4 = axes[1, 0]
ax4.scatter(df_mvm['RatingDiff'], df_mvm['PlyCount'], alpha=0.3, s=20,
           color='#3498db', label='Male vs Male')
ax4.scatter(df_mvf['RatingDiff'], df_mvf['PlyCount'], alpha=0.5, s=40,
           color='#e74c3c', label='Male vs Female', edgecolors='black', linewidth=0.5)
if len(df_mvpf) > 0:
    ax4.scatter(df_mvpf['RatingDiff'], df_mvpf['PlyCount'], alpha=0.5, s=40,
               color='#f39c12', label='Male vs Perceived Female', edgecolors='black', linewidth=0.5)
ax4.set_xlabel('Rating Difference (White - Black)', fontsize=12, fontweight='bold')
ax4.set_ylabel('Game Length (Plies)', fontsize=12, fontweight='bold')
ax4.set_title('Rating Difference vs Game Length', fontsize=12, fontweight='bold')
ax4.legend(fontsize=10)
ax4.grid(True, alpha=0.3)

# 5. Elo distribution by pairing
ax5 = axes[1, 1]
elo_hist_data = [df_mvm['White_Elo'], df_mvf['White_Elo']]
elo_hist_labels = ['Male vs Male', 'Male vs Female (Confirmed)']
elo_hist_colors = ['#3498db', '#e74c3c']
if len(df_mvpf) > 0:
    elo_hist_data.append(df_mvpf['White_Elo'])
    elo_hist_labels.append('Male vs Perceived Female')
    elo_hist_colors.append('#f39c12')
ax5.hist(elo_hist_data, bins=30,
    label=elo_hist_labels,
    color=elo_hist_colors, alpha=0.6, edgecolor='black')
ax5.set_xlabel('White Player Elo', fontsize=12, fontweight='bold')
ax5.set_ylabel('Frequency', fontsize=12, fontweight='bold')
ax5.set_title('Player Skill Distribution by Pairing', fontsize=12, fontweight='bold')
ax5.legend(fontsize=10)
ax5.grid(True, alpha=0.3, axis='y')

# 6. Summary statistics table
ax6 = axes[1, 2]
ax6.axis('off')

summary_text = f"""
EXPANDED RQ1 ANALYSIS SUMMARY

Sample Sizes:
  Male vs Male: {len(df_mvm):,} games
    Male vs Female (Confirmed): {len(df_mvf):,} games
    Male vs Perceived Female: {len(df_mvpf):,} games
    Male vs Female (All): {len(df_mvf_all):,} games

Resignation Time (Plies):
  MvM: {mvm_mean:.1f} ± {mvm_std:.1f}
  MvF: {mvf_mean:.1f} ± {mvf_std:.1f}
  Diff: {mvf_mean - mvm_mean:.2f}
  p-value: {p_value:.4f}

Aggressiveness:
  MvM: {mvm_aggr:.1f}%
  MvF: {mvf_aggr:.1f}%
  Diff: {mvm_aggr - mvf_aggr:.1f}pp
  p-value: {p_chi:.4f}

Regression (Model 3):
    MvF-confirmed coef: {model3.coef_[0]:.4f}
    MvF-perceived coef: {model3.coef_[1]:.4f}
    Rating coef: {model3.coef_[2]:.6f}
    Aggr coef: {model3.coef_[3]:.4f}
  R²: {r2_3:.6f}
"""

ax6.text(0.05, 0.95, summary_text, transform=ax6.transAxes,
        fontsize=10, verticalalignment='top', fontfamily='monospace',
        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

plt.tight_layout()
plt.savefig('analysis/plots/rq1_expanded_analysis.png', dpi=300, bbox_inches='tight')
print("✓ Saved: rq1_expanded_analysis.png")
plt.close()

# ============= COMPARISON WITH ORIGINAL =============
print("\n" + "=" * 80)
print("COMPARISON: ORIGINAL VS EXPANDED DATASET")
print("=" * 80)

# Load original results
df_orig_results = pd.read_csv('analysis/rq1_regression_results.csv')

print(f"\nOriginal RQ1 Dataset:")
print(f"  Games analyzed: {int(df_orig_results.loc[0, 'Total_Games_Analyzed']):,}")
print(f"  MvF games: {int(df_orig_results.loc[0, 'Male_vs_Female_Games'])}")
print(f"  MvM games: {int(df_orig_results.loc[0, 'Male_vs_Male_Games']):,}")
print(f"  Resignation diff: {float(df_orig_results.loc[0, 'Resignation_Difference_Plies']):.2f} plies (p={float(df_orig_results.loc[0, 'Resignation_Ttest_Pvalue']):.4f})")

print(f"\nExpanded RQ1 Dataset:")
print(f"  Games analyzed: {len(df_analysis):,}")
print(f"  MvF-confirmed games: {len(df_mvf)}")
print(f"  MvF-perceived games: {len(df_mvpf)}")
print(f"  MvF-all games: {len(df_mvf_all)}")
print(f"  MvM games: {len(df_mvm):,}")
print(f"  Resignation diff: {mvf_mean - mvm_mean:.2f} plies (p={p_value:.4f})")

print(f"\nSample Size Change:")
print(f"  Total: {len(df_analysis) / int(df_orig_results.loc[0, 'Total_Games_Analyzed']):.2f}x")
print(f"  Female opponents (confirmed only): {len(df_mvf) / int(df_orig_results.loc[0, 'Male_vs_Female_Games']):.2f}x")
print(f"  Female opponents (confirmed + perceived): {len(df_mvf_all) / int(df_orig_results.loc[0, 'Male_vs_Female_Games']):.2f}x")

# Save results
results = pd.DataFrame([{
    'Dataset': 'Expanded Lichess (All Elite Games)',
    'Total_Games': len(df_analysis),
    'MvF_Games': len(df_mvf),
    'MvPF_Games': len(df_mvpf),
    'MvF_All_Games': len(df_mvf_all),
    'MvM_Games': len(df_mvm),
    'Resignation_MvF_Mean': mvf_mean,
    'Resignation_MvM_Mean': mvm_mean,
    'Resignation_Diff': mvf_mean - mvm_mean,
    'Resignation_Pvalue': p_value,
    'Aggressiveness_MvF': mvf_aggr,
    'Aggressiveness_MvM': mvm_aggr,
    'Aggressiveness_Diff': mvm_aggr - mvf_aggr,
    'Chi2_Pvalue': p_chi,
    'Model3_R2': r2_3
}])

results.to_csv('analysis/rq1_expanded_results.csv', index=False)
print("\n✓ Saved: rq1_expanded_results.csv")

print("\n" + "=" * 80)
print("✓ EXPANDED RQ1 ANALYSIS COMPLETE")
print("=" * 80)
