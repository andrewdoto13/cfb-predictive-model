# CFB Predictive Model — Project Context

## Overview

A Python project for predicting college football game outcomes. Starts with an Elo rating system baseline, designed to be modular so advanced models (logistic regression, gradient boosting, neural networks) can be swapped in easily.

## Directory Structure

```
cfb-predictor/
├── src/
│   ├── __init__.py
│   ├── main.py            # CLI entry point
│   ├── baseline.py        # Elo baseline model
│   ├── data_loader.py     # Data loading & preprocessing
│   └── utils.py           # Shared utilities (plotting, etc.)
├── notebooks/             # Jupyter notebooks for exploration
├── data/
│   ├── raw/               # Unprocessed data (gitignored)
│   └── processed/         # Cleaned, ready-to-use data
├── scripts/
│   └── run_model.sh       # One-command runner
├── tests/                 # Unit and integration tests
├── FEATURES_AND_DATASETS.md  # Data sources & feature guide
├── requirements.txt
└── README.md
```

## Coding Conventions

- **Python 3.11+**, use type hints on all public functions
- **Docstrings**: Google style for all modules, classes, and public functions
- **Imports**: stdlib → third-party → local (`.src`), sorted alphabetically within groups
- **Formatting**: Black-compatible, 88-char line limit
- **Naming**: `snake_case` for functions/variables, `PascalCase` for classes, `UPPER_SNAKE_CASE` for constants
- **Error handling**: Fail fast with clear error messages. Catch specific exceptions, never bare `except`.
- **No magic numbers**: Parameters like `k`, `home_boost`, `margin_factor` belong in config or CLI args, not hardcoded.

## Data Handling Rules

**CRITICAL — No data leakage:**
- Always compute features using data available **before** the game being predicted
- Rolling averages must use only past games (no look-ahead)
- Train/test splits must be temporal, not random (e.g., train on 2020-2023, test on 2024)
- Never use future season data in training

**Data pipeline:**
1. `data/raw/` — raw downloads (gitignored, never committed)
2. `data/processed/` — cleaned, validated CSVs (can be committed if small)
3. `src/data_loader.py` — handles loading and basic preprocessing

## Model Development Phases

| Phase | Model | Target Accuracy | Status |
|-------|-------|----------------|--------|
| 1 | Elo rating (current) | ~60-65% | ✅ Complete |
| 2 | Logistic regression, XGBoost, LightGBM | ~65-70% | 🟡 Planned |
| 3 | Ensemble methods, neural networks | ~70-75% | 🔴 Planned |
| 4 | Meta-modeling, EPA simulation, market-adjusted | ~75-80% | 🔴 Planned |

When adding new models, follow the same interface pattern as `EloModel` in `src/baseline.py`:
- `fit(data)` — train on historical data
- `predict(home, away)` — return prediction for a matchup
- Keep it modular — `src/main.py` should only need to swap the import

## Feature Categories (from FEATURES_AND_DATASETS.md)

- **Basic**: score differential, total points, margin of victory
- **Rating-based**: Elo, SP+, FEI, FPI, Sagarin, DRR
- **Advanced (play-by-play)**: EPA/PPA, success rate, explosiveness, drive efficiency
- **Recruiting**: class ranking, returning production, star count, portal impact
- **Coaching/roster**: experience, coordinator tenure, QB status, injuries
- **Schedule/context**: SOS, rest days, travel, weather, rivalry, bye week
- **Betting market**: spread, over/under, moneyline, line movement
- **Temporal**: rolling EPA, rolling success rate, momentum, week number

## Testing

- Use `pytest` (already in requirements)
- Place tests in `tests/` mirroring `src/` structure
- Test data loading, feature engineering, and model predictions
- Mock external API calls (CFBD, SportsDataverse) — never make live calls in tests
- Aim for >80% coverage on data processing and feature engineering code

## Running the Project

```bash
# Activate venv
source .venv/bin/activate

# Run baseline model
./scripts/run_model.sh path/to/processed/college_football.csv

# Or directly
python -m src.main path/to/processed/college_football.csv

# Run tests
pytest tests/ -v
```

## Data Sources (Recommended)

- **CFBD Free Tier** (https://collegefootballdata.com/) — game results, team stats, EPA/PPA, betting lines
- **SportsDataverse** (`sdv-cfb`) — play-by-play data, box scores, win probability
- Set API keys in `.env` or environment variables, never hardcode

## Git Workflow

- Use feature branches: `feature/add-lightgbm-model`, `feature/epa-features`
- Commit messages: `type: concise description` (e.g., `feat: add rolling EPA features`, `fix: correct train/test temporal split`)
- Types: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`
- Keep `data/raw/` and `data/processed/` in `.gitignore` unless files are intentionally small
