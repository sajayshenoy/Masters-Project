import requests
import pandas as pd
import os
import time

def get_chesscom_titled_players():
    titles = ["GM", "WGM", "IM", "WIM", "FM", "WFM", "CM", "WCM", "NM"] 
    all_users = []
    
    headers = {
        'User-Agent': 'ChessResearchProject/1.0 (sajay@example.com)' # Good practice for Chess.com API
    }
    
    for title in titles:
        url = f"https://api.chess.com/pub/titled/{title}"
        print(f"Fetching {title} from Chess.com...", flush=True)
        try:
            resp = requests.get(url, headers=headers, timeout=30)
            if resp.status_code == 200:
                data = resp.json()
                players = data.get('players', [])
                print(f"  - Found {len(players)} {title} players", flush=True)
                for username in players:
                    all_users.append({'username': username, 'title': title})
            else:
                print(f"Failed to fetch {title}: {resp.status_code}")
                
            time.sleep(1) 
            
        except Exception as e:
            print(f"Error fetching {title}: {e}")
            
    return pd.DataFrame(all_users)

if __name__ == "__main__":
    df = get_chesscom_titled_players()
    if not df.empty:
        print(f"Extracted {len(df)} titled players from Chess.com.")
        output_file = os.path.join(os.path.dirname(__file__), "chesscom_titled_players.csv")
        df.to_csv(output_file, index=False)
        print(f"Saved to {output_file}")
    else:
        print("No players found or error occurred.")
