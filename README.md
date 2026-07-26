# A Unified FIDE, Chess.com, and Lichess Database

This repository holds the data pipeline, the unified dataset, and the analysis code for a master's
project that studies behavioral patterns in elite online chess. The main contribution is a single
player database that links official FIDE identities to Chess.com and Lichess accounts, so that
online games can be analyzed against a player's over-the-board identity.

Authors: Ajay Sathish Shenoy, Toni Kristic, Ved Chintamani Bhatawadekar (MSc Informatics,
University of Zurich). Supervisors: Prof. Dr. Anikó Hannák and Prof. Dr. Christoph Stadtfeld.

## What is in the repository

- The scraping and enrichment code for the three sources.
- The unification script that merges them into one player table.
- The derived datasets used in the analysis (player table and the RQ1/RQ2 tables).
- The analysis scripts and the figures they produce.

The raw Lichess game archive is not stored here. It comes from the publicly available Lichess
Elite Database (2013 to 2020), which anyone can download to reproduce the extraction.

## How the database is built

The three sources do not share a common key, so the pipeline links them in stages.

FIDE is the source of truth for identity, title, gender, and official rating. We parse the monthly
FIDE Standard Rating List, a fixed-width text file that lists every rated player, and keep the
titled players. This gives `data/fide_titled_players.csv` (23,366 titled players in the September
2025 list).

Chess.com is read through its public titled-player endpoint (`/pub/titled/{title}`), iterated over
every title code. This gives `data/chesscom_titled_players.csv` (15,446 accounts). Each account is
then enriched with the profile and stats endpoints for real name, country, and ratings; 15,423 of
them returned a profile.

Lichess has no single titled-player endpoint, so we combine members of the titled-arena and
related teams, the top 200 of every leaderboard, and the participants of the historic Titled Arena
tournaments from 2018 to 2024. The last list is the one that surfaces active titled players. This
gives `data/lichess_titled_players.csv` (5,429 accounts), of which 4,746 could be enriched in bulk
through the users endpoint.

The three lists are merged in `data/unify_datasets.py`. Names are normalized from the FIDE
"Last, First" form to a lowercase "first last" form. FIDE is the base layer, anchored on the FIDE
ID. Chess.com and Lichess accounts are matched to FIDE on the normalized name, with title and
federation used to separate near-collisions, and weaker signals (name similarity, federation,
rating overlap) used only to break ties. Platform-titled players who match no FIDE record, for
example National Masters, are added as new rows rather than dropped. The result is
`data/unified_chess_players.csv` with 33,713 unique players.

Gender is confirmed from the FIDE sex field where present. For players without a FIDE label, it is
inferred from the first name with the `gender-guesser` library, and the result is stored in
`data/unified_chess_players_with_inferred_gender.csv`. Every player carries one of five labels:
confirmed male, confirmed female, perceived male, perceived female, or unknown.

## Analysis

The project answers two research questions.

RQ1 asks whether players behave differently against female opponents, measured through game length
(a proxy for effort and resignation timing) and opening aggressiveness. RQ2 asks what drives a
player's opening repertoire: rating, activity, or gender, measured through aggressiveness and
Shannon-entropy diversity. Both questions are answered with multiple linear regression, fitted
with scikit-learn and reproduced in statsmodels for the standard errors, p-values, and diagnostics.

## Reproducing the results

Run the scripts in this order from the repository root:

- `data/unify_datasets.py` builds the unified player table.
- `analysis/05_comprehensive_lichess_extraction.py` extracts and labels the games.
- `analysis/06_rq1_expanded_analysis.py` runs the RQ1 analysis and figures.
- `analysis/02_rq2_opening_repertoire_analysis.py` runs the RQ2 correlations and regressions.
- `analysis/07_comprehensive_statistics_report.py` collects the statistics.
- `analysis/08_rq1_reviewer_variables.py` runs the extended RQ1 model (female-win, lower-rated
  winner, and square-root rating-difference terms).

The report figures are produced by `figures/make_figures.py`.

## Data availability and citation

The working copy of the code and the derived datasets is this GitHub repository. An archived,
citable snapshot is deposited on Zenodo, which mints a DOI and keeps a stable, non-proprietary
copy for other researchers to replicate and extend. See `CITATION.cff` for how to cite the
dataset, and `.zenodo.json` for the archive metadata.

## License

The code and derived datasets in this repository are released under the MIT License (see
`LICENSE`). The raw Lichess game data is subject to the terms of the Lichess Elite Database.
