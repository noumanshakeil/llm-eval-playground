from __future__ import annotations

def score_exact(expected: str, actual: str) -> float:
    return 1.0 if expected.strip() == actual.strip() else 0.0

def score_contains(expected: str, actual: str) -> float:
    return 1.0 if expected.lower() in actual.lower() else 0.0

def score_length(expected: str, actual: str) -> float:
    try:
        target = int(expected.strip())
    except ValueError:
        return 0.0
    diff = abs(len(actual.strip()) - target)
    return max(0.0, 1.0 - diff / max(target, 1))

REGISTRY = {
    "exact": score_exact,
    "contains": score_contains,
    "length": score_length,
}

def run_scorer(name: str, expected: str, actual: str) -> float:
    fn = REGISTRY.get(name, score_contains)
    return fn(expected, actual)
