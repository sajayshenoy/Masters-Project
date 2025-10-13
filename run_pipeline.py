# src/run_pipeline.py
"""
Top-level pipeline runner (Step 0 stub).
Later steps will populate this script to call FIDE loader,
enrichment, linking, entity-resolution, analytics, and tests.
"""

import argparse
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[1]

def main(args):
    logger.info("Pipeline stub. Repo root: %s", ROOT)
    logger.info("Use individual scripts in src/ for each pipeline step (populated in later steps).")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=0, help="sample run limit (used in later steps)")
    args = parser.parse_args()
    main(args)
