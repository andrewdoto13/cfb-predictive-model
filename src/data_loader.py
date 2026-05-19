"""
Data loading utilities.
"""

import pandas as pd
from pathlib import Path

def load_processed(csv_path: str | Path) -> pd.DataFrame:
    """
    Load a processed CSV file containing college football game data.
    Expected columns (at minimum):
        - date (parseable)
        - home_team
        - away_team
        - home_score
        - away_score
    The function parses dates, sorts by date, and returns a DataFrame.
    """
    path = Path(csv_path)
    df = pd.read_csv(path)
    # Ensure correct dtypes
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date').reset_index(drop=True)
    return df
