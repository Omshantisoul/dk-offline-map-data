# DK Offline Map - Developer Test Data

This public repository contains the reviewed Phase 6 developer-test catalog, schema, licensing notices, and reproducible package documentation for DK Offline Map.

It is not a production India or world map catalog. It contains only small test areas used to validate offline package management.

PMTiles binaries are distributed only as assets of the GitHub Release tagged `phase6-test-maps-v1`; they are not committed to Git history. Until that release is uploaded and independently verified, `catalog/catalog.json` intentionally contains `null` download URLs and `hostingStatus: "pending_release_upload"`.

## Layout

- `catalog/catalog.json` - reviewed catalog data
- `catalog/schema-v1.json` - machine-readable schema
- `licenses/` - attribution and licensing notices
- `documentation/` - generation, validation, manifest, Range-test, and release records

Every package is marked `productionReady: false`. There is no whole-India or whole-world download.
