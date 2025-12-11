import pandas as pd
import requests
import time
import os
from dotenv import load_dotenv

# Try to load .env from current or parent directories
env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(env_path)
API_KEY = os.getenv("lichess_api_key")
# Also try default if not found
if not API_KEY:
    load_dotenv()
    API_KEY = os.getenv("lichess_api_key")

def get_lichess_titled_players():
    titles = ["GM", "WGM", "IM", "WIM", "FM", "WFM", "CM", "WCM", "NM"]
    all_users = []
    
    headers = {'Accept': 'application/json'}
    if API_KEY:
        headers["Authorization"] = f"Bearer {API_KEY}"
        print(f"Using Lichess API Key: {API_KEY[:4]}...", flush=True)
    else:
        print("No Lichess API Key found in environment, running anonymously", flush=True)

    for title in titles:
        print(f"Fetching {title} from Lichess...", flush=True)
        # Note: The endpoint /api/user/titled/{title} might not exist or requires specific handling.
        # Checking logic during execution.
        url = f"https://lichess.org/api/user/titled/{title}"
        try:
            resp = requests.get(url, headers=headers, timeout=60)
            if resp.status_code == 200:
                users = resp.json()
                print(f"  - Found {len(users)} {title} players", flush=True)
                for user in users:
                    if isinstance(user, dict):
                         user_data = {
                             'id': user.get('id'),
                             'username': user.get('username'),
                             'title': user.get('title', title),
                             'online': user.get('online'),
                             'patron': user.get('patron'),
                             'perfs': user.get('perfs') 
                         }
                         all_users.append(user_data)
                    else:
                        all_users.append({'username': str(user), 'title': title})
            else:
                print(f"  - Failed to fetch {title}: {resp.status_code} - {resp.text}", flush=True)
        except Exception as e:
            print(f"  - Error fetching {title}: {e}", flush=True)
        
        time.sleep(1) 
    
    return pd.DataFrame(all_users)

if __name__ == "__main__":
    df = get_lichess_titled_players()
    # Save to data directory
    output_file = os.path.join("data", "lichess_titled_players.csv")
    df.to_csv(output_file, index=False)
    print(f"Saved to {output_file}", flush=True)
