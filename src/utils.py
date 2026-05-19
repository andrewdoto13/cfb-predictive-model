"""
Utility helpers used across the project.
"""

from .elo import actual_score_from_margin
import matplotlib.pyplot as plt

def home_field_boost(base_rating: float, boost: float = 45.0) -> float:
    """
    Return the home team rating with a home‑field advantage added.
    """
    return base_rating + boost

def plot_ratings(ratings: dict[str, float], title: str = "Team Ratings"):
    """
    Simple line plot of team ratings.
    `ratings` is a dict mapping team name → rating.
    """
    teams = list(ratings.keys())
    vals = [ratings[t] for t in teams]
    plt.figure(figsize=(10, 6))
    plt.plot(teams, vals, marker='o')
    plt.title(title)
    plt.xlabel("Team")
    plt.ylabel("Rating")
    plt.grid(True)
    plt.tight_layout()
    plt.show()
