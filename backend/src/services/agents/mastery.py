"""Mastery calculation utilities.

Implements the 40/30/20/10 mastery formula with proportional weight
redistribution for missing components.
"""

from typing import Any

MASTERY_LEVELS = {
    "Beginner": (0, 40),
    "Learning": (41, 70),
    "Proficient": (71, 90),
    "Mastered": (91, 100),
}

COMPONENT_WEIGHTS = {
    "exercises": 40,
    "quizzes": 30,
    "code_quality": 20,
    "streak": 10,
}


def calculate_mastery_score(
    components: dict[str, float],
) -> tuple[float, dict[str, Any]]:
    """Calculate mastery score using the 40/30/20/10 formula.

    When components are missing, redistribute weights proportionally.

    Args:
        components: Dict with keys exercises, quizzes, code_quality, streak

    Returns:
        Tuple of (overall_score, component_breakdown)
    """
    weights = dict(COMPONENT_WEIGHTS)
    missing = [k for k in weights if k not in components or components[k] is None]

    if len(missing) == len(weights):
        return 0.0, {
            "exercises": 0.0,
            "quizzes": 0.0,
            "code_quality": 0.0,
            "streak": 0.0,
            "missing_components": list(weights.keys()),
        }

    available_weight = sum(weights[k] for k in weights if k not in missing)
    score = 0.0
    breakdown = {}

    for key, weight in weights.items():
        if key in missing:
            breakdown[key] = 0.0
        else:
            redistributed_weight = (weight / available_weight) * 100
            score += (components[key] / 100) * redistributed_weight
            breakdown[key] = components[key]

    breakdown["missing_components"] = missing
    return round(score, 2), breakdown


def map_score_to_level(score: float) -> str:
    """Map a mastery score to a level name.

    Args:
        score: Score between 0 and 100

    Returns:
        Level name: Beginner, Learning, Proficient, or Mastered
    """
    for level, (low, high) in MASTERY_LEVELS.items():
        if low <= score <= high:
            return level
    return "Beginner"
