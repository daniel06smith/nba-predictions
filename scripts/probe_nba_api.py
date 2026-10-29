"""Probe: which NBA data hosts can this machine reach?"""
import sys
import time

from nba_api.live.nba.endpoints import boxscore as live_boxscore
from nba_api.stats.endpoints import scheduleleaguev2
from nba_api.live.nba.endpoints import scoreboard as live_scoreboard
from nba_api.stats.endpoints import leaguegamelog, scoreboardv3
from nba_api.live.nba.endpoints import boxscore as live_boxscore
from nba_api.stats.endpoints import scheduleleaguev2


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


def schedule(season):
    df = scheduleleaguev2.ScheduleLeagueV2(season=season, timeout=30).season_games.get_data_frame()
    print("     schedule columns:", df.columns.tolist())
    return f"{len(df)} rows"


def live_boxscore_first():
    games = live_scoreboard.ScoreBoard(timeout=30).get_dict()["scoreboard"]["games"]
    gid = games[0]["gameId"]
    data = live_boxscore.BoxScore(game_id=gid, timeout=30).get_dict()
    return f"game {gid}, status: {data['game']['gameStatusText']}"

def schedule(season):
    df = scheduleleaguev2.ScheduleLeagueV2(season=season, timeout=30).season_games.get_data_frame()
    print("     schedule columns:", df.columns.tolist())
    return f"{len(df)} rows"


def live_boxscore_first():
    games = live_scoreboard.ScoreBoard(timeout=30).get_dict()["scoreboard"]["games"]
    gid = games[0]["gameId"]
    data = live_boxscore.BoxScore(game_id=gid, timeout=30).get_dict()
    return f"game {gid}, status: {data['game']['gameStatusText']}"

results = [
    probe("stats  LeagueGameLog 2026-27", lambda: gamelog("2026-27")),
    probe("stats  LeagueGameLog 2025-26", lambda: gamelog("2025-26")),
    probe("stats  ScoreboardV3", lambda: scoreboard_v3("2026-10-22")),
    probe("cdn    live ScoreBoard", live_games),
    probe("sched ScheduleLeagueV2 2026-27", lambda: schedule("2026-27")),
    probe("cdn   live BoxScore", live_boxscore_first),
    probe("sched ScheduleLeagueV2 2026-27", lambda: schedule("2026-27")),
    probe("cdn   live BoxScore", live_boxscore_first),
]

sys.exit(0 if all(results) else 1)