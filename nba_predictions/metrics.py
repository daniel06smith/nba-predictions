import math

def log_loss(outcomes, probs, eps=1e-15):
    total = 0.0
    for y, p in zip(outcomes, probs):
        p = min(max(p, eps), 1 - eps)
        total += -(y * math.log(p) + (1 - y) * math.log(1 - p))
    return total / len(outcomes)


def brier_score(outcomes, probs):
    return sum((p - y) ** 2 for y, p in zip(outcomes, probs)) / len(outcomes)


def accuracy(outcomes, probs):
    return sum((p > 0.5) == bool(y) for y, p in zip(outcomes, probs)) / len(outcomes)