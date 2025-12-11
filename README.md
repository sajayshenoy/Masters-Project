# Data Pipeline Walkthrough

This document summarizes the process of extracting, enriching, and unifying titled player data from FIDE, Chess.com, and Lichess.

## 1. Data Extraction

### FIDE
- **Source:** FIDE Standard Rating List (Text File)
- **Method:** Parsed fixed-width text file.
- **Output:** `data/fide_titled_players.csv` (~23k records)

### Chess.com
- **Source:** Chess.com API (`/pub/titled/{title}`)
- **Method:** Iterated through all titles (GM, IM, etc.) to fetch usernames.
- **Output:** `data/chesscom_titled_players.csv` (~15k records)

### Lichess
- **Source:** Lichess API (Teams + Leaderboards + Titled Arenas)
- **Method:** 
    - Scraped members of 'titled-arena' and other teams.
    - Scraped top 200 from all leaderboards.
    - **Crucial Step:** Scraped participants from historic Titled Arena tournaments (2018-2024) to find active titled players.
- **Output:** `data/lichess_titled_players.csv` (~5.4k active titled players)

## 2. Data Enrichment

### Lichess
- **Script:** `data/enrich_lichess_data.py`
- **Logic:** Bulk fetched profiles (`POST /api/users`) to retrieve `realName`, `country`, and ratings.
- **Outcome:** 4,746 enriched profiles.

### Chess.com
- **Script:** `data/enrich_chesscom_data.py`
- **Logic:** Fetched `profile` and `stats` endpoints for each user (threaded).
- **Outcome:** 15,423 enriched profiles.

## 3. Data Unification

- **Script:** `data/unify_datasets.py`
- **Logic:**
    1. **Normalize Names:** Converted "Last, First" (FIDE) to "first last" (lowercase).
    2. **Base Layer:** Loaded FIDE players as the primary dataset.
    3. **Matching:** Matched Chess.com and Lichess players to FIDE records via normalized name.
    4. **Additions:** Added non-FIDE matched players (e.g. National Masters on platforms) as new rows.
- **Result:** `data/unified_chess_players.csv` containing **33,713 unique players**.

## Next Steps
- Analyze the unified dataset to answer Research Questions (Gender differences, Platform participation, etc.).
