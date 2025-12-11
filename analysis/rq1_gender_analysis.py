import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

def analyze_gender_differences():
    # Load Data
    input_file = os.path.join("data", "unified_chess_players.csv")
    if not os.path.exists(input_file):
        print("Dataset not found!")
        return

    df = pd.read_csv(input_file)
    print(f"Loaded {len(df)} players.")

    # Filter for players with known Sex (FIDE data)
    # FIDE uses 'M' and 'F'
    df_gender = df[df['sex'].isin(['M', 'F'])].copy()
    print(f"Players with known gender: {len(df_gender)}")
    
    # 1. Participation Rates
    total_m = len(df_gender[df_gender['sex'] == 'M'])
    total_f = len(df_gender[df_gender['sex'] == 'F'])
    
    # Check platform presence (if username is not null)
    m_on_chesscom = len(df_gender[(df_gender['sex'] == 'M') & (df_gender['chesscom_username'].notna())])
    f_on_chesscom = len(df_gender[(df_gender['sex'] == 'F') & (df_gender['chesscom_username'].notna())])
    
    m_on_lichess = len(df_gender[(df_gender['sex'] == 'M') & (df_gender['lichess_username'].notna())])
    f_on_lichess = len(df_gender[(df_gender['sex'] == 'F') & (df_gender['lichess_username'].notna())])

    print("\n--- Participation Statistics ---")
    print(f"Total Men: {total_m}")
    print(f"Total Women: {total_f}")
    if total_m > 0:
        print(f"Men on Chess.com: {m_on_chesscom} ({m_on_chesscom/total_m*100:.1f}%)")
        print(f"Men on Lichess: {m_on_lichess} ({m_on_lichess/total_m*100:.1f}%)")
    if total_f > 0:
        print(f"Women on Chess.com: {f_on_chesscom} ({f_on_chesscom/total_f*100:.1f}%)")
        print(f"Women on Lichess: {f_on_lichess} ({f_on_lichess/total_f*100:.1f}%)")
    
    # 2. Rating Analysis (Blitz vs FIDE)
    # Ensure ratings are numeric
    cols = ['rating_fide', 'chesscom_rating_blitz', 'lichess_rating_blitz']
    for c in cols:
        df_gender[c] = pd.to_numeric(df_gender[c], errors='coerce')
    
    # Plotting
    plots_dir = os.path.join("analysis", "plots")
    os.makedirs(plots_dir, exist_ok=True)
    
    # A. Boxplot of FIDE Ratings by Gender
    plt.figure(figsize=(8, 6))
    sns.boxplot(x='sex', y='rating_fide', data=df_gender)
    plt.title("FIDE Rating Distribution by Gender")
    plt.savefig(os.path.join(plots_dir, "fide_rating_dist.png"))
    plt.close()
    
    # B. Chess.com Blitz Distribution
    plt.figure(figsize=(8, 6))
    cc_data = df_gender.dropna(subset=['chesscom_rating_blitz'])
    if not cc_data.empty:
        sns.boxplot(x='sex', y='chesscom_rating_blitz', data=cc_data)
        plt.title("Chess.com Blitz Rating Distribution by Gender")
        plt.savefig(os.path.join(plots_dir, "chesscom_blitz_dist.png"))
        plt.close()

    # C. Lichess Blitz Distribution
    plt.figure(figsize=(8, 6))
    li_data = df_gender.dropna(subset=['lichess_rating_blitz'])
    if not li_data.empty:
        sns.boxplot(x='sex', y='lichess_rating_blitz', data=li_data)
        plt.title("Lichess Blitz Rating Distribution by Gender")
        plt.savefig(os.path.join(plots_dir, "lichess_blitz_dist.png"))
        plt.close()
    
    print(f"\nPlots saved to {plots_dir}")
    
    # 3. Correlation Stats
    print("\n--- Correlation (FIDE vs Online Blitz) ---")
    for sex in ['M', 'F']:
        sub = df_gender[df_gender['sex'] == sex]
        
        corr_cc = sub['rating_fide'].corr(sub['chesscom_rating_blitz'])
        corr_li = sub['rating_fide'].corr(sub['lichess_rating_blitz'])
        
        print(f"Gender {sex}:")
        print(f"  Corr FIDE vs Chess.com Blitz: {corr_cc:.3f} (n={sub[['rating_fide', 'chesscom_rating_blitz']].dropna().shape[0]})")
        print(f"  Corr FIDE vs Lichess Blitz:   {corr_li:.3f} (n={sub[['rating_fide', 'lichess_rating_blitz']].dropna().shape[0]})")

if __name__ == "__main__":
    analyze_gender_differences()
