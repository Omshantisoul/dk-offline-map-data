# DK Offline Map - Developer Test Data

This public repository contains reviewed developer-test map packages and companion offline-search indexes for DK Offline Map. It is not a production India or world catalog.

## Live Phase 6 map assets

The three accepted PMTiles packages are published in the GitHub Release tagged `phase6-test-maps-v1`. Their verified URLs, byte sizes and SHA-256 values are recorded in `catalog/catalog.json` and `documentation/PACKAGE-MANIFEST.md`.

## Phase 7 search indexes

Phase 7 adds separate, versioned, read-only SQLite search indexes for the Florence and Bengaluru Central developer-test maps. The indexes are derived from pinned Geofabrik OpenStreetMap extracts and use ordinary SQLite B-tree token indexes; FTS5 is not a runtime requirement.

Search-index binaries are distributed only as assets of the GitHub Release tagged `phase7-search-indexes-v1`. The Florence and Bengaluru Central assets were independently verified by full-file SHA-256 comparison and HTTP Range tests on 2026-07-17. Their canonical URLs, sizes and hashes are recorded in `catalog/catalog.json`.

## Layout

- `catalog/` - machine-readable catalog and schema
- `licenses/` - attribution and licensing notices
- `documentation/` - source, generation, validation, manifest, Range-test, and release records
- `tools/search-index/` - pinned, reproducible search-index generator and validators

Every package is marked `productionReady: false`. There is no whole-India or whole-world download.
