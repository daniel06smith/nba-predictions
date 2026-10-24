"""Probe: can this machine reach NBA stats?"""
import sys
import time

from nba_api.stats.endpoints import leaguegamelog

start = time.time()
try:
    games = leaguegamelog.LeagueGameLog(season="2026-27", timeout=30)
    df = games.get_data_frames()[0]
    print(f"OK: {len(df)} rows in {time.time() - start:.1f}s")
    print(df.columns.tolist())
    
except Exception as exc:  # fail loudly with the real cause
    print(f"FAIL after {time.time() - start:.1f}s: {type(exc).__name__}: {exc}")
    sys.exit(1)