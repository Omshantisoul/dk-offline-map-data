from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from pathlib import Path

from search_common import normalize_search_text, prefix_upper_bound, tokenize


def candidate_ids(connection: sqlite3.Connection, query: str, limit: int = 2000) -> set[int]:
    token_sets: list[set[int]] = []
    for token in tokenize(query):
        upper = prefix_upper_bound(token)
        rows = connection.execute("SELECT place_id FROM search_token WHERE token >= ? AND token < ? GROUP BY place_id LIMIT ?", (token, upper, limit))
        token_sets.append({row[0] for row in rows})
    return set.intersection(*token_sets) if token_sets else set()


def run(database: Path, fixture: Path) -> dict:
    connection = sqlite3.connect(f"{database.resolve().as_uri()}?mode=ro", uri=True)
    tests = json.loads(fixture.read_text(encoding="utf-8"))["queries"]
    results = []
    failures = []
    for test in tests:
        ids = candidate_ids(connection, test["query"])
        rows = connection.execute(f"SELECT place_id,primary_name,category_id FROM place WHERE place_id IN ({','.join('?' for _ in ids)})", tuple(ids)).fetchall() if ids else []
        names = [row[1] for row in rows]
        normalized_names = [normalize_search_text(name) for name in names]
        required = [normalize_search_text(name) for name in test.get("expectedAnyName", [])]
        category = test.get("expectedCategory")
        passed = bool(rows) and (not required or any(expected in normalized_names for expected in required)) and (not category or any(row[2] == category for row in rows))
        record = {"query": test["query"], "candidateCount": len(rows), "sampleNames": sorted(names)[:10], "passed": passed}
        results.append(record)
        if not passed: failures.append(record)
    connection.close()
    return {"database": str(database.resolve()), "fixture": str(fixture.resolve()), "tests": results, "failureCount": len(failures), "passed": not failures}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--database", type=Path, required=True)
    parser.add_argument("--fixture", type=Path, required=True)
    parser.add_argument("--report", type=Path)
    arguments = parser.parse_args()
    result = run(arguments.database, arguments.fixture)
    rendered = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    print(rendered, end="")
    if arguments.report: arguments.report.write_text(rendered, encoding="utf-8")
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
