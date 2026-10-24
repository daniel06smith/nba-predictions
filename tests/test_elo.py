from nba_predictions.elo import expected_score

def test_equal_ratings_is_even():
    assert expected_score(1500, 1500) == 0.5

def test_higher_rating_is_favoured():
    assert expected_score(1600, 1500) > 0.5