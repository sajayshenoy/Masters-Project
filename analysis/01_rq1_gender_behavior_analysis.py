"""
RQ1: Gender-Based Behavioral Differences Analysis
==================================================
To analyze:
1. Resignation behavior (game length in lost positions)
2. Decision quality (blunder rates if available, else proxy metrics)
3. Time allocation and strategic choices
4. Comparisons: Male vs Female, Male vs Perceived Female, Male vs Male
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 8)
plt.rcParams['font.size'] = 10

print("=" * 70)
print("RQ1 ANALYSIS: GENDER-BASED BEHAVIORAL DIFFERENCES")
print("=" * 70)

# Load data
df_games = pd.read_csv('data/rq1_behavior_analysis.csv')
df_players = pd.read_csv('data/unified_chess_players_with_inferred_gender.csv')

# Create player gender lookup
player_gender_map = dict(zip(df_players['name'], df_players['sex']))

# Add player gender (white player)
df_games['White_Sex'] = df_games['White_Unified_Name'].map(player_gender_map)

# Rename for clarity
df_games.rename(columns={'Black_Sex': 'Opponent_Sex'}, inplace=True)

# Filter to records where we have both player and opponent gender
df_analysis = df_games[
    (df_games['White_Sex'].notna()) & 
    (df_games['Opponent_Sex'] != 'unknown')
].copy()

print(f"\nTotal games: {len(df_games):,}")
print(f"Games with complete gender info: {len(df_analysis):,}")

# ========== CREATE GENDER PAIRINGS ==========
print("\n" + "=" * 70)
print("1. GAME DISTRIBUTION BY GENDER PAIRING")
print("=" * 70)

# Create gender pairing categories
def create_pairing(player_sex, opponent_sex):
    """Create gender pairing category"""
    if pd.isna(player_sex) or pd.isna(opponent_sex):
        return 'Unknown'
    
    # Only use M and F (filter out 'unknown')
    if player_sex == 'unknown' or opponent_sex == 'unknown':
        return 'Unknown'
    
    if player_sex == 'M' and opponent_sex == 'M':
        return 'Male vs Male'
    elif player_sex == 'M' and opponent_sex == 'F':
        return 'Male vs Female'
    elif player_sex == 'F' and opponent_sex == 'M':
        return 'Female vs Male'
    elif player_sex == 'F' and opponent_sex == 'F':
        return 'Female vs Female'
    else:
        return 'Unknown'

df_analysis['Pairing'] = df_analysis.apply(
    lambda row: create_pairing(row['White_Sex'], row['Opponent_Sex']), 
    axis=1
)

# Filter to only clear pairings (remove 'Unknown')
df_analysis = df_analysis[df_analysis['Pairing'] != 'Unknown'].copy()

pairing_counts = df_analysis['Pairing'].value_counts()
print(f"\nGames by pairing:")
for pairing, count in pairing_counts.items():
    print(f"  {pairing:30s}: {count:>6,} ({count/len(df_analysis)*100:>5.1f}%)")

# ========== RESIGNATION TIME ANALYSIS ==========
print("\n" + "=" * 70)
print("2. RESIGNATION TIME ANALYSIS (PlyCount)")
print("=" * 70)

resignation_stats = df_analysis.groupby('Pairing')['PlyCount'].agg([
    'count', 'mean', 'median', 'std', 'min', 'max'
]).round(2)

print(f"\nResignation statistics by pairing:")
print(resignation_stats)

# Detailed statistics for Male vs Female (focus on main RQ)
mvf = df_analysis[df_analysis['Pairing'] == 'Male vs Female']['PlyCount']
mvm = df_analysis[df_analysis['Pairing'] == 'Male vs Male']['PlyCount']

print(f"\nKey Comparison: Male vs Female vs Male vs Male")
print(f"  Male vs Female - Mean: {mvf.mean():.2f}, Median: {mvf.median():.0f}")
print(f"  Male vs Male   - Mean: {mvm.mean():.2f}, Median: {mvm.median():.0f}")
print(f"  Difference     - Mean: {mvf.mean() - mvm.mean():.2f} plies")

# T-test
t_stat, p_value = stats.ttest_ind(mvf, mvm)
print(f"\n  T-test: t={t_stat:.4f}, p={p_value:.4f}")
if p_value < 0.05:
    print(f"  ✓ SIGNIFICANT: Players resign {('later' if mvf.mean() > mvm.mean() else 'earlier')} against females")
else:
    print(f"  ✗ NOT SIGNIFICANT: No significant difference in resignation time")

# ========== STRATEGIC CHOICES (AGGRESSIVENESS) ==========
print("\n" + "=" * 70)
print("3. STRATEGIC CHOICES: OPENING AGGRESSIVENESS")
print("=" * 70)

aggr_stats = df_analysis.groupby('Pairing')['IsAggressive'].agg([
    lambda x: (x == True).sum(),
    lambda x: (x == True).sum() / len(x) * 100,
    'count'
]).round(2)
aggr_stats.columns = ['Aggressive_Count', 'Aggressive_Pct', 'Total']

print(f"\nAggressiveness by pairing:")
print(aggr_stats)

# Extract percentages
mvf_aggr = (df_analysis[df_analysis['Pairing'] == 'Male vs Female']['IsAggressive'] == True).sum() / \
           len(df_analysis[df_analysis['Pairing'] == 'Male vs Female']) * 100
mvm_aggr = (df_analysis[df_analysis['Pairing'] == 'Male vs Male']['IsAggressive'] == True).sum() / \
           len(df_analysis[df_analysis['Pairing'] == 'Male vs Male']) * 100

print(f"\nKey Finding:")
print(f"  Male vs Female: {mvf_aggr:.1f}% aggressive openings")
print(f"  Male vs Male:   {mvm_aggr:.1f}% aggressive openings")
print(f"  Difference:     {mvm_aggr - mvf_aggr:.1f} percentage points")

# Chi-square test
contingency = pd.crosstab(
    df_analysis['Pairing'],
    df_analysis['IsAggressive']
)
chi2, p_chi, dof, expected = stats.chi2_contingency(contingency)
print(f"\n  Chi-square test: χ²={chi2:.4f}, p={p_chi:.4f}")
if p_chi < 0.05:
    print(f"  ✓ SIGNIFICANT: Players choose different opening strategies")

# ========== RATING DIFFERENCE EFFECT ==========
print("\n" + "=" * 70)
print("4. RATING DIFFERENCE EFFECT ON GAME LENGTH")
print("=" * 70)

rating_stats = df_analysis.groupby('Pairing')['RatingDiff'].agg([
    'mean', 'median', 'std'
]).round(2)

print(f"\nRating difference by pairing:")
print(rating_stats)

# ========== REGRESSION MODELS ==========
print("\n" + "=" * 70)
print("5. REGRESSION MODELS: EXPLAINING RESIGNATION TIME")
print("=" * 70)

# Prepare data for regression
df_reg = df_analysis.copy()

# Encode categorical variables
df_reg['Is_MvsF'] = (df_reg['Pairing'] == 'Male vs Female').astype(int)
df_reg['Is_Aggressive'] = (df_reg['IsAggressive'] == True).astype(int)

# Model 1: Basic model - Opponent gender effect
reg_data = df_reg[['Is_MvsF', 'PlyCount', 'RatingDiff']].copy()
X1 = reg_data[['Is_MvsF']].values
y = reg_data['PlyCount'].values

model1 = LinearRegression()
model1.fit(X1, y)
r2_1 = model1.score(X1, y)

print(f"\nModel 1: Effect of Opponent Gender on Game Length")
print(f"  Coefficient (Is_MvsF): {model1.coef_[0]:.4f}")
print(f"  Intercept: {model1.intercept_:.4f}")
print(f"  R² Score: {r2_1:.4f}")

# Model 2: Multi-variable model
X2 = reg_data[['Is_MvsF', 'RatingDiff']].values
model2 = LinearRegression()
model2.fit(X2, y)
r2_2 = model2.score(X2, y)

print(f"\nModel 2: Opponent Gender + Rating Difference")
print(f"  Coefficient (Is_MvsF): {model2.coef_[0]:.4f}")
print(f"  Coefficient (RatingDiff): {model2.coef_[1]:.4f}")
print(f"  R² Score: {r2_2:.4f}")

# Model 3: Add aggressiveness
X3 = reg_data[['Is_MvsF', 'RatingDiff']].copy()
X3['Is_Aggressive'] = df_reg['Is_Aggressive'].values
X3 = X3.values

model3 = LinearRegression()
model3.fit(X3, y)
r2_3 = model3.score(X3, y)

print(f"\nModel 3: Opponent Gender + Rating Difference + Aggressiveness")
print(f"  Coefficient (Is_MvsF): {model3.coef_[0]:.4f}")
print(f"  Coefficient (RatingDiff): {model3.coef_[1]:.4f}")
print(f"  Coefficient (Is_Aggressive): {model3.coef_[2]:.4f}")
print(f"  R² Score: {r2_3:.4f}")

# ========== VISUALIZATIONS ==========
print("\n" + "=" * 70)
print("6. GENERATING VISUALIZATIONS")
print("=" * 70)

fig, axes = plt.subplots(2, 2, figsize=(16, 12))

# 1. Box plot: Resignation times by pairing
ax1 = axes[0, 0]
pairing_order = ['Male vs Male', 'Male vs Female']
data_for_box = [df_analysis[df_analysis['Pairing'] == p]['PlyCount'].values 
                 for p in pairing_order]
bp = ax1.boxplot(data_for_box, labels=pairing_order, patch_artist=True)
for patch, color in zip(bp['boxes'], ['#3498db', '#e74c3c']):
    patch.set_facecolor(color)
    patch.set_alpha(0.7)
ax1.set_ylabel('Game Length (Plies)', fontsize=12, fontweight='bold')
ax1.set_title('RQ1.1: Resignation Time by Gender Pairing', fontsize=13, fontweight='bold')
ax1.grid(True, alpha=0.3)

# 2. Bar plot: Aggressiveness comparison
ax2 = axes[0, 1]
aggr_by_pairing = []
labels_aggr = []
for pairing in pairing_order:
    pct = (df_analysis[df_analysis['Pairing'] == pairing]['IsAggressive'] == True).sum() / \
          len(df_analysis[df_analysis['Pairing'] == pairing]) * 100
    aggr_by_pairing.append(pct)
    labels_aggr.append(pairing)

bars = ax2.bar(labels_aggr, aggr_by_pairing, color=['#3498db', '#e74c3c'], alpha=0.7, edgecolor='black', linewidth=1.5)
ax2.set_ylabel('Aggressive Opening %', fontsize=12, fontweight='bold')
ax2.set_title('RQ1.3: Opening Aggressiveness by Gender Pairing', fontsize=13, fontweight='bold')
ax2.set_ylim(0, max(aggr_by_pairing) * 1.2)
for i, (bar, val) in enumerate(zip(bars, aggr_by_pairing)):
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, 
             f'{val:.1f}%', ha='center', fontsize=11, fontweight='bold')
ax2.grid(True, alpha=0.3, axis='y')

# 3. Scatter: Rating difference vs Game length
ax3 = axes[1, 0]
for pairing, color in zip(pairing_order, ['#3498db', '#e74c3c']):
    data = df_analysis[df_analysis['Pairing'] == pairing]
    ax3.scatter(data['RatingDiff'], data['PlyCount'], alpha=0.4, s=30, 
                label=pairing, color=color)
ax3.set_xlabel('Rating Difference', fontsize=12, fontweight='bold')
ax3.set_ylabel('Game Length (Plies)', fontsize=12, fontweight='bold')
ax3.set_title('RQ1.2: Rating Difference vs Resignation Time', fontsize=13, fontweight='bold')
ax3.legend(fontsize=11)
ax3.grid(True, alpha=0.3)

# 4. Distribution: Game length by pairing
ax4 = axes[1, 1]
for pairing, color in zip(pairing_order, ['#3498db', '#e74c3c']):
    data = df_analysis[df_analysis['Pairing'] == pairing]['PlyCount']
    ax4.hist(data, bins=50, alpha=0.6, label=pairing, color=color, edgecolor='black')
ax4.set_xlabel('Game Length (Plies)', fontsize=12, fontweight='bold')
ax4.set_ylabel('Frequency', fontsize=12, fontweight='bold')
ax4.set_title('RQ1.1: Distribution of Game Lengths', fontsize=13, fontweight='bold')
ax4.legend(fontsize=11)
ax4.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('analysis/plots/rq1_comprehensive_analysis.png', dpi=300, bbox_inches='tight')
print("  ✓ Saved: rq1_comprehensive_analysis.png")
plt.close()

# ========== SAVE RESULTS ==========
print("\n" + "=" * 70)
print("7. SAVING ANALYSIS RESULTS")
print("=" * 70)

results = {
    'Research_Question': 'RQ1: Gender-Based Behavioral Differences',
    'Total_Games_Analyzed': len(df_analysis),
    'Male_vs_Female_Games': len(df_analysis[df_analysis['Pairing'] == 'Male vs Female']),
    'Male_vs_Male_Games': len(df_analysis[df_analysis['Pairing'] == 'Male vs Male']),
    'Resignation_MvF_Mean': mvf.mean(),
    'Resignation_MvM_Mean': mvm.mean(),
    'Resignation_Difference_Plies': mvf.mean() - mvm.mean(),
    'Resignation_Ttest_Pvalue': p_value,
    'Aggressiveness_MvF_Pct': mvf_aggr,
    'Aggressiveness_MvM_Pct': mvm_aggr,
    'Aggressiveness_Difference_Pct': mvm_aggr - mvf_aggr,
    'Chi2_Pvalue': p_chi,
    'Regression_Model3_R2': r2_3,
    'Regression_Gender_Coefficient': model3.coef_[0],
    'Regression_Rating_Coefficient': model3.coef_[1],
    'Regression_Aggressiveness_Coefficient': model3.coef_[2]
}

results_df = pd.DataFrame([results])
results_df.to_csv('analysis/rq1_regression_results.csv', index=False)
print("  ✓ Saved: rq1_regression_results.csv")

# Save detailed game-level analysis
df_analysis.to_csv('analysis/rq1_games_with_pairings.csv', index=False)
print("  ✓ Saved: rq1_games_with_pairings.csv")

print("\n" + "=" * 70)
print("RQ1 ANALYSIS COMPLETE")
print("=" * 70)
