from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path

from search_common import APPLICATION_ID, SCHEMA_VERSION


class SchemaTests(unittest.TestCase):
    def test_schema_identifiers_and_tables(self):
        schema = (Path(__file__).resolve().parent / "schema-v1.sql").read_text(encoding="utf-8")
        with tempfile.TemporaryDirectory() as directory:
            connection = sqlite3.connect(Path(directory) / "schema.sqlite")
            connection.executescript(schema)
            self.assertEqual(APPLICATION_ID, connection.execute("PRAGMA application_id").fetchone()[0])
            self.assertEqual(SCHEMA_VERSION, connection.execute("PRAGMA user_version").fetchone()[0])
            tables = {row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            self.assertTrue({"metadata", "admin_area", "category", "place", "place_name", "search_token"}.issubset(tables))
            connection.close()


if __name__ == "__main__":
    unittest.main()
