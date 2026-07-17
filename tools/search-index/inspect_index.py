from __future__ import annotations

import argparse
import json
import sqlite3
import unicodedata
from pathlib import Path


def has_non_latin(value: str) -> bool:
    return any(char.isalpha() and "LATIN" not in unicodedata.name(char, "") for char in value)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("database", type=Path)
    arguments = parser.parse_args()
    connection = sqlite3.connect(f"{arguments.database.resolve().as_uri()}?mode=ro", uri=True)
    categories = {}
    for category_id, in connection.execute("SELECT DISTINCT category_id FROM place ORDER BY category_id"):
        categories[category_id] = [dict(zip(("name", "importance", "locality"), row)) for row in connection.execute("SELECT primary_name,importance,locality FROM place WHERE category_id=? ORDER BY importance DESC,primary_name LIMIT 12", (category_id,))]
    aliases = [dict(zip(("name", "language", "kind", "primaryName", "category"), row)) for row in connection.execute("SELECT n.name,n.language,n.name_kind,p.primary_name,p.category_id FROM place_name n JOIN place p ON p.place_id=n.place_id WHERE lower(n.name) LIKE '%bangalore%' OR lower(n.name) LIKE '%florence%' OR lower(n.name) LIKE '%firenze%' ORDER BY n.name LIMIT 100")]
    non_latin = []
    for row in connection.execute("SELECT n.name,n.language,n.name_kind,p.primary_name,p.category_id FROM place_name n JOIN place p ON p.place_id=n.place_id ORDER BY p.importance DESC,n.name"):
        if has_non_latin(row[0]):
            non_latin.append(dict(zip(("name", "language", "kind", "primaryName", "category"), row)))
            if len(non_latin) >= 100:
                break
    print(json.dumps({"database": str(arguments.database.resolve()), "categories": categories, "matchedAliases": aliases, "nonLatin": non_latin}, indent=2, ensure_ascii=False))
    connection.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
