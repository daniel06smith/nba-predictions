import math
import pytest
from nba_predictions.metrics import accuracy, brier_score, log_loss


def test_log_loss_of_a_coin_flip():
    assert log_loss([1, 0], [0.5, 0.5]) == pytest.approx(math.log(2))


def test_brier_score_of_perfect_and_worst_predictions():
    assert brier_score([1, 0], [1.0, 0.0]) == 0
    assert brier_score([1, 0], [0.0, 1.0]) == 1


def test_accuracy():
    assert accuracy([1, 0, 1], [0.9, 0.2, 0.4]) == pytest.approx(2 / 3)