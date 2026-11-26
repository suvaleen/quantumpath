"""Local CSV/JSON learner feedback storage (no database)."""
import csv
import json
from datetime import datetime, timezone
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
FEEDBACK_CSV = DATA_DIR / "feedback.csv"
FIELDS = ["timestamp", "language", "role", "score", "total", "rating", "comment"]


def save_feedback(summary: dict, rating: int, comment: str, path: Path = FEEDBACK_CSV) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    is_new = not path.exists()
    with path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        if is_new:
            writer.writeheader()
        writer.writerow(
            {
                "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "language": summary["language"],
                "role": summary["role"],
                "score": summary["score"],
                "total": summary["total"],
                "rating": rating,
                "comment": comment.strip(),
            }
        )


def summary_json(summary: dict) -> str:
    return json.dumps(summary, ensure_ascii=False, indent=2)
