# Phase 7 search-index validation

For every generated SQLite asset:

```powershell
python tools\search-index\validate_search_index.py out\florence-test-search-v1.sqlite --report reports\florence-validation.json
python tools\search-index\golden_queries.py --database out\florence-test-search-v1.sqlite --fixture tests\florence-golden-queries.json --report reports\florence-golden.json
python tools\search-index\validate_search_index.py out\bengaluru-central-test-search-v1.sqlite --report reports\bengaluru-validation.json
python tools\search-index\golden_queries.py --database out\bengaluru-central-test-search-v1.sqlite --fixture tests\bengaluru-golden-queries.json --report reports\bengaluru-golden.json
python -m unittest discover -s tools\search-index -p "test_*.py" -v
```

Required checks:

- `PRAGMA integrity_check` equals `ok`
- `PRAGMA quick_check` equals `ok`
- `PRAGMA foreign_key_check` returns zero rows
- application ID equals `0x444B5331`
- user/schema version equals `1`
- required tables and indexes exist
- every place coordinate is within package bounds
- the database opens with SQLite URI `mode=ro`
- index is non-empty
- normalization tests pass for Latin, accented Latin, Devanagari and Kannada
- golden prefix and multi-token queries return expected real OSM features
- final byte size and SHA-256 are recorded after all validation

Uploaded Release assets must be downloaded again and compared byte-for-byte by size and SHA-256. HTTP Range support is tested separately; safe full-file download remains the required fallback.

Final local result: both databases are valid, both six-query golden suites pass with zero failures, and all six normalization/schema unit tests pass.
