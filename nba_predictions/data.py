"""Parse raw LeagueGameLog JSON into one Game record per game."""
import json
from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class Game:
    game_id: str
    date: str  # "YYYY-MM-DD"
    home_team: str  # team abbreviation, e.g. "LAL"
    away_team: str
    home_pts: int
    away_pts: int
    neutral_site: bool = False

    @property
    def home_won(self) -> bool:
        return self.home_pts > self.away_pts

    @property
    def season(self) -> str:
        """Two-digit season start year from the game id, e.g. '25' for 2025-26."""
        return self.game_id[3:5]


def parse_game_log(raw_json: str) -> list[Game]:
    """Turn the API's one-row-per-team format into one row per game.

    Fails loudly on anything unexpected rather than guessing.
    """
    result_set = json.loads(raw_json)["resultSets"][0]
    headers = result_set["headers"]
    rows = [dict(zip(headers, row)) for row in result_set["rowSet"]]

    by_game = {}
    for row in rows:
        if not row["GAME_ID"].startswith("002"):
            raise ValueError(f"non-regular-season game id: {row['GAME_ID']}")
        by_game.setdefault(row["GAME_ID"], []).append(row)

    games = []
    for game_id, team_rows in by_game.items():
        homes = [r for r in team_rows if " vs. " in r["MATCHUP"]]
        aways = [r for r in team_rows if " @ " in r["MATCHUP"]]
        if len(team_rows) == 2 and len(homes) == 1 and len(aways) == 1:
            home, away = homes[0], aways[0]
            neutral = False
        elif len(team_rows) == 2 and len(homes) == 0 and len(aways) == 2:
            # Neutral-site game: the API marks BOTH rows "@". Neither team is
            # really "home", so fill the slots alphabetically for determinism.
            home, away = sorted(team_rows, key=lambda r: r["TEAM_ABBREVIATION"])
            neutral = True
        else:
            raise ValueError(f"game {game_id}: unexpected home/away pattern")

        margin = home["PTS"] - away["PTS"]
        if home["PLUS_MINUS"] != margin or away["PLUS_MINUS"] != -margin:
            raise ValueError(f"game {game_id}: scores and plus-minus disagree")

        games.append(
            Game(
                game_id=game_id,
                date=home["GAME_DATE"],
                home_team=home["TEAM_ABBREVIATION"],
                away_team=away["TEAM_ABBREVIATION"],
                home_pts=home["PTS"],
                away_pts=away["PTS"],
                neutral_site=neutral,
            )
        )

    games.sort(key=lambda g: (g.date, g.game_id))  # chronological, for Elo later
    return games

def load_games(root="data/league_game_log", seasons=None) -> list[Game]:
    """Load the latest snapshot of each season folder under `root`."""
    games = []
    for season_dir in sorted(Path(root).glob("season=*")):
        if seasons is not None and season_dir.name.removeprefix("season=") not in seasons:
            continue
        latest = sorted(season_dir.glob("pulled=*.json"))[-1]
        games.extend(parse_game_log(latest.read_text(encoding="utf-8")))
    games.sort(key=lambda g: (g.date, g.game_id))
    return games