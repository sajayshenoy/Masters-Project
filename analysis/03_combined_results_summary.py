"""
Combined Research Results Summary
==================================
Creates a unified summary of all findings for both RQ1 and RQ2
"""

import pandas as pd
import json

# Load all results
rq1 = pd.read_csv('analysis/rq1_regression_results.csv')
rq2 = pd.read_csv('analysis/rq2_regression_results.csv')
gender_dist = pd.read_csv('analysis/gender_distribution_summary.csv')

# Create comprehensive summary
summary = {
    "Analysis_Metadata": {
        "Date": "February 26, 2026",
        "Dataset": "Unified Chess Players (33,713) + Lichess Elite Games (18,886)",
        "Analysis_Scripts": [
            "00_gender_inference_analysis.py",
            "01_rq1_gender_behavior_analysis.py", 
            "02_rq2_opening_repertoire_analysis.py"
        ]
    },
    
    "Gender_Distribution": {
        "Total_Players": int(gender_dist.loc[0, 'total_players']),
        "Male_Percentage": float(gender_dist.loc[0, 'male_pct']),
        "Female_Percentage": float(gender_dist.loc[0, 'female_pct']),
        "Unknown_Percentage": float(gender_dist.loc[0, 'unknown_pct']),
        "Source": {
            "From_FIDE": int(gender_dist.loc[0, 'male_fide_only'] + gender_dist.loc[0, 'female_fide_only']),
            "Inferred_by_Algorithm": int(gender_dist.loc[0, 'male_after_inference'] + gender_dist.loc[0, 'female_after_inference'] - gender_dist.loc[0, 'male_fide_only'] - gender_dist.loc[0, 'female_fide_only']),
            "Still_Unclassifiable": int(gender_dist.loc[0, 'still_unknown'])
        }
    },
    
    "RQ1_Findings": {
        "Research_Question": "Do players behave differently when facing female opponents?",
        "Games_Analyzed": int(rq1.loc[0, 'Total_Games_Analyzed']),
        "Male_vs_Female_Games": int(rq1.loc[0, 'Male_vs_Female_Games']),
        "Male_vs_Male_Games": int(rq1.loc[0, 'Male_vs_Male_Games']),
        
        "Sub_Question_1_1_Resignation_Time": {
            "Title": "Do players resign at later stages or worse positions against female opponents?",
            "Male_vs_Female_Mean_Plies": round(float(rq1.loc[0, 'Resignation_MvF_Mean']), 2),
            "Male_vs_Male_Mean_Plies": round(float(rq1.loc[0, 'Resignation_MvM_Mean']), 2),
            "Difference_Plies": round(float(rq1.loc[0, 'Resignation_Difference_Plies']), 2),
            "T_test_P_Value": round(float(rq1.loc[0, 'Resignation_Ttest_Pvalue']), 4),
            "Significant": False,
            "Conclusion": "Players do NOT resign significantly earlier or later against female opponents"
        },
        
        "Sub_Question_1_2_Decision_Quality": {
            "Title": "Is blunder rate or opening aggressiveness different vs female opponents?",
            "Male_vs_Female_Aggressive_Pct": round(float(rq1.loc[0, 'Aggressiveness_MvF_Pct']), 1),
            "Male_vs_Male_Aggressive_Pct": round(float(rq1.loc[0, 'Aggressiveness_MvM_Pct']), 1),
            "Difference_Percentage_Points": round(float(rq1.loc[0, 'Aggressiveness_Difference_Pct']), 1),
            "Chi2_P_Value": round(float(rq1.loc[0, 'Chi2_Pvalue']), 4),
            "Significant": False,
            "Conclusion": "Males show 7% lower aggressive openings vs females, but difference is NOT significant"
        },
        
        "Regression_Model": {
            "Variables": ["Opponent_Gender", "Rating_Difference", "Aggressiveness"],
            "R_Squared": round(float(rq1.loc[0, 'Regression_Model3_R2']), 4),
            "Intercept_Meaning": "Base game length ~84 plies",
            "Gender_Coefficient": round(float(rq1.loc[0, 'Regression_Gender_Coefficient']), 4),
            "Gender_Interpretation": "+1.22 plies longer when opponent is female",
            "Rating_Coefficient": round(float(rq1.loc[0, 'Regression_Rating_Coefficient']), 4),
            "Rating_Interpretation": "+0.021 plies per rating point difference",
            "Aggressiveness_Coefficient": round(float(rq1.loc[0, 'Regression_Aggressiveness_Coefficient']), 4),
            "Aggressiveness_Interpretation": "-0.98 plies shorter when opening is aggressive"
        },
        
        "Overall_Conclusion": "WEAK EVIDENCE: No statistically significant behavioral differences, small sample of female opponents (n=63)"
    },
    
    "RQ2_Findings": {
        "Research_Question": "Do players adapt opening repertoire depending on opponent rating and platform?",
        "Players_Analyzed": int(rq2.loc[0, 'Total_Players_Analyzed']),
        "Male_Players": int(rq2.loc[0, 'Male_Players']),
        "Female_Players": int(rq2.loc[0, 'Female_Players']),
        
        "Sub_Question_2_1_Aggressive_vs_Rating": {
            "Title": "Do players choose more aggressive openings against weaker opponents?",
            "Male_Avg_Aggressiveness_Pct": round(float(rq2.loc[0, 'Male_Avg_Aggressiveness']) * 100, 1),
            "Female_Avg_Aggressiveness_Pct": round(float(rq2.loc[0, 'Female_Avg_Aggressiveness']) * 100, 1),
            "Difference_Percentage_Points": round((float(rq2.loc[0, 'Female_Avg_Aggressiveness']) - float(rq2.loc[0, 'Male_Avg_Aggressiveness'])) * 100, 1),
            "Male_Rating_Correlation": round(float(rq2.loc[0, 'Aggressiveness_Corr_Male']), 4),
            "Female_Rating_Correlation": round(float(rq2.loc[0, 'Aggressiveness_Corr_Female']), 4),
            "R_Squared": round(float(rq2.loc[0, 'Aggressiveness_Model_R2']), 4),
            "Gender_Coefficient": round(float(rq2.loc[0, 'Aggressiveness_Gender_Coef']), 6),
            "Significant": False,
            "Conclusion": "NO: Players do NOT adapt aggressiveness based on opponent rating"
        },
        
        "Sub_Question_2_2_Diversity_Rating": {
            "Title": "Does opening diversity correlate with rating growth across platforms?",
            "Male_Avg_Diversity": round(float(rq2.loc[0, 'Male_Avg_Diversity']), 4),
            "Female_Avg_Diversity": round(float(rq2.loc[0, 'Female_Avg_Diversity']), 4),
            "Difference": round(float(rq2.loc[0, 'Male_Avg_Diversity']) - float(rq2.loc[0, 'Female_Avg_Diversity']), 4),
            "Male_Rating_Correlation": round(float(rq2.loc[0, 'Diversity_Corr_Male']), 4),
            "Female_Rating_Correlation": round(float(rq2.loc[0, 'Diversity_Corr_Female']), 4),
            "Male_Rating_Mean": round(float(rq2.loc[0, 'Male_Avg_Rating']), 1),
            "Female_Rating_Mean": round(float(rq2.loc[0, 'Female_Avg_Rating']), 1),
            "R_Squared": round(float(rq2.loc[0, 'Diversity_Model_R2']), 4),
            "Gender_Coefficient": round(float(rq2.loc[0, 'Diversity_Gender_Coef']), 6),
            "Significant": True,
            "Conclusion": "YES: Strong correlation between rating and opening diversity (r=0.29-0.62). Multi-variable model explains 46.6% of variation"
        },
        
        "Overall_Conclusion": "MIXED EVIDENCE: Strong rating-diversity correlation (skill marker), but NO rating-based strategic adaptation in aggressiveness. Female players show stronger diversity-rating relationship."
    },
    
    "Key_Statistics": {
        "Sample_Bias": {
            "FIDE_Email_Gender": "79.3% male, 20.7% female",
            "Chess_com_Players": "42.5% male, 9.5% female",
            "Lichess_Players": "27.3% male, 3.5% female"
        },
        "Effect_Sizes": {
            "Resignation_Time_Difference": "3.78 plies (not significant)",
            "Aggressiveness_Difference": "7.0 percentage points (not significant)",
            "Female_Rating_Deficit": "72.1 rating points (SIGNIFICANT, p<0.001)",
            "Diversity_Correlation_Gender_Effect": "+0.093 (positive for females)"
        }
    }
}

# Save as JSON
with open('analysis/combined_results_summary.json', 'w') as f:
    json.dump(summary, f, indent=2)

print("Combined Results Summary")
print("=" * 70)
print("\n✓ RQ1 Summary:")
print(f"  Total Games: {summary['RQ1_Findings']['Games_Analyzed']:,}")
print(f"  Male vs Female Games: {summary['RQ1_Findings']['Male_vs_Female_Games']}")
print(f"  Male vs Male Games: {summary['RQ1_Findings']['Male_vs_Male_Games']}")
print(f"\n  Resignation Time Difference: {summary['RQ1_Findings']['Sub_Question_1_1_Resignation_Time']['Difference_Plies']} plies (p={summary['RQ1_Findings']['Sub_Question_1_1_Resignation_Time']['T_test_P_Value']})")
print(f"  Aggressiveness Difference: {summary['RQ1_Findings']['Sub_Question_1_2_Decision_Quality']['Difference_Percentage_Points']}pp (p={summary['RQ1_Findings']['Sub_Question_1_2_Decision_Quality']['Chi2_P_Value']})")
print(f"\n  Conclusion: {summary['RQ1_Findings']['Overall_Conclusion']}")

print("\n✓ RQ2 Summary:")
print(f"  Total Players: {summary['RQ2_Findings']['Players_Analyzed']}")
print(f"  Male vs Female: {summary['RQ2_Findings']['Male_Players']} vs {summary['RQ2_Findings']['Female_Players']}")
print(f"\n  Aggressiveness Model R²: {summary['RQ2_Findings']['Sub_Question_2_1_Aggressive_vs_Rating']['R_Squared']}")
print(f"  Diversity Model R²: {summary['RQ2_Findings']['Sub_Question_2_2_Diversity_Rating']['R_Squared']}")
print(f"\n  Rating-Diversity Correlation: Male r={summary['RQ2_Findings']['Sub_Question_2_2_Diversity_Rating']['Male_Rating_Correlation']}, Female r={summary['RQ2_Findings']['Sub_Question_2_2_Diversity_Rating']['Female_Rating_Correlation']}")
print(f"\n  Conclusion: {summary['RQ2_Findings']['Overall_Conclusion']}")

print("\n✓ File saved: analysis/combined_results_summary.json")
