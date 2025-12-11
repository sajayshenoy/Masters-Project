import berserk
import os
import sys
from dotenv import load_dotenv

# Force stdout to flush
sys.stdout.reconfigure(line_buffering=True)

load_dotenv()
api_key = os.getenv("lichess_api_key")

if api_key:
    session = berserk.TokenSession(api_key)
    client = berserk.Client(session=session)
    print("Berserk client initialized.")
    print("Attributes of client.users:")
    print(dir(client.users))
else:
    print("No API key found.", flush=True)
