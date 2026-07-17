# Search-index SQLite schema v1

Each map has a separate read-only SQLite companion database.

- `PRAGMA application_id = 0x444B5331` (`DKS1`)
- `PRAGMA user_version = 1`
- foreign keys are enabled during generation and validation
- FTS5 is not used or required

Tables:

- `metadata`: source, package, bounds, schema and generator identity
- `category`: stable searchable feature categories
- `admin_area`: optional locality hierarchy
- `place`: one searchable OSM node or way
- `place_name`: primary, localized, official and alternate names
- `search_token`: normalized full tokens, indexed with ordinary SQLite B-trees

Prefix lookup uses a half-open lexical range:

```sql
SELECT place_id
FROM search_token
WHERE token >= :prefix
  AND token < :prefixUpperBound
GROUP BY place_id
LIMIT :candidateLimit;
```

There is no leading-wildcard scan. Multi-token queries intersect bounded candidate sets.

Normalization uses NFKC, Unicode case folding, Latin-only accent folding, punctuation-to-space conversion and whitespace collapse. Devanagari, Kannada and other non-Latin combining marks are preserved. Original display names are never replaced by normalized values.
