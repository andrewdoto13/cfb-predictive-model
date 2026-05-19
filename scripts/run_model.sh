#!/usr/bin/env bash
# Activate the virtual environment and run the model
source /home/andy/college-football-elo-predictor/.venv/bin/activate
python -m src.main "$1"
