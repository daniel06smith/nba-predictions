"""Time-ordered Elo tuning, with every trial tracked in MLflow.

Protocol (no leakage):
  warm-up   2021-22 .. 2023-24   ratings learn from these
  validate  2024-25              parameters are chosen here
  test      2025-26              scored ONCE, for the best parameters only
"""
import itertools

import mlflow

from nba_predictions.data import load_games
from nba_predictions.elo import predict_games
from nba_predictions.metrics import accuracy, brier_score, log_loss

SEASONS = ["2021-22", "2022-23", "2023-24", "2024-25", "2025-26"]
VALIDATION, TEST = "24", "25"  # two-digit season start years

GRID = {
    "k": [10, 15, 20, 25, 30],
    "home_advantage": [30, 50, 70, 100],
    "carryover": [0.6, 0.75, 0.9],
}


def score(predictions, season):
    rows = [(g, p) for g, p in predictions if g.season == season]
    y = [1.0 if g.home_won else 0.0 for g, _ in rows]
    p = [prob for _, prob in rows]
    return {
        "log_loss": log_loss(y, p),
        "brier": brier_score(y, p),
        "accuracy": accuracy(y, p),
    }


def main():
    mlflow.set_tracking_uri("sqlite:///mlflow.db")
    mlflow.set_experiment("nba-elo-tuning")

    all_games = load_games(seasons=SEASONS)
    dev_games = [g for g in all_games if g.season != TEST]  # test season stays untouched

    with mlflow.start_run(run_name="elo-sweep"):  # one parent run per execution
        best = None
        combos = itertools.product(GRID["k"], GRID["home_advantage"], GRID["carryover"])
        for k, home_advantage, carryover in combos:
            params = {"k": k, "home_advantage": home_advantage, "carryover": carryover}
            val = score(predict_games(dev_games, **params), VALIDATION)
            run_name = f"k{k}_ha{home_advantage}_co{carryover}"
            with mlflow.start_run(run_name=run_name, nested=True):
                mlflow.log_params(params)
                mlflow.log_metrics({f"val_{name}": v for name, v in val.items()})
            if best is None or val["log_loss"] < best[1]["log_loss"]:
                best = (params, val)

        best_params, best_val = best
        tuned_test = score(predict_games(all_games, **best_params), TEST)
        default_test = score(predict_games(all_games), TEST)  # the untuned defaults

        # Summary on the parent run: best settings, validation, and the one-time test.
        mlflow.log_params({f"best_{n}": v for n, v in best_params.items()})
        mlflow.log_metrics({f"val_{n}": v for n, v in best_val.items()})
        mlflow.log_metrics({f"test_{n}": v for n, v in tuned_test.items()})
        mlflow.log_metrics({f"default_test_{n}": v for n, v in default_test.items()})

    print(f"best parameters (chosen on validation): {best_params}")
    print(f"validation log loss: {best_val['log_loss']:.4f}")
    print(f"test log loss, defaults: {default_test['log_loss']:.4f}")
    print(f"test log loss, tuned:    {tuned_test['log_loss']:.4f}")


if __name__ == "__main__":
    main()