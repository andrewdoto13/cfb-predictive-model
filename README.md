# CFB Predictive Model

A Python project for predicting college football game outcomes. Currently uses an Elo rating system as a baseline, with a modular design that makes it easy to swap in more advanced models (logistic regression, gradient boosting, neural networks, etc.) as development progresses.

## Project Layout

```
cfb-predictive-model/
│
├─ .gitignore
├─ README.md
├─ requirements.txt
├─ src/
│   ├─ __init__.py
│   ├─ baseline.py        # Elo-based baseline model
│   ├─ data_loader.py     # Data loading & preprocessing
│   ├─ utils.py           # Shared utilities (plotting, etc.)
│   └─ main.py            # CLI entry point
├─ notebooks/
│   └─ (exploration & experimentation)
├─ data/
│   ├─ raw/
│   └─ processed/
├─ scripts/
│   └─ run_model.sh
└─ tests/
    └─ (test files)
```

## Setup

```bash
# 1. Create a virtual environment inside the project directory
cd /home/andy/college-football-elo-predictor
python3 -m venv .venv

# 2. Activate the venv
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the model
./scripts/run_model.sh path/to/processed/college_football.csv
```

## Usage

```bash
python -m src.main path/to/processed/college_football.csv
```

The script will:
1. Load the CSV (expects columns: `date`, `home_team`, `away_team`, `home_score`, `away_score`).
2. Train the configured model on the game data.
3. Output predictions and/or team ratings.

## Model Swapping

The project is structured to make it easy to replace the current Elo baseline with other approaches:

- **Current**: Elo rating system with margin-adjusted scoring (`src/baseline.py`)
- **Planned**: Logistic regression, XGBoost, neural networks, etc.

To switch models, update the import in `src/main.py` and adjust the training/prediction pipeline accordingly.

## License

MIT – feel free to adapt and reuse.
