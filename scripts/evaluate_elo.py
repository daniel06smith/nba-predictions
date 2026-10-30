from nba_predictions.data import load_games
from nba_predictions.elo import predict_games
from nba_predictions.metrics import accuracy, brier_score, log_loss

SEASONS = ["2021-22", "2022-23", "2023-24", "2024-25", "2025-26"]
TEST_SEASON = "25"  # 2025-26

games = load_games(seasons=SEASONS)
predictions = predict_games(games)

train = [g for g in games if g.season != TEST_SEASON]
test = [(g, p) for g, p in predictions if g.season == TEST_SEASON]
y = [1.0 if g.home_won else 0.0 for g, _ in test]

home_rate = sum(g.home_won for g in train) / len(train)
models = {
    "coin flip": [0.5] * len(y),
    "home-win rate": [home_rate] * len(y),
    "Elo": [p for _, p in test],
}
print(f"{len(games)} games loaded, {len(test)} in the test season")
for name, probs in models.items():
    print(f"{name:14} log loss {log_loss(y, probs):.4f}  "
          f"Brier {brier_score(y, probs):.4f}  accuracy {accuracy(y, probs):.3f}")