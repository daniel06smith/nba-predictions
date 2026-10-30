"""Backfill: pull LeagueGameLog for several seasons from stats.nba.com and
store the raw JSON responses in Azure Blob Storage (container: raw).

Runs from a laptop only: stats.nba.com blocks GitHub-hosted runners.
Auth: uses your `az login` session via DefaultAzureCredential (no keys).
"""
import time
from datetime import datetime, timezone

from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
from nba_api.stats.endpoints import leaguegamelog

ACCOUNT_URL = "https://stnbapred060725.blob.core.windows.net"
CONTAINER = "raw"
SEASONS = ["2021-22", "2022-23", "2023-24", "2024-25", "2025-26", "2026-27"]
RETRIES = 3


def fetch_season(season):
    for attempt in range(1, RETRIES + 1):
        try:
            return leaguegamelog.LeagueGameLog(season=season, timeout=60).get_json()
        except Exception as exc:
            print(f"  attempt {attempt} failed: {type(exc).__name__}: {exc}")
            if attempt == RETRIES:
                raise  # fail loudly, don't write partial data
            time.sleep(5 * attempt)


def main():
    client = BlobServiceClient(ACCOUNT_URL, credential=DefaultAzureCredential())
    container = client.get_container_client(CONTAINER)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    for season in SEASONS:
        print(f"{season}: fetching...")
        body = fetch_season(season)
        blob_name = f"league_game_log/season={season}/pulled={stamp}.json"
        container.upload_blob(blob_name, body, overwrite=False)
        print(f"  uploaded {blob_name} ({len(body):,} characters)")
        time.sleep(2)  # be polite to the API


if __name__ == "__main__":
    main()