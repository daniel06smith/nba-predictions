"""Probe: which NBA data hosts can this machine reach?"""
import sys
import time

from nba_api.live.nba.endpoints import scoreboard as live_scoreboard
from nba_api.stats.endpoints import leaguegamelog, scoreboardv3


def probe(name, fn):
    start = time.time()
    try:
        summary = fn()
        print(f"OK   {name}: {summary} ({time.time() - start:.1f}s)")
        return True
    except Exception as exc:  # fail loudly with the real cause
        print(f"FAIL {name}: {type(exc).__name__}: {exc} ({time.time() - start:.1f}s)")
        return False


def gamelog(season):
    df = leaguegamelog.LeagueGameLog(season=season, timeout=30).get_data_frames()[0]
    return f"{len(df)} rows"


def scoreboard_v3(date):
    df = scoreboardv3.ScoreboardV3(game_date=date, timeout=30).game_header.get_data_frame()
    return f"{len(df)} games on {date}"


def live_games():
    data = live_scoreboard.ScoreBoard(timeout=30).get_dict()
    return f"{len(data['scoreboard']['games'])} games today"


results = [
    probe("stats  LeagueGameLog 2026-27", lambda: gamelog("2026-27")),
    probe("stats  LeagueGameLog 2025-26", lambda: gamelog("2025-26")),
    probe("stats  ScoreboardV3", lambda: scoreboard_v3("2026-10-22")),
    probe("cdn    live ScoreBoard", live_games),
]
sys.exit(0 if all(results) else 1)