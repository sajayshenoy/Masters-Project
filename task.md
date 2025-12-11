# Task Checklist

## Phase 1: Data Extraction
- [ ] Analyze existing notebooks and API keys <!-- id: 0 -->
- [x] **FIDE Data Extraction** <!-- id: 1 -->
    - [x] Extract titled players list (Count: ~23k) <!-- id: 2 -->
    - [x] Extract player details (ratings, gender, etc.) <!-- id: 3 -->
    - [x] Save to CSV <!-- id: 4 -->
- [x] **Lichess Data Extraction** <!-- id: 5 -->
    - [x] Setup Lichess API client <!-- id: 6 -->
    - [x] Fetch titled players (Count: 5429) <!-- id: 7 -->
    - [x] Save basic list to CSV <!-- id: 9 -->

## Phase 2: Data Enrichment
- [x] **Lichess Enrichment** <!-- id: 15 -->
    - [x] Fetch full user profiles (Bulk API) <!-- id: 16 -->
    - [x] Extract ratings (Bullet, Blitz, Rapid, Classical) <!-- id: 17 -->
    - [x] Extract metadata (Name, Bio, Country) <!-- id: 18 -->
- [x] **Chess.com Enrichment** <!-- id: 19 -->
    - [x] Fetch user profiles (Name, Country, FIDE ID) <!-- id: 20 -->
    - [x] Fetch user stats (Ratings) <!-- id: 21 -->
- [x] **FIDE Enrichment** (Existing list is sufficient) <!-- id: 22 -->

## Phase 3: Data Unification
- [x] Inspect and normalize data formats <!-- id: 23 -->
- [x] Merge datasets by Name/FIDE ID <!-- id: 24 -->
- [x] Handle duplicates and name variations <!-- id: 25 -->
- [x] Create final unified CSV (Count: 33,713) <!-- id: 26 -->

## Phase 4: Analysis
- [x] Implement RQ1 analysis (Gender differences) <!-- id: 27 -->
- [ ] Implement RQ2 analysis (Opening repertoire) <!-- id: 28 -->
- [ ] Create visualizations and report <!-- id: 29 -->
