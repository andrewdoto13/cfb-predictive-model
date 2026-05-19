# College Football Elo Predictor

A simple Python project that implements an Elo rating system for NCAA college football teams.
It includes:

- Core Elo calculation utilities (`src/elo.py`)
- Data loading helpers (`src/data_loader.py`)
- Utility functions (`src/utils.py`)
- A CLI entry point (`src/main.py`) to run the model on a CSV file
- Jupyter notebooks for exploration and experimentation (`notebooks/`)

## Project Layout
```
college-football-elo-predictor/
│
├─ .gitignore
├─ README.md
├─ requirements.txt
├─ src/
│   ├─ __init__.py
│   ├─ elo.py
│   ├─ data_loader.py
│   ├─ utils.py
│   └─ main.py
├─ notebooks/
│   ├─ 01_exploratory_analysis.ipynb
│   ├─ 02_elo_baseline.ipynb
│   └─ 03_margin_adjusted.ipynb
├─ data/
│   ├─ raw/
│   └─ processed/
├─ scripts/
│   ├─ download_kaggle_dataset.sh
│   └─ run_model.sh
└─ tests/
    ├─ test_elo.py
    └─ test_utils.py
```

## Setup

```bash
# 1️⃣ Clone / copy this repo
git clone <repo‑url> /home/andy/college-football-elo-predictor   # or just copy the folder

# 2️⃣ Create a virtual environment inside the project directory
cd /home/andy/college-football-elo-predictor
python3 -m venv .venv

# 3️⃣ Activate the venv
source .venv/bin/activate

# 4️⃣ Install dependencies
pip install -r requirements.txt

# 5️⃣ (Optional) Download a sample dataset
./scripts/download_kaggle_dataset.sh   # requires Kaggle API token

# 6️⃣ Run the model
./scripts/run_model.sh
```

## Usage

```bash
python -m src.main path/to/processed/college_football.csv
```

The script will:
1. Load the CSV (expects columns: `date`, `home_team`, `away_team`, `home_score`, `away_score`).
2. Initialise each team’s rating (default 1500).
3. Iterate through games in chronological order.
4. Update ratings using the Elo formula (margin‑adjusted if you enable the flag in `src/utils.py`).
5. Output the final ratings and optionally plot the rating trajectories.

## License

MIT – feel free to adapt and reuse.
