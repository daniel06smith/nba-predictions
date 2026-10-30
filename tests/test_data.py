import json
import pytest

from nba_predictions.data import load_games, parse_game_log

HEADERS = ["GAME_ID", "GAME_DATE", "TEAM_ABBREVIATION", "MATCHUP", "PTS", "PLUS_MINUS"]


def make_raw(rows):
    return json.dumps(
        {"resultSets": [{"name": "LeagueGameLog", "headers": HEADERS, "rowSet": rows}]}
    )


def test_pairs_two_team_rows_into_one_game():
    raw = make_raw(
        [
            ["0022500002", "2025-10-21", "LAL", "LAL vs. GSW", 109, -10],
            ["0022500002", "2025-10-21", "GSW", "GSW @ LAL", 119, 10],
        ]
    )
    (game,) = parse_game_log(raw)
    assert (game.home_team, game.away_team) == ("LAL", "GSW")
    assert (game.home_pts, game.away_pts) == (109, 119)
    assert game.home_won is False


def test_games_come_back_in_chronological_order():
    raw = make_raw(
        [
            ["0022500010", "2025-10-23", "BOS", "BOS vs. NYK", 100, 5],
            ["0022500010", "2025-10-23", "NYK", "NYK @ BOS", 95, -5],
            ["0022500002", "2025-10-21", "LAL", "LAL vs. GSW", 109, -10],
            ["0022500002", "2025-10-21", "GSW", "GSW @ LAL", 119, 10],
        ]
    )
    assert [g.game_id for g in parse_game_log(raw)] == ["0022500002", "0022500010"]


def test_rejects_game_with_missing_team_row():
    raw = make_raw([["0022500002", "2025-10-21", "LAL", "LAL vs. GSW", 109, -10]])
    with pytest.raises(ValueError):
        parse_game_log(raw)


def test_rejects_scores_that_disagree_with_plus_minus():
    raw = make_raw(
        [
            ["0022500002", "2025-10-21", "LAL", "LAL vs. GSW", 109, -10],
            ["0022500002", "2025-10-21", "GSW", "GSW @ LAL", 119, 7],
        ]
    )
    with pytest.raises(ValueError):
        parse_game_log(raw)


def test_rejects_preseason_game_ids():
    raw = make_raw(
        [
            ["0012500001", "2025-10-05", "LAL", "LAL vs. GSW", 100, 0],
            ["0012500001", "2025-10-05", "GSW", "GSW @ LAL", 100, 0],
        ]
    )
    with pytest.raises(ValueError):
        parse_game_log(raw)

def test_load_games_uses_the_latest_snapshot(tmp_path):
    season_dir = tmp_path / "season=2025-26"
    season_dir.mkdir()
    one_game = [
        ["0022500002", "2025-10-21", "LAL", "LAL vs. GSW", 109, -10],
        ["0022500002", "2025-10-21", "GSW", "GSW @ LAL", 119, 10],
    ]
    two_games = one_game + [
        ["0022500010", "2025-10-23", "BOS", "BOS vs. NYK", 100, 5],
        ["0022500010", "2025-10-23", "NYK", "NYK @ BOS", 95, -5],
    ]
    (season_dir / "pulled=20261001T000000Z.json").write_text(make_raw(one_game))
    (season_dir / "pulled=20261030T000000Z.json").write_text(make_raw(two_games))
    assert len(load_games(tmp_path)) == 2

def test_neutral_site_game_has_no_home_team():
    raw = make_raw(
        [
            ["0022500147", "2025-11-01", "DET", "DET @ DAL", 122, 12],
            ["0022500147", "2025-11-01", "DAL", "DAL @ DET", 110, -12],
        ]
    )
    (game,) = parse_game_log(raw)
    assert game.neutral_site is True
    assert (game.home_team, game.away_team) == ("DAL", "DET")  # alphabetical slots
    assert (game.home_pts, game.away_pts) == (110, 122)


def test_rejects_game_where_both_rows_claim_home():
    raw = make_raw(
        [
            ["0022500002", "2025-10-21", "LAL", "LAL vs. GSW", 109, -10],
            ["0022500002", "2025-10-21", "GSW", "GSW vs. LAL", 119, 10],
        ]
    )
    with pytest.raises(ValueError):
        parse_game_log(raw)