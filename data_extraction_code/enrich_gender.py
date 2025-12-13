import pandas as pd
import gender_guesser.detector as gender
import os

def infer_gender():
    # --- PATH FIX ---
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    data_dir = os.path.join(project_root, "data")
    input_file = os.path.join(data_dir, "unified_chess_players.csv")
    # ----------------

    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found.")
        return

    print(f"Loading data from {input_file}...")
    df = pd.read_csv(input_file)
    
    d = gender.Detector()
    
    def predict_sex(name):
        if not isinstance(name, str): return None
        # Extract first name (assuming "First Last" format)
        first_name = name.split()[0]
        guess = d.get_gender(first_name)
        
        if guess in ['male', 'mostly_male']: return 'M'
        if guess in ['female', 'mostly_female']: return 'F'
        return None

    # Apply only to rows where sex is missing
    mask_missing = df['sex'].isna()
    print(f"Inferring gender for {mask_missing.sum()} players...")
    
    # Create column if not exists
    if 'sex_inferred' not in df.columns:
        df['sex_inferred'] = None

    df.loc[mask_missing, 'sex_inferred'] = df.loc[mask_missing, 'name'].apply(predict_sex)
    
    # Merge into main sex column for analysis (optional, or keep separate)
    # For now, we keep separate to distinguish source
    
    print("Inference Counts:")
    print(df['sex_inferred'].value_counts())
    
    df.to_csv(input_file, index=False)
    print("Updated unified dataset with inferred gender.")

if __name__ == "__main__":
    infer_gender()