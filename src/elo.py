"""
Core Elo rating utilities.
"""

from __future__ import annotations
import math

def expected_score(rating_a: float, rating_b: float, home_boost: float = 0.0) -> float:
    """
    Compute the expected score for team A against team B.
    Implements the classic Elo formula with a 400-point scaling factor.
    Optionally adds a home‑field boost to rating_a.
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
        s = 1.0 / (1.0 + 10 ** (margin / margin_factor))  # negative exponent makes s small
    else:  # tie (rare in college football)
        s = 0.5
    return s


def update_rating(rating_a: float, rating_b: float, s_a: float,
                  k: float = 20.0, home_boost: float = 0.0) -> tuple[float, float]:
    """
    Return the updated rating for team A and the expected score E_a.
    s_a – actual score for team A (0‑1)
    k   – learning rate (default 20)
    home_boost – optional home‑field advantage added to rating_a before computing E_a
    """
    e_a = expected_score(rating_a, rating_b, home_boost)
    new_rating = rating_a + k * (s_a - e_a)
    return new_rating, e_a
