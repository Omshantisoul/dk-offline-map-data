from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path

from golden_queries import candidate_ids
from search_common import normalize_search_text, tokenize


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect search-index candidates for a query.")
    parser.add_argument("--database", type=Path, required=True)
    parser.add_argument("--query", required=True)
    parser.add_argument("--limit", type=int, default=20)
    arguments = parser.parse_args()
    connection = sqlite3.connect(f"{arguments.database.resolve().as_uri()}?mode=ro", uri=True)
    ids = candidate_ids(connection, arguments.query)
    rows = []
    if ids:
        placeholders = ",".join("?" for _ in ids)
        for row in connection.execute(
            f"""
            SELECT p.primary_name, p.category_id, p.latitude, p.longitude,
                   GROUP_CONCAT(pn.name, ' | ')
            FROM place p
            JOIN place_name pn ON pn.place_id = p.place_id
            WHERE p.place_id IN ({placeholders})
            GROUP BY p.place_id
            ORDER BY p.importance DESC, p.primary_name COLLATE NOCASE
            LIMIT ?
            """,
            (*ids, arguments.limit),
        ):
            rows.append({"primaryName": row[0], "category": row[1], "latitude": row[2], "longitude": row[3], "names": row[4].split(" | ")})
    metadata = dict(connection.execute("SELECT 'created_at', created_at FROM metadata UNION ALL SELECT 'attribution', attribution FROM metadata"))
    connection.close()
    print(json.dumps({"query": arguments.query, "normalized": normalize_search_text(arguments.query), "tokens": tokenize(arguments.query), "candidateCount": len(ids), "results": rows, "metadata": metadata}, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
