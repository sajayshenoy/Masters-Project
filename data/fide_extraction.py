import pandas as pd
import os

def load_fide_data(file_path):
    """
    Parses the FIDE standard rating list (fixed width format).
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    # Column specifications based on visual inspection
    # ID: 0-15
    # Name: 15-76
    # Fed: 76-80
    # Sex: 80-84
    # Tit: 84-89
    # WTit: 89-94
    # OTit: 94-100 (approx)
    # FOA: 100-106 (approx)
    # Rating: 113-119 (based on 'SEP25' header alignment)
    
    colspecs = [
        (0, 15),    # ID Number
        (15, 76),   # Name
        (76, 80),   # Fed
        (80, 84),   # Sex
        (84, 89),   # Tit
        (89, 94),   # WTit
        (113, 119)  # Rating
    ]
    
    names = ['ID', 'Name', 'Fed', 'Sex', 'Title', 'WTitle', 'Rating']
    
    # Read strict fixed width
    df = pd.read_fwf(file_path, colspecs=colspecs, names=names, header=0, skiprows=1)
    
    # Clean data
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].str.strip()
            
    # Filter for titled players (Title or WTitle is not empty)
    # Note: 'nan' might be present if empty
    df = df.fillna('')
    titled_mask = (df['Title'] != '') | (df['WTitle'] != '')
    titled_players = df[titled_mask].copy()
    
    # Prioritize Title over WTitle if both exist? Or keep both.
    # User said "FIDE will be used as the source of truth".
    # We'll keep both for now, or merge them.
    
    return titled_players

if __name__ == "__main__":
    # Assuming file is in parent directory or current
    # Based on file listing, it is in 'github_repo/Masters-Project/standard_rating_list.txt'
    # This script will be in 'github_repo/Masters-Project/data/'
    
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    fide_file = os.path.join(base_dir, "standard_rating_list.txt")
    
    try:
        df = load_fide_data(fide_file)
        print(f"Extracted {len(df)} titled players from FIDE list.")
        
        output_file = os.path.join(os.path.dirname(__file__), "fide_titled_players.csv")
        df.to_csv(output_file, index=False)
        print(f"Saved to {output_file}")
        
    except Exception as e:
        print(f"Error: {e}")
