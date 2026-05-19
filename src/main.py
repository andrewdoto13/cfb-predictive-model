"""
Command‑line entry point for the Elo predictor.
"""

import argparse
import sys
from pathlib import Path

import pandas as pd

from .data_loader import load_processed
from .utils import plot_ratings
from .elo import update_rating, actual_score_from_margin

def run_elo(csv_path: Path, k: float = 20.0, home_boost: float = 45.0, margin_factor: float = 28.0):
    """
    Iterate through the games, updating Elo ratings.
    Returns a dict {team: final_rating}.
    """
    df = load_processed(csv_path)

    # Initialise ratings dictionary
    ratings = {}

    for _, row in df.iterrows():
        home = row['home_team']
        away = row['away_team']

        # Ensure both teams have an entry in ratings
        if home not in ratings:
            ratings[home] = 1500.0
        if away not in ratings:
            ratings[away] = 1500.0

        # Compute actual score using margin
        s_home = actual_score_from_margin(row['home_score'], row['away_score'], margin_factor)

        # Optionally add home boost before computing expected score
        home_adj = home_field_boost(ratings[home], home_boost)

        # Update ratings
        new_home, _ = update_rating(ratings[home], ratings[away], s_home,
                                    k=k, home_boost=0.0)  # home_boost already applied to rating
        new_away, _ = update_rating(ratings[away], ratings[home], 1.0 - s_home,
                                    k=k, home_boost=0.0)

        ratings[home] = new_home
        ratings[away] = new_away

    return ratings

def parse_args():
    parser = argparse.ArgumentParser(description="Run Elo rating update on a college football CSV.")
    parser.add_argument("csv_path", type=Path, help="Path to the processed CSV file.")
    parser.add_argument("--k", type=float, default=20.0, help="Learning rate K (default: 20).")
    parser.add_argument("--home_boost", type=float, default=45.0, help="Home‑field boost (default: 45).")
    parser.add_argument("--margin_factor", type=float, default=28.0, help="Margin scaling factor (default: 28).")
    return parser.parse_args()

def main():
    args = parse_args()
    try:
        final_ratings = run_elo(args.csv_path, k=args.k, home_boost=args.home_boost, margin_factor=args.margin_factor)
        print("\n=== Final Elo Ratings ===")
        for team, rating in sorted(final_ratings.items(), key=lambda x: -x[1]):
            print(f"{team:20s} {rating:6.1f}")
        # Optional: plot the ratings
        plot_ratings(final_ratings, title="Final College Football Elo Ratings")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
