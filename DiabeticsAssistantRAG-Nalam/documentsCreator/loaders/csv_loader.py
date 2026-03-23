from pathlib import Path
from typing import Dict, List
import csv


def load_csv_rows(path: Path) -> List[Dict[str, str]]:
    """
    Load a CSV file and return a list of row dictionaries.

    This keeps the standard JSON module independent of any external
    frameworks by using only the standard library.
    """
    rows: List[Dict[str, str]] = []

    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)

        for row in reader:
            rows.append(dict(row))

    return rows

