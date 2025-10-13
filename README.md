# Chess Pipeline (prototype)

This repository contains a reproducible pipeline prototype to build a unified chess player + tournament database from:
- FIDE tournament exports (via `fideparser`)
- ChessTools Ratings API (api.chesstools.org)
- Lichess public API

## Step 0 — Setup
- Repo structure created.
- `sql/schema.sql` contains the SQLite schema.
- `sql/migration_postgres.sql` contains Postgres migration SQL.
- `requirements.txt` lists Python dependencies.

## Quickstart (local)
1. Create a venv and install:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
