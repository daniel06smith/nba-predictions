INITIAL_RATING = 1500.0


def expected_score(rating_a: float, rating_b: float) -> float:
    """Probability that team A beats team B under the Elo model."""
    return 1 / (1 + 10 ** ((rating_b - rating_a) / 400))


def predict_games(games, k=20.0, home_advantage=100.0, carryover=0.75):
    """Walk through games in date order, predicting each one BEFORE updating.

    Returns a list of (game, home_win_probability). At each new season,
    ratings are pulled part of the way back toward the mean (carryover=1.0
    keeps them, 0.0 resets them). Neutral-site games get no home bonus.
    """
    ratings = {}
    predictions = []
    current_season = None
    for game in games:
        if game.season != current_season:
            if current_season is not None:
                ratings = {
                    t: INITIAL_RATING + carryover * (r - INITIAL_RATING)
                    for t, r in ratings.items()
                }
            current_season = game.season
        home = ratings.get(game.home_team, INITIAL_RATING)
        away = ratings.get(game.away_team, INITIAL_RATING)
        bonus = 0.0 if game.neutral_site else home_advantage
        p_home = expected_score(home + bonus, away)
        predictions.append((game, p_home))

        delta = k * ((1.0 if game.home_won else 0.0) - p_home)
        ratings[game.home_team] = home + delta
        ratings[game.away_team] = away - delta
    return predictions