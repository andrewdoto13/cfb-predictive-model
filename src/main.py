"""
Command-line entry point for the CFB predictive model.

Currently uses the Elo baseline (src/baseline.py). To switch to a different
model, replace the import and adjust the training/prediction pipeline below.
"""

import argparse
import sys
from pathlib import Path

import pandas as pd

from .data_loader import load_processed
from .utils import plot_ratings
from .baseline import EloModel


def run_model(csv_path: Path, k: float = 20.0, home_boost: float = 45.0,
              margin_factor: float = 28.0) -> dict:
    """
    Iterate through the games, updating model ratings.
    Returns a dict {team: final_rating}.
    """
    df = load_processed(csv_path)

    model = EloModel(k=k, home_boost=home_boost, margin_factor=margin_factor)

    for _, row in df.iterrows():
        model.update(
            home_team=row['home_team'],
            away_team=row['away_team'],
            home_score=int(row['home_score']),
            away_score=int(row['away_score']),
        )

    return model.get_ratings()


def parse_args():
    parser = argparse.ArgumentParser(
        description="Run the CFB predictive model on game data."
    )
    parser.add_argument("csv_path", type=Path, help="Path to the processed CSV file.")
    parser.add_argument("--k", type=float, default=20.0, help="Learning rate (default: 20).")
    parser.add_argument("--home_boost", type=float, default=45.0,
                        help="Home-field boost (default: 45).")
    parser.add_argument("--margin_factor", type=float, default=28.0,
                        help="Margin scaling factor (default: 28).")
    return parser.parse_args()


def main():
    args = parse_args()
    try:
        final_ratings = run_model(
            args.csv_path,
            k=args.k,
            home_boost=args.home_boost,
            margin_factor=args.margin_factor,
        )
        print("\n=== Final Ratings ===")
        for team, rating in sorted(final_ratings.items(), key=lambda x: -x[1]):
            print(f"{team:20s} {rating:6.1f}")
        plot_ratings(final_ratings, title="Team Ratings")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
