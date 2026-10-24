def expected_score(rating_a: float, rating_b: float) -> float:
    """Probability that team A beats team B under the Elo model."""
    return 1 / (1 + 10 ** ((rating_b - rating_a) / 400))