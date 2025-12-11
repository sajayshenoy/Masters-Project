import requests
import json

def inspect_user():
    # Check RebeccaHarris (Daniel Naroditsky)
    users = ['RebeccaHarris', 'alireza2003']
    
    print("--- Individual GET ---")
    for u in users:
        url = f"https://lichess.org/api/user/{u}"
        resp = requests.get(url)
        if resp.status_code == 200:
            data = resp.json()
            profile = data.get('profile', {})
            print(f"User: {u}, Profile: {profile}")
        else:
            print(f"Error {u}: {resp.status_code}")

    print("\n--- Bulk POST ---")
    url_bulk = "https://lichess.org/api/users"
    resp = requests.post(url_bulk, data=','.join(users))
    if resp.status_code == 200:
        data = resp.json()
        for u in data:
             print(f"Bulk User: {u.get('username')}, Profile: {u.get('profile', {})}")

if __name__ == "__main__":
    inspect_user()
