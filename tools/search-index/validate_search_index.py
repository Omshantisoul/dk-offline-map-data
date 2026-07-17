from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from pathlib import Path

from search_common import APPLICATION_ID, SCHEMA_VERSION, sha256_file

REQUIRED_TABLES = {"metadata", "admin_area", "category", "place", "place_name", "search_token"}
REQUIRED_INDEXES = {"idx_search_token_token_place", "idx_place_category_importance", "idx_place_spatial", "idx_place_name_exact", "idx_place_name_owner"}


def validate(path: Path) -> dict:
    uri = f"{path.resolve().as_uri()}?mode=ro"
    connection = sqlite3.connect(uri, uri=True)
    errors: list[str] = []
    integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]
    quick = connection.execute("PRAGMA quick_check").fetchone()[0]
    foreign_keys = connection.execute("PRAGMA foreign_key_check").fetchall()
    application_id = connection.execute("PRAGMA application_id").fetchone()[0]
    user_version = connection.execute("PRAGMA user_version").fetchone()[0]
    tables = {row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    indexes = {row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='index'")}
    if integrity != "ok": errors.append(f"integrity_check={integrity}")
    if quick != "ok": errors.append(f"quick_check={quick}")
    if foreign_keys: errors.append(f"foreign_key_check returned {len(foreign_keys)} rows")
    if application_id != APPLICATION_ID: errors.append(f"application_id={application_id}")
    if user_version != SCHEMA_VERSION: errors.append(f"user_version={user_version}")
    if not REQUIRED_TABLES.issubset(tables): errors.append(f"missing tables={sorted(REQUIRED_TABLES - tables)}")
    if not REQUIRED_INDEXES.issubset(indexes): errors.append(f"missing indexes={sorted(REQUIRED_INDEXES - indexes)}")
    metadata = connection.execute("SELECT search_index_id,package_id,west,south,east,north,source_timestamp,source_sha256,generator_version FROM metadata WHERE id=1").fetchone()
    if metadata is None:
        errors.append("metadata row missing")
        bounds = None
    else:
        bounds = metadata[2:6]
        outside = connection.execute("SELECT COUNT(*) FROM place WHERE longitude < ? OR longitude > ? OR latitude < ? OR latitude > ?", (bounds[0], bounds[2], bounds[1], bounds[3])).fetchone()[0]
        if outside: errors.append(f"places outside bounds={outside}")
    counts = {
        "places": connection.execute("SELECT COUNT(*) FROM place").fetchone()[0],
        "names": connection.execute("SELECT COUNT(*) FROM place_name").fetchone()[0],
        "tokens": connection.execute("SELECT COUNT(*) FROM search_token").fetchone()[0],
        "categories": dict(connection.execute("SELECT category_id,COUNT(*) FROM place GROUP BY category_id ORDER BY category_id")),
    }
    if counts["places"] == 0 or counts["tokens"] == 0:
        errors.append("empty search index")
    connection.close()
    return {"path": str(path.resolve()), "bytes": path.stat().st_size, "sha256": sha256_file(path), "integrityCheck": integrity, "quickCheck": quick, "foreignKeyCheckRows": len(foreign_keys), "applicationId": application_id, "userVersion": user_version, "metadata": metadata, "bounds": bounds, **counts, "errors": errors, "valid": not errors}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("database", type=Path)
    parser.add_argument("--report", type=Path)
    arguments = parser.parse_args()
    result = validate(arguments.database)
    rendered = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    print(rendered, end="")
    if arguments.report:
        arguments.report.write_text(rendered, encoding="utf-8")
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
