"""
RQ2: Opening Repertoire Adaptation and Performance
====================================================
To analyze:
1. Aggressive opening choices vs opponent strength (rating)
2. Opening diversity correlation with rating growth
3. Opponent rating differences effect on opening choice
4. Regression models for opening choice and rating impact
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
print("RQ2 ANALYSIS: OPENING REPERTOIRE ADAPTATION")
print("=" * 70)

# Load data
df_analysis = pd.read_csv('data/rq2_opening_analysis.csv')
df_players = pd.read_csv('data/unified_chess_players_with_inferred_gender.csv')

# Create player gender lookup
player_gender_map = dict(zip(df_players['name'], df_players['sex']))

# Add player gender
df_analysis['Player_Sex'] = df_analysis['Player'].map(player_gender_map)

# Filter to players with known gender (not 'unknown' and not null)
df_analysis = df_analysis[
    (df_analysis['Player_Sex'].notna()) & 
    (df_analysis['Player_Sex'] != 'unknown')
].copy()

print(f"\nTotal players in analysis: {len(df_analysis):,}")
print(f"\nGender distribution:")
gender_dist = df_analysis['Player_Sex'].value_counts()
for gender, count in gender_dist.items():
    print(f"  {gender}: {count:,} ({count/len(df_analysis)*100:.1f}%)")

platform_dist = df_analysis['Platform'].value_counts()
print(f"\nPlatform distribution:")
for platform, count in platform_dist.items():
    print(f"  {platform}: {count:,} ({count/len(df_analysis)*100:.1f}%)")

# ========== RATING ANALYSIS ==========
print("\n" + "=" * 70)
print("1. PLAYER RATING DISTRIBUTION")
print("=" * 70)

rating_stats = df_analysis.groupby('Player_Sex')['AvgRating'].agg([
    'count', 'mean', 'median', 'std', 'min', 'max'
]).round(2)

print(f"\nRating statistics by gender:")
print(rating_stats)

# Separate male and female players
df_male = df_analysis[df_analysis['Player_Sex'] == 'M'].copy()
df_female = df_analysis[df_analysis['Player_Sex'] == 'F'].copy()

male_rating = df_male['AvgRating'].mean()
female_rating = df_female['AvgRating'].mean()

print(f"\nKey Finding:")
print(f"  Male players avg rating: {male_rating:.1f}")
print(f"  Female players avg rating: {female_rating:.1f}")
print(f"  Difference: {male_rating - female_rating:.1f} points")

# T-test
t_stat, p_value = stats.ttest_ind(df_male['AvgRating'], df_female['AvgRating'])
print(f"  T-test: t={t_stat:.4f}, p={p_value:.4f}")

# ========== OPENING DIVERSITY ANALYSIS ==========
print("\n" + "=" * 70)
print("2. OPENING DIVERSITY (SHANNON ENTROPY)")
print("=" * 70)

diversity_stats = df_analysis.groupby('Player_Sex')['OpeningDiversity'].agg([
    'count', 'mean', 'median', 'std'
]).round(4)

print(f"\nOpening diversity by gender:")
print(diversity_stats)

male_div = df_male['OpeningDiversity'].mean()
female_div = df_female['OpeningDiversity'].mean()

print(f"\nKey Finding:")
print(f"  Male players avg diversity: {male_div:.4f}")
print(f"  Female players avg diversity: {female_div:.4f}")
print(f"  Difference: {male_div - female_div:.4f}")

# Correlation: Rating vs Diversity
corr_male_rating_div = df_male['AvgRating'].corr(df_male['OpeningDiversity'])
corr_female_rating_div = df_female['AvgRating'].corr(df_female['OpeningDiversity'])

print(f"\nCorrelation between Rating and Opening Diversity:")
print(f"  Male players: r = {corr_male_rating_div:.4f}")
print(f"  Female players: r = {corr_female_rating_div:.4f}")

# ========== AGGRESSIVENESS ANALYSIS ==========
print("\n" + "=" * 70)
print("3. OPENING AGGRESSIVENESS ANALYSIS")
print("=" * 70)

aggr_stats = df_analysis.groupby('Player_Sex')['Aggressiveness'].agg([
    'count', 'mean', 'median', 'std'
]).round(4)

print(f"\nAggressiveness by gender:")
print(aggr_stats)

male_aggr = df_male['Aggressiveness'].mean()
female_aggr = df_female['Aggressiveness'].mean()

print(f"\nKey Finding:")
print(f"  Male players avg aggressiveness: {male_aggr:.4f} ({male_aggr*100:.1f}%)")
print(f"  Female players avg aggressiveness: {female_aggr:.4f} ({female_aggr*100:.1f}%)")
print(f"  Difference: {(male_aggr - female_aggr)*100:.1f} percentage points")

# Correlation: Rating vs Aggressiveness
corr_male_rating_aggr = df_male['AvgRating'].corr(df_male['Aggressiveness'])
corr_female_rating_aggr = df_female['AvgRating'].corr(df_female['Aggressiveness'])

print(f"\nCorrelation between Rating and Aggressiveness:")
print(f"  Male players: r = {corr_male_rating_aggr:.4f}")
print(f"  Female players: r = {corr_female_rating_aggr:.4f}")

# ========== REGRESSION MODELS ==========
print("\n" + "=" * 70)
print("4. REGRESSION MODELS: PREDICTING OPENING CHOICES")
print("=" * 70)

# Create binary gender variable (1 = Female, 0 = Male)
df_reg = df_analysis.copy()
df_reg['Is_Female'] = (df_reg['Player_Sex'] == 'F').astype(int)

# Standardize rating for interpretation
scaler = StandardScaler()
df_reg['AvgRating_Scaled'] = scaler.fit_transform(df_reg[['AvgRating']])

# ===== MODEL 1: Aggressiveness =====
print("\nMODEL A: Predicting AGGRESSIVENESS")

X1_aggr = df_reg[['AvgRating_Scaled']].values
y_aggr = df_reg['Aggressiveness'].values

model1_aggr = LinearRegression()
model1_aggr.fit(X1_aggr, y_aggr)
r2_1_aggr = model1_aggr.score(X1_aggr, y_aggr)

print(f"\n  Model A1: Rating Effect on Aggressiveness")
print(f"    Coefficient (Rating): {model1_aggr.coef_[0]:.6f}")
print(f"    Intercept: {model1_aggr.intercept_:.6f}")
print(f"    R² Score: {r2_1_aggr:.6f}")

# Model A2: Rating + Gender
X2_aggr = df_reg[['AvgRating_Scaled', 'Is_Female']].values
model2_aggr = LinearRegression()
model2_aggr.fit(X2_aggr, y_aggr)
r2_2_aggr = model2_aggr.score(X2_aggr, y_aggr)

print(f"\n  Model A2: Rating + Gender Effect on Aggressiveness")
print(f"    Coefficient (Rating): {model2_aggr.coef_[0]:.6f}")
print(f"    Coefficient (Is_Female): {model2_aggr.coef_[1]:.6f}")
print(f"    R² Score: {r2_2_aggr:.6f}")

# Model A3: Rating + Gender + Platform + Games
df_reg['Platform_Encoded'] = (df_reg['Platform'] == 'Lichess').astype(int)
X3_aggr = df_reg[['AvgRating_Scaled', 'Is_Female', 'Platform_Encoded', 'GamesCount']].values
# Log-transform GamesCount to reduce skewness
X3_aggr[:, 3] = np.log1p(X3_aggr[:, 3])

model3_aggr = LinearRegression()
model3_aggr.fit(X3_aggr, y_aggr)
r2_3_aggr = model3_aggr.score(X3_aggr, y_aggr)

print(f"\n  Model A3: Rating + Gender + Platform + Games (Multi-variable)")
print(f"    Coefficient (Rating): {model3_aggr.coef_[0]:.6f}")
print(f"    Coefficient (Is_Female): {model3_aggr.coef_[1]:.6f}")
print(f"    Coefficient (Platform): {model3_aggr.coef_[2]:.6f}")
print(f"    Coefficient (Log GamesCount): {model3_aggr.coef_[3]:.6f}")
print(f"    R² Score: {r2_3_aggr:.6f}")

# ===== MODEL 2: Opening Diversity =====
print("\n\nMODEL B: Predicting OPENING DIVERSITY")

y_div = df_reg['OpeningDiversity'].values

X1_div = df_reg[['AvgRating_Scaled']].values
model1_div = LinearRegression()
model1_div.fit(X1_div, y_div)
r2_1_div = model1_div.score(X1_div, y_div)

print(f"\n  Model B1: Rating Effect on Diversity")
print(f"    Coefficient (Rating): {model1_div.coef_[0]:.6f}")
print(f"    R² Score: {r2_1_div:.6f}")

X2_div = df_reg[['AvgRating_Scaled', 'Is_Female']].values
model2_div = LinearRegression()
model2_div.fit(X2_div, y_div)
r2_2_div = model2_div.score(X2_div, y_div)

print(f"\n  Model B2: Rating + Gender Effect on Diversity")
print(f"    Coefficient (Rating): {model2_div.coef_[0]:.6f}")
print(f"    Coefficient (Is_Female): {model2_div.coef_[1]:.6f}")
print(f"    R² Score: {r2_2_div:.6f}")

X3_div = df_reg[['AvgRating_Scaled', 'Is_Female', 'Platform_Encoded', 'GamesCount']].values
X3_div[:, 3] = np.log1p(X3_div[:, 3])

model3_div = LinearRegression()
model3_div.fit(X3_div, y_div)
r2_3_div = model3_div.score(X3_div, y_div)

print(f"\n  Model B3: Rating + Gender + Platform + Games (Multi-variable)")
print(f"    Coefficient (Rating): {model3_div.coef_[0]:.6f}")
print(f"    Coefficient (Is_Female): {model3_div.coef_[1]:.6f}")
print(f"    Coefficient (Platform): {model3_div.coef_[2]:.6f}")
print(f"    Coefficient (Log GamesCount): {model3_div.coef_[3]:.6f}")
print(f"    R² Score: {r2_3_div:.6f}")

# ========== VISUALIZATIONS ==========
print("\n" + "=" * 70)
print("5. GENERATING VISUALIZATIONS")
print("=" * 70)

fig, axes = plt.subplots(2, 3, figsize=(18, 12))

# 1. Rating distribution by gender
ax1 = axes[0, 0]
ax1.hist([df_male['AvgRating'].values, df_female['AvgRating'].values], 
         bins=30, label=['Male', 'Female'], color=['#3498db', '#e74c3c'], alpha=0.7, edgecolor='black')
ax1.set_xlabel('Average Rating', fontsize=11, fontweight='bold')
ax1.set_ylabel('Frequency', fontsize=11, fontweight='bold')
ax1.set_title('Rating Distribution by Gender', fontsize=12, fontweight='bold')
ax1.legend(fontsize=10)
ax1.grid(True, alpha=0.3, axis='y')

# 2. Opening Diversity by Gender
ax2 = axes[0, 1]
ax2.hist([df_male['OpeningDiversity'].values, df_female['OpeningDiversity'].values],
         bins=30, label=['Male', 'Female'], color=['#3498db', '#e74c3c'], alpha=0.7, edgecolor='black')
ax2.set_xlabel('Opening Diversity (Shannon Entropy)', fontsize=11, fontweight='bold')
ax2.set_ylabel('Frequency', fontsize=11, fontweight='bold')
ax2.set_title('Opening Diversity by Gender', fontsize=12, fontweight='bold')
ax2.legend(fontsize=10)
ax2.grid(True, alpha=0.3, axis='y')

# 3. Aggressiveness by Gender
ax3 = axes[0, 2]
aggr_data = [df_male['Aggressiveness'].values * 100, df_female['Aggressiveness'].values * 100]
ax3.hist(aggr_data, bins=30, label=['Male', 'Female'], 
         color=['#3498db', '#e74c3c'], alpha=0.7, edgecolor='black')
ax3.set_xlabel('Aggressiveness (%)', fontsize=11, fontweight='bold')
ax3.set_ylabel('Frequency', fontsize=11, fontweight='bold')
ax3.set_title('Opening Aggressiveness by Gender', fontsize=12, fontweight='bold')
ax3.legend(fontsize=10)
ax3.grid(True, alpha=0.3, axis='y')

# 4. Rating vs Diversity scatter
ax4 = axes[1, 0]
ax4.scatter(df_male['AvgRating'], df_male['OpeningDiversity'], 
           alpha=0.5, s=40, color='#3498db', label='Male')
ax4.scatter(df_female['AvgRating'], df_female['OpeningDiversity'],
           alpha=0.5, s=40, color='#e74c3c', label='Female')
# Add trend lines
z_male = np.polyfit(df_male['AvgRating'], df_male['OpeningDiversity'], 1)
p_male = np.poly1d(z_male)
z_female = np.polyfit(df_female['AvgRating'], df_female['OpeningDiversity'], 1)
p_female = np.poly1d(z_female)
x_range = np.linspace(df_analysis['AvgRating'].min(), df_analysis['AvgRating'].max(), 100)
ax4.plot(x_range, p_male(x_range), color='#3498db', linewidth=2, linestyle='--', alpha=0.8)
ax4.plot(x_range, p_female(x_range), color='#e74c3c', linewidth=2, linestyle='--', alpha=0.8)
ax4.set_xlabel('Average Rating', fontsize=11, fontweight='bold')
ax4.set_ylabel('Opening Diversity', fontsize=11, fontweight='bold')
ax4.set_title(f'RQ2.2: Rating vs Diversity (Male r={corr_male_rating_div:.3f}, Female r={corr_female_rating_div:.3f})', 
             fontsize=12, fontweight='bold')
ax4.legend(fontsize=10)
ax4.grid(True, alpha=0.3)

# 5. Rating vs Aggressiveness scatter
ax5 = axes[1, 1]
ax5.scatter(df_male['AvgRating'], df_male['Aggressiveness'] * 100,
           alpha=0.5, s=40, color='#3498db', label='Male')
ax5.scatter(df_female['AvgRating'], df_female['Aggressiveness'] * 100,
           alpha=0.5, s=40, color='#e74c3c', label='Female')
# Add trend lines
z_male_a = np.polyfit(df_male['AvgRating'], df_male['Aggressiveness'], 1)
p_male_a = np.poly1d(z_male_a)
z_female_a = np.polyfit(df_female['AvgRating'], df_female['Aggressiveness'], 1)
p_female_a = np.poly1d(z_female_a)
ax5.plot(x_range, p_male_a(x_range) * 100, color='#3498db', linewidth=2, linestyle='--', alpha=0.8)
ax5.plot(x_range, p_female_a(x_range) * 100, color='#e74c3c', linewidth=2, linestyle='--', alpha=0.8)
ax5.set_xlabel('Average Rating', fontsize=11, fontweight='bold')
ax5.set_ylabel('Aggressiveness (%)', fontsize=11, fontweight='bold')
ax5.set_title(f'RQ2.1: Rating vs Aggressiveness (Male r={corr_male_rating_aggr:.3f}, Female r={corr_female_rating_aggr:.3f})',
             fontsize=12, fontweight='bold')
ax5.legend(fontsize=10)
ax5.grid(True, alpha=0.3)

# 6. Comparison bars
ax6 = axes[1, 2]
metrics = ['Avg Rating', 'Diversity', 'Aggressiveness %']
male_vals = [male_rating/2700, male_div, male_aggr*100/50]  # Normalize for visibility
female_vals = [female_rating/2700, female_div, female_aggr*100/50]

x_pos = np.arange(len(metrics))
width = 0.35

bars1 = ax6.bar(x_pos - width/2, [male_rating/2700, male_div, male_aggr*100],
               width, label='Male', color='#3498db', alpha=0.7, edgecolor='black')
bars2 = ax6.bar(x_pos + width/2, [female_rating/2700, female_div, female_aggr*100],
               width, label='Female', color='#e74c3c', alpha=0.7, edgecolor='black')

ax6.set_ylabel('Normalized Values', fontsize=11, fontweight='bold')
ax6.set_title('RQ2 Summary: Gender Comparison', fontsize=12, fontweight='bold')
ax6.set_xticks(x_pos)
ax6.set_xticklabels(['Avg Rating\n(÷2700)', 'Diversity', 'Aggressiveness\n(%)'], fontsize=10)
ax6.legend(fontsize=10)
ax6.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('analysis/plots/rq2_comprehensive_analysis.png', dpi=300, bbox_inches='tight')
print("  ✓ Saved: rq2_comprehensive_analysis.png")
plt.close()

# ========== SAVE RESULTS ==========
print("\n" + "=" * 70)
print("6. SAVING ANALYSIS RESULTS")
print("=" * 70)

results = {
    'Research_Question': 'RQ2: Opening Repertoire Adaptation',
    'Total_Players_Analyzed': len(df_analysis),
    'Male_Players': len(df_male),
    'Female_Players': len(df_female),
    'Male_Avg_Rating': male_rating,
    'Female_Avg_Rating': female_rating,
    'Male_Avg_Diversity': male_div,
    'Female_Avg_Diversity': female_div,
    'Diversity_Corr_Male': corr_male_rating_div,
    'Diversity_Corr_Female': corr_female_rating_div,
    'Male_Avg_Aggressiveness': male_aggr,
    'Female_Avg_Aggressiveness': female_aggr,
    'Aggressiveness_Corr_Male': corr_male_rating_aggr,
    'Aggressiveness_Corr_Female': corr_female_rating_aggr,
    'Aggressiveness_Model_R2': r2_3_aggr,
    'Aggressiveness_Gender_Coef': model3_aggr.coef_[1],
    'Diversity_Model_R2': r2_3_div,
    'Diversity_Gender_Coef': model3_div.coef_[1]
}

results_df = pd.DataFrame([results])
results_df.to_csv('analysis/rq2_regression_results.csv', index=False)
print("  ✓ Saved: rq2_regression_results.csv")

# Save detailed player-level analysis
df_analysis.to_csv('analysis/rq2_players_with_metrics.csv', index=False)
print("  ✓ Saved: rq2_players_with_metrics.csv")

print("\n" + "=" * 70)
print("RQ2 ANALYSIS COMPLETE")
print("=" * 70)
