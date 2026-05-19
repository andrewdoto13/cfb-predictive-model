"""
Baseline Elo rating model for college football.

This module implements an Elo-based rating system as a simple, interpretable
baseline. It can be replaced with more advanced models (logistic regression,
gradient boosting, neural networks, etc.) in src/models.py or similar.
"""

from __future__ import annotations
import math
from typing import Dict, Tuple


def expected_score(rating_a: float, rating_b: float, home_boost: float = 0.0) -> float:
    """
    Compute the expected score for team A against team B.
    Implements the classic Elo formula with a 400-point scaling factor.
    Optionally adds a home-field boost to rating_a.
    """
    exponent = (rating_b - rating_a + home_boost) / 400.0
    return 1.0 / (1.0 + 10 ** exponent)


def actual_score_from_margin(home_points: int, away_points: int, margin_factor: float = 28.0) -> float:
    """
    Convert the point margin into a score S in the range (0, 1).

    * Home win  -> S = sigmoid(margin / margin_factor)
    * Home loss -> S = 1 - sigmoid(|margin| / margin_factor)
    * Tie       -> S = 0.5

    The sigmoid shape lets larger margins contribute more strongly.
    """
    margin = home_points - away_points
    if margin > 0:  # home win
        s = 1.0 / (1.0 + 10 ** (-margin / margin_factor))
    elif margin < 0:  # home loss
        s = 1.0 / (1.0 + 10 ** (margin / margin_factor))
    else:  # tie
        s = 0.5
    return s


def update_rating(rating_a: float, rating_b: float, s_a: float,
                  k: float = 20.0, home_boost: float = 0.0) -> Tuple[float, float]:
    """
    Return the updated rating for team A and the expected score E_a.
    s_a – actual score for team A (0-1)
    k   – learning rate (default 20)
    home_boost – optional home-field advantage added to rating_a
    """
    e_a = expected_score(rating_a, rating_b, home_boost)
    new_rating = rating_a + k * (s_a - e_a)
    return new_rating, e_a


def compute_home_boost(home_rating: float, boost: float = 45.0) -> float:
    """Return the home team rating with a home-field advantage added."""
    return home_rating + boost


class EloModel:
    """
    Simple Elo rating model for college football.

    This can serve as a baseline that is later replaced by more advanced
    models. The interface is designed to be swappable.
    """

    def __init__(self, k: float = 20.0, home_boost: float = 45.0,
                 margin_factor: float = 28.0, initial_rating: float = 1500.0):
        self.k = k
        self.home_boost = home_boost
        self.margin_factor = margin_factor
        self.initial_rating = initial_rating
        self.ratings: Dict[str, float] = {}

    def _ensure_team(self, team: str) -> None:
        if team not in self.ratings:
            self.ratings[team] = self.initial_rating

    def predict(self, home_team: str, away_team: str) -> float:
        """Return the predicted probability that home_team wins."""
        self._ensure_team(home_team)
        self._ensure_team(away_team)
        home_adj = self.compute_home_boost(self.ratings[home_team])
        return expected_score(home_adj, self.ratings[away_team])

    def update(self, home_team: str, away_team: str,
               home_score: int, away_score: int) -> None:
        """Update ratings after a game."""
        self._ensure_team(home_team)
        self._ensure_team(away_team)

        s_home = actual_score_from_margin(home_score, away_score, self.margin_factor)
        home_adj = self.compute_home_boost(self.ratings[home_team])

        new_home, _ = update_rating(self.ratings[home_team], self.ratings[away_team],
                                    s_home, k=self.k, home_boost=0.0)
        new_away, _ = update_rating(self.ratings[away_team], self.ratings[home_team],
                                    1.0 - s_home, k=self.k, home_boost=0.0)

        self.ratings[home_team] = new_home
        self.ratings[away_team] = new_away

    def get_ratings(self) -> Dict[str, float]:
        return dict(self.ratings)
