"""Expertise level from the quiz score."""

# (minimum share of all quiz questions answered correctly, level key), highest first.
THRESHOLDS = ((0.80, "advanced"), (0.50, "intermediate"), (0.0, "beginner"))


def expertise_level(correct: int, answered: int, total: int) -> str:
    """Return 'not_assessed', 'beginner', 'intermediate' or 'advanced'.

    Unanswered questions count as not correct, so the level can only rise as more
    questions are answered correctly.
    """
    if answered == 0 or total == 0:
        return "not_assessed"
    share = correct / total
    return next(level for minimum, level in THRESHOLDS if share >= minimum)
