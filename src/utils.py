"""
Shared utility helpers used across the project.
"""

import matplotlib.pyplot as plt


def plot_ratings(ratings: dict, title: str = "Team Ratings") -> None:
    """
    Simple line plot of team ratings.
    `ratings` is a dict mapping team name -> rating.
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
