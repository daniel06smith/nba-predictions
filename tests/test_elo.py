from nba_predictions.data import Game
from nba_predictions.elo import expected_score
from nba_predictions.data import Game
from nba_predictions.elo import predict_games

def test_equal_ratings_is_even():
    assert expected_score(1500, 1500) == 0.5

def test_higher_rating_is_favoured():
    assert expected_score(1600, 1500) > 0.5

def game(game_id, date, home_pts, away_pts, home="AAA", away="BBB"):
    return Game(game_id, date, home, away, home_pts, away_pts)


def test_first_prediction_favours_the_home_team():
    ((_, p),) = predict_games([game("0022500001", "2025-10-21", 100, 90)])
    assert p > 0.5


def test_predictions_never_use_future_results():
    first = game("0022500001", "2025-10-21", 100, 90)
    later_win = game("0022500002", "2025-10-22", 100, 90)
    later_loss = game("0022500002", "2025-10-22", 90, 100)
    p_win = predict_games([first, later_win])[0][1]
    p_loss = predict_games([first, later_loss])[0][1]
    assert p_win == p_loss


def test_winning_raises_the_next_prediction():
    first = game("0022500001", "2025-10-21", 100, 90)
    rematch = game("0022500002", "2025-10-23", 100, 90)
    preds = predict_games([first, rematch])
    assert preds[1][1] > preds[0][1]


def test_new_season_resets_ratings_when_carryover_is_zero():
    s25 = game("0022500001", "2025-10-21", 100, 90)
    s26 = game("0022600001", "2026-10-21", 100, 90)
    first, second = predict_games([s25, s26], carryover=0.0)
    assert first[1] == second[1]

def test_neutral_site_game_has_no_home_edge():
    neutral = Game("0022500147", "2025-11-01", "DAL", "DET", 110, 122, neutral_site=True)
    ((_, p),) = predict_games([neutral])
    assert p == 0.5